"""run_v3.py - extended evaluation for the matched re-evaluation (all reviewer requests).

New relative to run_revision.py
  * Models: Linear, STGCN, Graph WaveNet added to LSTM / AC-LSTM / DCRNN / DyGCN-AC-LSTM /
    fixed-graph ablation; optional separately tuned fixed-graph model (--tune-static).
  * Any target x decoder cell: --target smoothed|raw  x  (--residual or not).
  * Rolling origins: --start-step / --max-steps (fixed, pre-declared blocks).
  * Tuning robustness: --tune-seeds 0 1 2 (selection by mean validation RMSE; per-seed
    winners recorded), --grid small|large.
  * Compute: parameters, training seconds per seed, peak GPU memory, inference ms/window.
  * Common-scale metrics: every forecast is also scored against the UNSMOOTHED z series
    (RMSE, MAE, MASE, per-horizon), so all target/decoder cells are comparable.
  * Operational metrics (--rm routing matrix): flow/link-load WAPE, bottleneck-load error,
    under-provisioning rate at 0/10/20% headroom, all on actual traffic volumes.
  * Predictions saved per model x seed -> resumable; bootstrap at block lengths 1/3/5/10.
"""
import argparse, json, os, time
import numpy as np, torch
from src.abilene import load_abilene
from src.preprocessing import preprocess, zscore_apply
from src.datasets import make_windows
from src.adjacency import build_adjacency
from src.train import precompute_adjacency, run_epoch
from src.metrics import all_metrics
from src.dygcn_ac_lstm import DyGCNACLSTM
from src.dcrnn import DCRNN
from src.baselines import LSTMBaseline, ACLSTMBaseline
from src.extra_models import LinearForecaster, STGCN, GraphWaveNet
from src.residual import Residual
from src.evaluation import (window_mse, persistence, seasonal_naive, paired_seed_tests,
                            block_bootstrap_diff)
from src.operational import to_volume, load_routing, operational_metrics, scale_metrics

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SEQ = HOR = 12
W, K, P, G = 48, 6, 4, 4

GRIDS = {"small": {"LSTM": [(32, 0), (64, 0)], "AC-LSTM": [(32, 0), (64, 0)], "Linear": [(0, 0)],
                   "DCRNN": [(h, k) for h in (32, 64) for k in (2, 3)],
                   "STGCN": [(h, k) for h in (32, 64) for k in (2, 3)],
                   "GWN": [(h, k) for h in (16, 32) for k in (1, 2)],
                   "DyGCN-AC-LSTM": [(h, k) for h in (32, 64) for k in (2, 3)]},
         "large": {"LSTM": [(h, 0) for h in (32, 64, 128)], "AC-LSTM": [(h, 0) for h in (32, 64, 128)],
                   "Linear": [(0, 0)],
                   "DCRNN": [(h, k) for h in (32, 64, 128) for k in (1, 2, 3)],
                   "STGCN": [(h, k) for h in (32, 64, 128) for k in (1, 2, 3)],
                   "GWN": [(h, k) for h in (16, 32, 64) for k in (1, 2, 3)],
                   "DyGCN-AC-LSTM": [(h, k) for h in (32, 64, 128) for k in (1, 2, 3)]}}
IS_GRAPH = {"LSTM": False, "AC-LSTM": False, "Linear": False, "DCRNN": True, "STGCN": True,
            "GWN": True, "DyGCN-AC-LSTM": True, "DyGCN-static": True, "DyGCN-static-tuned": True}
USES_STATIC = {"DCRNN", "STGCN", "GWN", "DyGCN-static", "DyGCN-static-tuned"}
ALL_MODELS = ["Linear", "LSTM", "AC-LSTM", "DCRNN", "STGCN", "GWN", "DyGCN-AC-LSTM", "DyGCN-static"]


def make(name, F, h, k, residual):
    m = {"LSTM": lambda: LSTMBaseline(F, h, HOR), "AC-LSTM": lambda: ACLSTMBaseline(F, h, G, HOR),
         "Linear": lambda: LinearForecaster(SEQ, HOR),
         "DCRNN": lambda: DCRNN(hidden=h, K=k, layers=2, horizon=HOR),
         "STGCN": lambda: STGCN(F, hidden=h, K=k, L=SEQ, H=HOR),
         "GWN": lambda: GraphWaveNet(F, hidden=h, order=k, L=SEQ, H=HOR),
         "DyGCN-AC-LSTM": lambda: DyGCNACLSTM(h, G, k, HOR),
         "DyGCN-static": lambda: DyGCNACLSTM(h, G, k, HOR),
         "DyGCN-static-tuned": lambda: DyGCNACLSTM(h, G, k, HOR)}[name]()
    return Residual(m) if residual else m


