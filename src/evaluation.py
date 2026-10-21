"""Evaluation helpers requested in review (NumPy only, tested without torch).

- per-horizon RMSE
- persistence / seasonal-naive forecasts on the same windows
- paired seed-level t-tests with Holm correction
- moving-block bootstrap over chronological test windows (time-level uncertainty)
"""
import numpy as np
from scipy import stats


def per_horizon_rmse(Y, P):
    """Y, P: [n_windows, H, F] -> list of H RMSEs."""
    return np.sqrt(((Y - P) ** 2).mean(axis=(0, 2))).tolist()


def window_mse(Y, P):
    """Per-window MSE, [n_windows] (chronological order preserved)."""
    return ((Y - P) ** 2).mean(axis=(1, 2))


def persistence(X, H):
    """Repeat the last observed input step for all H horizons."""
    return np.repeat(X[:, -1:, :], H, axis=1)


def seasonal_naive(series, origins, H, period):
    """Value one period earlier for each target step (causal)."""
    return np.stack([series[o + np.arange(H) - period] for o in origins])


def holm(pvals):
    p = np.asarray(pvals, float); m = len(p); order = np.argsort(p)
    adj = np.empty(m); run = 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (m - k) * p[i])); adj[i] = run
    return adj.tolist()


def paired_seed_tests(per_seed, pairs):
    """per_seed: {model: [rmse per seed]}; pairs: [(a, b), ...] testing a - b.
    Returns rows with mean diff, 95% CI, t, p, Holm-adjusted p, per-seed diffs."""
    rows = []
    for a, b in pairs:
        x, y = np.array(per_seed[a]), np.array(per_seed[b]); d = x - y; n = len(d)
        h = stats.t.ppf(0.975, n - 1) * d.std(ddof=1) / np.sqrt(n)
        t = stats.ttest_rel(x, y)
        rows.append(dict(a=a, b=b, diff=float(d.mean()), ci=[float(d.mean() - h), float(d.mean() + h)],
                         t=float(t.statistic), df=n - 1, p=float(t.pvalue), per_seed=d.round(5).tolist()))
    for r, p in zip(rows, holm([r["p"] for r in rows])):
        r["p_holm"] = p
    return rows


def block_bootstrap_diff(mse_a, mse_b, block=5, n_boot=2000, seed=0):
    """RMSE(a) - RMSE(b) with a moving-block bootstrap over chronological windows.
    Blocks keep temporal dependence; this is uncertainty over test periods,
    NOT independent replications of the networks."""
    mse_a, mse_b = np.asarray(mse_a), np.asarray(mse_b); n = len(mse_a)
    rng = np.random.default_rng(seed); nb = int(np.ceil(n / block))
    starts = np.arange(n - block + 1); out = []
    for _ in range(n_boot):
        idx = np.concatenate([np.arange(s, s + block) for s in rng.choice(starts, nb)])[:n]
        out.append(np.sqrt(mse_a[idx].mean()) - np.sqrt(mse_b[idx].mean()))
    point = float(np.sqrt(mse_a.mean()) - np.sqrt(mse_b.mean()))
    return dict(diff=point, ci=[float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))],
                block=block, n_boot=n_boot)
