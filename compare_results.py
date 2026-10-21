"""compare_results.py - check a re-run against an archived result file.

Usage:  python compare_results.py results/v3/Abilene_TM_raw_resid_start24192_v3.json  my_rerun/Abilene_TM_raw_resid_start24192_v3.json
Compares the mean own-target test RMSE of every model present in both files.
GPU training is not bit-for-bit deterministic, so differences up to about 0.002 are expected;
larger differences indicate a different environment, data file, or code version.
"""
import json, sys

def means(path):
    d = json.load(open(path))
    return {m: e["mean"] for m, e in d["test"].items() if isinstance(e, dict) and "mean" in e}

if len(sys.argv) != 3:
    sys.exit(__doc__)
a, b = means(sys.argv[1]), means(sys.argv[2])
common = sorted(set(a) & set(b))
if not common:
    sys.exit("No models in common - are these results for the same condition?")
worst = 0.0
print(f"{'model':26s} {'archived':>9s} {'re-run':>9s} {'diff':>9s}")
for m in common:
    diff = b[m] - a[m]; worst = max(worst, abs(diff))
    print(f"{m:26s} {a[m]:9.4f} {b[m]:9.4f} {diff:+9.4f}")
print(f"\nlargest absolute difference: {worst:.4f} -> " + ("MATCH (within 0.002)" if worst <= 0.002 else "CHECK: larger than expected"))