def prepare(a):
    TM, meta = load_abilene(a.path, drop_node=a.drop_node, sample_min=a.sample_min,
                            min_active_frac=a.min_active_frac, log_transform=True)
    TM = TM[a.start_step:]
    if a.max_steps: TM = TM[:a.max_steps]
    T = len(TM); tr, va = int(0.65 * T), int(0.80 * T)
    den, info = preprocess(TM, tr, c=4, alpha0=0.3, steps_per_day=meta["steps_per_day"],
                           smooth=(a.target == "smoothed"))
    z = zscore_apply(TM, info["mu"], info["sigma"])               # unsmoothed common scale
    static = build_adjacency(den[:W], K)
    sets, zsets = {}, {}
    for k_, (lo, hi) in {"train": (0, tr), "val": (tr, va), "test": (va, T)}.items():
        X, Y, idx = make_windows(den[lo:hi], SEQ, HOR); sets[k_] = (X, Y, idx + lo)
        _, Yz, _ = make_windows(z[lo:hi], SEQ, HOR); zsets[k_] = Yz
    need = [o - SEQ + t for _, _, O in sets.values() for o in O for t in range(SEQ)]
    amap = precompute_adjacency(den, need, W, K, P, static=static)
    R = load_routing(a.rm, meta["N_orig"], meta["flow_pairs_orig"]) if a.rm else None
    return dict(den=den, z=z, tr=tr, meta=meta, info=info, sets=sets, zsets=zsets, amap=amap,
                sadj=torch.tensor(static, dtype=torch.float32), R=R)


def fit(model, D, name, epochs):
    model = model.to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs, eta_min=1e-5)
    X, Y, O = D["sets"]["train"]; st = D["sadj"] if name in USES_STATIC else None
    for _ in range(epochs):
        run_epoch(model, X, Y, O, D["amap"], opt=opt, tf=0.5, is_graph=IS_GRAPH[name],
                  device=DEVICE, static_adj=st); sch.step()
    return model


def predict(model, D, split, name):
    X, Y, O = D["sets"][split]; st = D["sadj"] if name in USES_STATIC else None
    _, Pm = run_epoch(model, X, Y, O, D["amap"], opt=None, is_graph=IS_GRAPH[name],
                      device=DEVICE, static_adj=st)
    return Pm


