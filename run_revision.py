"""Revision experiments requested by the referee, in one runner.

What it does (per dataset, per target/decoder setting):
  * MATCHED validation search: DCRNN and DyGCN-AC-LSTM get the SAME grid
    (hidden {32,64} x hops {2,3}); LSTM and AC-LSTM get hidden {32,64}.
    Selection = validation RMSE, one run per config, fixed seed. Test is never
    touched during selection; all validation scores are saved.
  * ABLATION: DyGCN-AC-LSTM with a FIXED adjacency (same cell, same tuned config,
    same parameters) -> isolates dynamic vs static graph inside the same model.
  * Naive forecasts: persistence, seasonal-naive, training mean.
  * Reports per-seed RMSE, per-horizon RMSE, paired seed t-tests with Holm,
    and a moving-block bootstrap over test windows (time-level uncertainty).
  * Saves everything to results/<tag>.json so nothing is lost.

Settings:
  --target smoothed|raw   smoothed = paper protocol; raw = log + z-score, no smoothing
  --residual              persistence-anchored decoder for every learned model
"""
import argparse, json, os, time
import numpy as np, torch
from src.abilene import load_abilene
from src.preprocessing import preprocess
from src.datasets import make_windows
from src.adjacency import build_adjacency
from src.train import precompute_adjacency, run_epoch
from src.metrics import all_metrics
from src.dygcn_ac_lstm import DyGCNACLSTM
from src.dcrnn import DCRNN
from src.baselines import LSTMBaseline, ACLSTMBaseline
from src.residual import Residual
from src.evaluation import (per_horizon_rmse, window_mse, persistence, seasonal_naive,
                            paired_seed_tests, block_bootstrap_diff)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SEQ = HOR = 12
W, K, P, G = 48, 6, 4, 4


def prepare(a):
    TM, meta = load_abilene(a.path, drop_node=a.drop_node, sample_min=a.sample_min,
                            min_active_frac=a.min_active_frac, log_transform=True)
    TM = TM[a.start_step:]
    if a.max_steps: TM = TM[:a.max_steps]
    T = len(TM); tr, va = int(0.65 * T), int(0.80 * T)
    den, _ = preprocess(TM, tr, c=4, alpha0=0.3, steps_per_day=meta["steps_per_day"],
                        smooth=(a.target == "smoothed"))
    static = build_adjacency(den[:W], K)
    sets = {}
    for k, (lo, hi) in {"train": (0, tr), "val": (tr, va), "test": (va, T)}.items():
        X, Y, idx = make_windows(den[lo:hi], SEQ, HOR); sets[k] = (X, Y, idx + lo)
    need = [o - SEQ + t for _, _, O in sets.values() for o in O for t in range(SEQ)]
    amap = precompute_adjacency(den, need, W, K, P, static=static)
    return den, meta, sets, amap, torch.tensor(static, dtype=torch.float32)


def make(name, F, h, k, residual):
    m = {"LSTM": lambda: LSTMBaseline(F, h, HOR),
         "AC-LSTM": lambda: ACLSTMBaseline(F, h, G, HOR),
         "DCRNN": lambda: DCRNN(hidden=h, K=k, layers=2, horizon=HOR),
         "DyGCN-AC-LSTM": lambda: DyGCNACLSTM(h, G, k, HOR),
         "DyGCN-static": lambda: DyGCNACLSTM(h, G, k, HOR)}[name]()
    return Residual(m) if residual else m


IS_GRAPH = {"LSTM": False, "AC-LSTM": False, "DCRNN": True, "DyGCN-AC-LSTM": True, "DyGCN-static": True}
USES_STATIC = {"DCRNN", "DyGCN-static"}


def fit(model, sets, amap, name, sadj, epochs):
    model = model.to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs, eta_min=1e-5)
    X, Y, O = sets["train"]; st = sadj if name in USES_STATIC else None
    for _ in range(epochs):
        run_epoch(model, X, Y, O, amap, opt=opt, tf=0.5, is_graph=IS_GRAPH[name],
                  device=DEVICE, static_adj=st); sch.step()
    return model


