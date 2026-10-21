"""summarize.py - turn all run_v3 JSON results in a folder into paper-ready tables.

Usage:  python summarize.py /content/drive/MyDrive/dygcn_results_v3
Writes summary.md next to the JSON files and prints it.

Tables:
 1. Per-run main table: own-target RMSE, common-scale raw-z RMSE, MASE, link WAPE,
    bottleneck error, under-provisioning@10% (mean over seeds; naive forecasts deterministic).
 2. Factorial (start 0): best learned model vs persistence in each target x decoder cell,
    on the COMMON raw-z scale and on link WAPE.
 3. Rolling origins: DyGCN-AC-LSTM minus DCRNN (and minus fixed graph) per origin block,
    with the number of blocks in which DCRNN is better.
 4. Compute: parameters, training s/seed, ms/window, peak MB.
 5. Tuning stability: selected config vs per-tune-seed winners.
"""
import json, glob, os, sys
import numpy as np

d = sys.argv[1] if len(sys.argv) > 1 else "results"
runs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(d, "*_v3.json")))]
runs = [r for r in runs if "paired_seed_tests" in r]          # completed runs only
L = []
def P(s=""): L.append(s)

def cell(r):
    a = r["args"]; return (os.path.basename(a["path"]).split("_")[0], a["target"], "resid" if a["residual"] else "abs", a["start_step"])

def mm(e, k):
    return e["metrics_mean"][k] if "metrics_mean" in e else e[k]

P(f"# Summary of {len(runs)} completed runs in {d}\n")
for r in runs:
    ds, tg, dec, st = cell(r); hasR = "link_wape" in r["test"]["Persistence"]
    P(f"## {ds} | target={tg} | decoder={dec} | start={st}\n")
    P("| model | own RMSE (mean ± sd) | raw-z RMSE | MASE |" + (" link WAPE | bottleneck | underprov@10% |" if hasR else ""))
    P("|---|---|---|---|" + ("---|---|---|" if hasR else ""))
    for n, e in r["test"].items():
        own = f"{e['mean']:.4f} ± {e['sd']:.4f}" if "mean" in e else f"{e['rmse_own']:.4f}"
        row = f"| {n} | {own} | {mm(e,'rmse_rawz'):.4f} | {mm(e,'mase'):.3f} |"
        if hasR: row += f" {mm(e,'link_wape'):.3f} | {mm(e,'bottleneck_err'):.3f} | {mm(e,'underprov_rate@10'):.3f} |"
        P(row)
    P("\nPaired seed tests (Holm):")
    for t in r["paired_seed_tests"]:
        P(f"- {t['a']} − {t['b']}: {t['diff']:+.4f} [{t['ci'][0]:+.4f}, {t['ci'][1]:+.4f}], p_Holm = {t['p_holm']:.4f}")
    P("\nBlock-bootstrap 95% CI on the common raw-z scale, block = 1 / 3 / 5 / 10 windows:")
    for k, v in r["block_bootstrap_rawz"].items():
        P(f"- {k}: " + "  ".join(f"b{b} [{c['ci'][0]:+.4f}, {c['ci'][1]:+.4f}]" for b, c in v.items()))
    P()

# factorial
P("## Factorial (first block): best learned model vs persistence, common scale\n")
P("| data | target | decoder | best learned (raw-z RMSE) | persistence own-input | persistence raw-input | best link WAPE | persistence link WAPE |")
P("|---|---|---|---|---|---|---|---|")
for r in runs:
    ds, tg, dec, st = cell(r)
    if st: continue
    learned = {n: e for n, e in r["test"].items() if "metrics_mean" in e}
    b = min(learned, key=lambda n: learned[n]["metrics_mean"]["rmse_rawz"])
    pr = r["test"].get("Persistence-raw-input", r["test"]["Persistence"])
    lw = lambda e: f"{mm(e,'link_wape'):.3f}" if "link_wape" in e.get("metrics_mean", e) else "-"
    P(f"| {ds} | {tg} | {dec} | {b} {learned[b]['metrics_mean']['rmse_rawz']:.4f} | {mm(r['test']['Persistence'],'rmse_rawz'):.4f} | {mm(pr,'rmse_rawz'):.4f} | {lw(learned[b])} | {lw(r['test']['Persistence'])} |")

# rolling origins
P("\n## Rolling origins: DyGCN-AC-LSTM minus comparator (own-target RMSE; negative favors DyGCN)\n")
groups = {}
for r in runs:
    ds, tg, dec, st = cell(r); groups.setdefault((ds, tg, dec), []).append(r)
for g, rs in groups.items():
    if len(rs) < 2: continue
    P(f"**{g[0]} | {g[1]} | {g[2]}**\n")
    P("| start | vs DCRNN | p_Holm | vs fixed graph | p_Holm |"); P("|---|---|---|---|---|")
    better = 0
    for r in sorted(rs, key=lambda r: r["args"]["start_step"]):
        t = {x["b"]: x for x in r["paired_seed_tests"]}
        dc, fx = t.get("DCRNN"), t.get("DyGCN-static")
        better += int(dc is not None and dc["diff"] > 0)
        P(f"| {r['args']['start_step']} | {dc['diff']:+.4f} | {dc['p_holm']:.4f} | " + (f"{fx['diff']:+.4f} | {fx['p_holm']:.4f} |" if fx else "- | - |"))
    P(f"\nDCRNN better in {better} of {len(rs)} origin blocks.\n")

# compute
P("## Compute (mean over seeds)\n")
P("| run | model | params | train s/seed | ms/window | peak MB |"); P("|---|---|---|---|---|---|")
for r in runs:
    for n, c in r["compute"].items():
        mem = [x for x in c["peak_mem_mb"] if x]
        P(f"| {r['tag']} | {n} | {c['params']:,} | {np.mean(c['train_s']):.0f} | {np.mean(c['infer_ms_per_window']):.2f} | {np.mean(mem):.0f} |" if mem else
          f"| {r['tag']} | {n} | {c['params']:,} | {np.mean(c['train_s']):.0f} | {np.mean(c['infer_ms_per_window']):.2f} | - |")

# tuning stability
P("\n## Tuning stability (selected by mean validation RMSE vs winner per tuning seed)\n")
for r in runs:
    for n, t in r["tuning"].items():
        if "winner_per_tune_seed" in t:
            P(f"- {r['tag']} {n}: selected {tuple(t['selected'])}; per-seed winners {[tuple(w) for w in t['winner_per_tune_seed']]}")
open(os.path.join(d, "summary.md"), "w").write("\n".join(L)); print("\n".join(L))