def evaluate_forecast(D, Pm):
    """Own-target RMSE + common-scale + operational metrics for one forecast."""
    Yte = D["sets"]["test"][1]; Yz = D["zsets"]["test"]
    out = {"rmse_own": all_metrics(Yte, Pm)["RMSE"]}
    out.update(scale_metrics(Yz, Pm, D["z"][:D["tr"]]))
    mu, sd = D["info"]["mu"], D["info"]["sigma"]
    out.update(operational_metrics(to_volume(Yz, mu, sd), to_volume(Pm, mu, sd), D["R"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True); ap.add_argument("--rm", default=None)
    ap.add_argument("--drop-node", type=int, default=None)
    ap.add_argument("--sample-min", type=int, default=5)
    ap.add_argument("--min-active-frac", type=float, default=0.5)
    ap.add_argument("--start-step", type=int, default=0); ap.add_argument("--max-steps", type=int, default=None)
    ap.add_argument("--target", choices=["smoothed", "raw"], default="smoothed")
    ap.add_argument("--residual", action="store_true")
    ap.add_argument("--models", nargs="+", default=ALL_MODELS)
    ap.add_argument("--tune-static", action="store_true", help="also tune the fixed-graph model separately")
    ap.add_argument("--grid", choices=["small", "large"], default="small")
    ap.add_argument("--tune-seeds", type=int, nargs="+", default=[0])
    ap.add_argument("--fixed", nargs="+", default=None, help="skip tuning, e.g. DCRNN=64,3 STGCN=64,2")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 456, 789, 1024])
    ap.add_argument("--outdir", default="results"); ap.add_argument("--tag", default=None)
    a = ap.parse_args()
    models = list(a.models) + (["DyGCN-static-tuned"] if a.tune_static else [])
    base = os.path.splitext(os.path.basename(a.path))[0]
    tag = a.tag or (f"{base}_{a.target}_{'resid' if a.residual else 'abs'}"
                    + (f"_start{a.start_step}" if a.start_step else "") + "_v3")
    os.makedirs(a.outdir, exist_ok=True)
    pred_dir = os.path.join(a.outdir, f"{tag}_preds"); os.makedirs(pred_dir, exist_ok=True)
    json_path = os.path.join(a.outdir, f"{tag}.json")
    print(f"device: {DEVICE} | run: {tag} | models: {models}", flush=True)
    if os.path.exists(json_path):
        try:
            prev = json.load(open(json_path))
            if prev.get("paired_seed_tests") is not None and "block_bootstrap_own" in prev:
                print(f"ALREADY COMPLETE: {json_path} - nothing to do. Delete that file to force a rerun.")
                return
        except Exception:
            pass

    D = prepare(a); F = D["den"].shape[1]
    Xte, Yte, Ote = D["sets"]["test"]
    print(f"F={F} | windows train/val/test = {len(D['sets']['train'][0])}/{len(D['sets']['val'][0])}/{len(Xte)}"
          f" | routing links: {D['R'].shape[1] if D['R'] is not None else 'none'}", flush=True)
    out = {"tag": tag, "args": vars(a), "F": F, "tuning": {}, "test": {}, "compute": {}}

    # ---- naive forecasts (own space) + persistence of the raw series ----
    naive = {"Persistence": persistence(Xte, HOR),
             "Seasonal-naive": seasonal_naive(D["den"], Ote, HOR, D["meta"]["steps_per_day"]),
             "Training-mean": np.zeros_like(Yte)}
    if a.target == "smoothed":
        naive["Persistence-raw-input"] = np.stack([np.repeat(D["z"][o - 1][None, :], HOR, 0) for o in Ote])
    wmse_own, wmse_z = {}, {}
    for n, Pn in naive.items():
        out["test"][n] = evaluate_forecast(D, Pn)
        wmse_own[n] = window_mse(Yte, Pn); wmse_z[n] = window_mse(D["zsets"]["test"], Pn)
        print(f"  {n:22s} own RMSE {out['test'][n]['rmse_own']:.4f} | raw-z RMSE {out['test'][n]['rmse_rawz']:.4f}"
              + (f" | link WAPE {out['test'][n]['link_wape']:.3f}" if D["R"] is not None else ""), flush=True)

    # ---- selection (multi-seed, recorded) ----
    chosen = {}
    fixed = dict(x.split("=") for x in a.fixed) if a.fixed else {}
    for name in [m for m in models if m != "DyGCN-static"]:
        gname = "DyGCN-AC-LSTM" if name == "DyGCN-static-tuned" else name
        if name in fixed:
            p_ = [int(v) for v in fixed[name].split(",")]; chosen[name] = (p_[0], p_[1] if len(p_) > 1 else 0)
            out["tuning"][name] = {"selected": chosen[name], "note": "fixed via --fixed"}; continue
        res = []
        for (h, k) in GRIDS[a.grid][gname]:
            vals = []
            for ts in a.tune_seeds:
                torch.manual_seed(ts); np.random.seed(ts)
                m = fit(make(name, F, h, k, a.residual), D, name, a.epochs)
                vals.append(all_metrics(D["sets"]["val"][1], predict(m, D, "val", name))["RMSE"])
            res.append({"hidden": h, "hops": k, "val_rmse_per_tune_seed": vals, "val_rmse_mean": float(np.mean(vals))})
            print(f"  [tune {name}] ({h},{k}) val {np.mean(vals):.4f} " + str(np.round(vals, 4)), flush=True)
        best = min(res, key=lambda r: r["val_rmse_mean"]); chosen[name] = (best["hidden"], best["hops"])
        winners = [min(res, key=lambda r: r["val_rmse_per_tune_seed"][i]) for i in range(len(a.tune_seeds))]
        out["tuning"][name] = {"grid": res, "selected": chosen[name],
                               "winner_per_tune_seed": [(w["hidden"], w["hops"]) for w in winners]}
        json.dump(out, open(json_path, "w"), indent=1)
    if "DyGCN-static" in models:
        chosen["DyGCN-static"] = chosen["DyGCN-AC-LSTM"]
        out["tuning"]["DyGCN-static"] = {"selected": chosen["DyGCN-static"], "note": "inherits DyGCN-AC-LSTM (controlled ablation)"}
    print("selected:", chosen, flush=True)

    # ---- seeds (resumable) ----
    per_seed = {n: [] for n in chosen}; preds = {n: [] for n in chosen}; metr = {n: [] for n in chosen}
    for seed in a.seeds:
        for name, (h, k) in chosen.items():
            fpath = os.path.join(pred_dir, f"{name}_seed{seed}.npy")
            if os.path.exists(fpath):
                Pm = np.load(fpath); note = "loaded"
            else:
                torch.manual_seed(seed); np.random.seed(seed)
                if DEVICE == "cuda": torch.cuda.reset_peak_memory_stats()
                t0 = time.time(); m = fit(make(name, F, h, k, a.residual), D, name, a.epochs); t_fit = time.time() - t0
                t1 = time.time(); Pm = predict(m, D, "test", name); t_inf = (time.time() - t1) / len(Xte) * 1e3
                np.save(fpath, Pm.astype(np.float32))
                comp = out["compute"].setdefault(name, {"params": int(sum(p.numel() for p in m.parameters())),
                                                        "train_s": [], "infer_ms_per_window": [], "peak_mem_mb": []})
                comp["train_s"].append(t_fit); comp["infer_ms_per_window"].append(t_inf)
                comp["peak_mem_mb"].append(torch.cuda.max_memory_allocated() / 2**20 if DEVICE == "cuda" else None)
                note = f"{t_fit:.0f}s"
            ev = evaluate_forecast(D, Pm); metr[name].append(ev)
            per_seed[name].append(ev["rmse_own"]); preds[name].append(Pm)
            print(f"seed {seed} {name:18s} own {ev['rmse_own']:.4f} raw-z {ev['rmse_rawz']:.4f}"
                  + (f" linkWAPE {ev['link_wape']:.3f}" if D["R"] is not None else "") + f"  ({note})", flush=True)
            json.dump({**out, "partial_per_seed": per_seed}, open(json_path, "w"), indent=1)

    keys = [k for k in metr[next(iter(metr))][0] if not k.startswith("horizon") and k != "n_links"]
    for name in chosen:
        v = np.array(per_seed[name])
        out["test"][name] = {"per_seed": v.tolist(), "mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                             "metrics_mean": {k: float(np.mean([e[k] for e in metr[name]])) for k in keys},
                             "metrics_sd": {k: float(np.std([e[k] for e in metr[name]], ddof=1)) if len(v) > 1 else 0.0 for k in keys},
                             "metrics_per_seed": {k: [e[k] for e in metr[name]] for k in keys},
                             "horizon_rmse_rawz": np.mean([e["horizon_rmse_rawz"] for e in metr[name]], 0).tolist()}
        wmse_own[name] = np.mean([window_mse(Yte, p) for p in preds[name]], 0)
        wmse_z[name] = np.mean([window_mse(D["zsets"]["test"], p) for p in preds[name]], 0)

    tgt = "DyGCN-AC-LSTM"
    pairs = [(tgt, b) for b in ["DCRNN", "STGCN", "GWN", "DyGCN-static", "DyGCN-static-tuned", "Linear", "AC-LSTM"]
             if b in chosen and tgt in chosen]
    out["paired_seed_tests"] = paired_seed_tests(per_seed, pairs) if len(a.seeds) > 1 else []
    learned = [n for n in chosen]
    bpairs = pairs + [(n, "Persistence") for n in learned]
    out["block_bootstrap_own"] = {f"{x}|{y}": {str(b): block_bootstrap_diff(wmse_own[x], wmse_own[y], block=b)
                                                for b in (1, 3, 5, 10)} for x, y in bpairs}
    out["block_bootstrap_rawz"] = {f"{x}|{y}": {str(b): block_bootstrap_diff(wmse_z[x], wmse_z[y], block=b)
                                                 for b in (1, 3, 5, 10)} for x, y in bpairs}
    out["window_mse_own"] = {k: np.asarray(v).tolist() for k, v in wmse_own.items()}
    out["window_mse_rawz"] = {k: np.asarray(v).tolist() for k, v in wmse_z.items()}
    json.dump(out, open(json_path, "w"), indent=1)

    print(f"\n=== {tag} ===")
    hdr = "model                  own RMSE          raw-z RMSE   MASE" + ("   linkWAPE  bottleneck  underprov@10%" if D["R"] is not None else "")
    print(hdr)
    for n in list(naive) + learned:
        e = out["test"][n]; mm = e.get("metrics_mean", e)
        own = f"{e['mean']:.4f}+/-{e['sd']:.4f}" if "mean" in e else f"{e['rmse_own']:.4f}         "
        line = f"{n:22s} {own:17s} {mm['rmse_rawz']:.4f}       {mm['mase']:.3f}"
        if D["R"] is not None:
            line += f"   {mm['link_wape']:.3f}     {mm['bottleneck_err']:.3f}       {mm['underprov_rate@10']:.3f}"
        print(line)
    print("\nPaired seed tests vs DyGCN-AC-LSTM (Holm):")
    for r in out["paired_seed_tests"]:
        print(f"  {r['a']} - {r['b']}: {r['diff']:+.4f} [{r['ci'][0]:+.4f},{r['ci'][1]:+.4f}] p_holm={r['p_holm']:.4f}")
    print("Compute (params | train s/seed | ms/window | peak MB):")
    for n, c in out["compute"].items():
        mem = [x for x in c["peak_mem_mb"] if x]; print(f"  {n:18s} {c['params']:>9,d} | {np.mean(c['train_s']):7.0f} | {np.mean(c['infer_ms_per_window']):6.2f} | {np.mean(mem) if mem else float('nan'):7.0f}")
    print(f"\nsaved {json_path}")


if __name__ == "__main__":
    main()