def predict(model, sets, split, amap, name, sadj):
    X, Y, O = sets[split]; st = sadj if name in USES_STATIC else None
    _, P_ = run_epoch(model, X, Y, O, amap, opt=None, is_graph=IS_GRAPH[name],
                      device=DEVICE, static_adj=st)
    return P_


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True)
    ap.add_argument("--drop-node", type=int, default=None)
    ap.add_argument("--sample-min", type=int, default=5)
    ap.add_argument("--min-active-frac", type=float, default=0.5)
    ap.add_argument("--max-steps", type=int, default=None)
    ap.add_argument("--start-step", type=int, default=0,
                    help="use steps [start, start+max_steps): e.g. 12096 = Abilene weeks 7-12, an uninspected period")
    ap.add_argument("--target", choices=["smoothed", "raw"], default="smoothed")
    ap.add_argument("--residual", action="store_true")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 456, 789, 1024])
    ap.add_argument("--tag", default=None)
    ap.add_argument("--outdir", default="results",
                    help="where JSON + per-seed predictions go (use a Google Drive folder to survive disconnects)")
    ap.add_argument("--fixed", nargs="+", default=None,
                    help="skip tuning, e.g. LSTM=32 AC-LSTM=32 DCRNN=64,3 DyGCN-AC-LSTM=64,3")
    a = ap.parse_args()
    tag = a.tag or (f"{os.path.splitext(os.path.basename(a.path))[0]}_{a.target}_{'resid' if a.residual else 'abs'}"
                    + (f"_start{a.start_step}" if a.start_step else ""))
    print(f"device: {DEVICE} | run: {tag}", flush=True)
    os.makedirs(a.outdir, exist_ok=True)
    pred_dir = os.path.join(a.outdir, f"{tag}_preds"); os.makedirs(pred_dir, exist_ok=True)
    json_path = os.path.join(a.outdir, f"{tag}.json")

    den, meta, sets, amap, sadj = prepare(a)
    F = den.shape[1]; spd = meta["steps_per_day"]
    Xte, Yte, Ote = sets["test"]
    print(f"F={F} flows | windows train/val/test = "
          f"{len(sets['train'][0])}/{len(sets['val'][0])}/{len(Xte)}", flush=True)
    out = {"tag": tag, "args": vars(a), "F": F, "tuning": {}, "test": {}}

    # ---- naive forecasts (deterministic) ----
    naive = {"Persistence": persistence(Xte, HOR),
             "Seasonal-naive": seasonal_naive(den, Ote, HOR, spd),
             "Training-mean": np.zeros_like(Yte)}
    wmse = {}
    for n, Pn in naive.items():
        out["test"][n] = {"rmse": all_metrics(Yte, Pn)["RMSE"], "horizon": per_horizon_rmse(Yte, Pn)}
        wmse[n] = window_mse(Yte, Pn)
        print(f"  {n:16s} test RMSE {out['test'][n]['rmse']:.4f}", flush=True)

    # ---- matched validation search ----
    grids = {"LSTM": [(32, 0), (64, 0)], "AC-LSTM": [(32, 0), (64, 0)],
             "DCRNN": [(h, k) for h in (32, 64) for k in (2, 3)],
             "DyGCN-AC-LSTM": [(h, k) for h in (32, 64) for k in (2, 3)]}
    chosen = {}
    if a.fixed:
        for item in a.fixed:
            name, cfg = item.split("=")
            parts = [int(x) for x in cfg.split(",")]
            chosen[name] = (parts[0], parts[1] if len(parts) > 1 else 0)
            out["tuning"][name] = {"selected": {"hidden": chosen[name][0], "hops": chosen[name][1]},
                                   "note": "fixed via --fixed (taken from an earlier tuning log)"}
        missing = [n for n in grids if n not in chosen]
        assert not missing, f"--fixed is missing: {missing}"
        print("using fixed configs:", chosen, flush=True)
        grids = {}
    for name, grid in grids.items():
        res = []
        for (h, k) in grid:
            torch.manual_seed(0); np.random.seed(0)
            m = fit(make(name, F, h, k, a.residual), sets, amap, name, sadj, a.epochs)
            v = all_metrics(sets["val"][1], predict(m, sets, "val", amap, name, sadj))["RMSE"]
            res.append({"hidden": h, "hops": k, "val_rmse": v})
            print(f"  [tune {name}] hidden={h} hops={k} -> val {v:.4f}", flush=True)
        best = min(res, key=lambda r: r["val_rmse"]); chosen[name] = (best["hidden"], best["hops"])
        out["tuning"][name] = {"grid": res, "selected": best}
    chosen["DyGCN-static"] = chosen["DyGCN-AC-LSTM"]          # ablation: identical config
    out["tuning"]["DyGCN-static"] = {"selected": "same as DyGCN-AC-LSTM (controlled ablation)"}

    # ---- seeds ----
    per_seed = {n: [] for n in chosen}; preds = {n: [] for n in chosen}
    for seed in a.seeds:
        for name, (h, k) in chosen.items():
            fpath = os.path.join(pred_dir, f"{name}_seed{seed}.npy")
            if os.path.exists(fpath):                        # resume: already done
                Pm = np.load(fpath); r = all_metrics(Yte, Pm)["RMSE"]
                per_seed[name].append(r); preds[name].append(Pm)
                print(f"seed {seed} {name:16s} RMSE {r:.4f}  (loaded, already done)", flush=True)
                continue
            torch.manual_seed(seed); np.random.seed(seed); t0 = time.time()
            m = fit(make(name, F, h, k, a.residual), sets, amap, name, sadj, a.epochs)
            Pm = predict(m, sets, "test", amap, name, sadj)
            np.save(fpath, Pm.astype(np.float32))           # saved immediately
            r = all_metrics(Yte, Pm)["RMSE"]; per_seed[name].append(r); preds[name].append(Pm)
            print(f"seed {seed} {name:16s} RMSE {r:.4f}  ({time.time()-t0:.0f}s)", flush=True)
            json.dump({**out, "partial_per_seed": per_seed}, open(json_path, "w"), indent=1)

    for name in chosen:
        v = np.array(per_seed[name]); Pm = np.mean(preds[name], axis=0)
        out["test"][name] = {"per_seed": v.tolist(), "mean": float(v.mean()), "sd": float(v.std(ddof=1)),
                             "horizon_seed_avg": per_horizon_rmse(Yte, Pm)}
        wmse[name] = np.mean([window_mse(Yte, p) for p in preds[name]], axis=0)

    pairs = [("DyGCN-AC-LSTM", "DCRNN"), ("DyGCN-AC-LSTM", "DyGCN-static"), ("AC-LSTM", "DyGCN-AC-LSTM")]
    out["paired_seed_tests"] = paired_seed_tests(per_seed, pairs)
    bpairs = pairs + [("DCRNN", "Persistence"), ("DyGCN-AC-LSTM", "Persistence")]
    out["block_bootstrap"] = {f"{x}-{y}": block_bootstrap_diff(wmse[x], wmse[y]) for x, y in bpairs}
    out["block_length_sensitivity"] = {f"{x}-{y}": {str(b): block_bootstrap_diff(wmse[x], wmse[y], block=b)["ci"]
                                       for b in (1, 3, 5, 10)} for x, y in bpairs}
    out["window_mse_seed_avg"] = {k: np.asarray(v).tolist() for k, v in wmse.items()}
    json.dump(out, open(json_path, "w"), indent=1)

    print(f"\n=== {tag}: test RMSE (mean +/- sd over {len(a.seeds)} seeds) ===")
    for n in ["Persistence", "Seasonal-naive", "Training-mean"]:
        print(f"{n:16s} {out['test'][n]['rmse']:.4f}")
    for n in chosen:
        print(f"{n:16s} {out['test'][n]['mean']:.4f} +/- {out['test'][n]['sd']:.4f}   selected {chosen[n]}")
    print("\nPaired seed tests (Holm-adjusted):")
    for r in out["paired_seed_tests"]:
        print(f"  {r['a']} - {r['b']}: {r['diff']:+.4f} CI [{r['ci'][0]:+.4f},{r['ci'][1]:+.4f}] "
              f"t={r['t']:.2f} p={r['p']:.4f} p_holm={r['p_holm']:.4f}")
    print("Block bootstrap over test windows (RMSE diff, 95% CI):")
    for k_, b in out["block_bootstrap"].items():
        print(f"  {k_}: {b['diff']:+.4f} [{b['ci'][0]:+.4f},{b['ci'][1]:+.4f}]")
    print("Block-length sensitivity (95% CI for block = 1, 3, 5, 10 windows):")
    for k_, d in out["block_length_sensitivity"].items():
        print(f"  {k_}: " + "  ".join(f"b{b}[{c[0]:+.4f},{c[1]:+.4f}]" for b, c in d.items()))
    print(f"\nsaved {json_path}")


if __name__ == "__main__":
    main()
