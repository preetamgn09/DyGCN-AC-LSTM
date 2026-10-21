"""Common-scale and operational metrics (NumPy only).

Every forecast, whatever target it was trained on, is mapped back to traffic VOLUME
(invert z-score, then expm1 of the log1p transform) and compared with the ACTUAL raw
volumes. This puts all target x decoder settings on one common scale.

Link loads use the 0/1 routing matrix R (rows = original OD pairs i*N+j, cols = links):
load = volume @ R[pairs]. Only the modelled OD flows contribute (self-flows and flows of a
dropped node are excluded from both forecast and actual), so loads are the load induced by
the forecast flows.
  * flow_wape        : sum|V^-V| / sum V over flows
  * link_wape        : same over link loads
  * bottleneck_err   : mean over (window, step) of |max_l L^ - max_l L| / max_l L
  * underprov_rate@h : share of (window, step, link) with actual load > (1+h) * forecast load,
                       i.e. links provisioned at forecast + h headroom that would be exceeded
No link capacities are available, so these are load-based, not utilization-based.
"""
import numpy as np


def to_volume(Z, mu, sigma):
    """z-units -> traffic volume. Z [..., F]; mu, sigma [F]."""
    return np.clip(np.expm1(Z * sigma + mu), 0, None)


def load_routing(path, N_orig, flow_pairs):
    R = np.genfromtxt(path, delimiter=",")
    R = R[:, ~np.all(np.isnan(R), axis=0)]
    assert R.shape[0] == N_orig * N_orig, f"routing rows {R.shape[0]} != {N_orig}^2"
    rows = [i * N_orig + j for (i, j) in flow_pairs]
    R = R[rows]
    return R[:, R.sum(0) > 0]                      # links carrying at least one modelled flow


def operational_metrics(V_true, V_pred, R=None, headrooms=(0.0, 0.1, 0.2)):
    """V_true, V_pred: [n, H, F] volumes."""
    out = {"flow_wape": float(np.abs(V_pred - V_true).sum() / max(V_true.sum(), 1e-12))}
    if R is not None:
        Lt, Lp = V_true @ R, V_pred @ R                          # [n, H, links]
        out["link_wape"] = float(np.abs(Lp - Lt).sum() / max(Lt.sum(), 1e-12))
        mt, mp = Lt.max(-1), Lp.max(-1)
        out["bottleneck_err"] = float(np.mean(np.abs(mp - mt) / np.maximum(mt, 1e-12)))
        for h in headrooms:
            out[f"underprov_rate@{int(h*100)}"] = float(np.mean(Lt > (1 + h) * Lp))
        out["n_links"] = int(R.shape[1])
    return out


def scale_metrics(Yz, Pz, train_z):
    """Common-scale errors on the unsmoothed z series. MASE scale = mean |one-step change|
    of the training split (per-flow-pooled), so MASE < 1 beats in-sample one-step naive."""
    err = Pz - Yz
    scale = np.mean(np.abs(np.diff(train_z, axis=0)))
    return {"rmse_rawz": float(np.sqrt(np.mean(err ** 2))), "mae_rawz": float(np.mean(np.abs(err))),
            "mase": float(np.mean(np.abs(err)) / scale),
            "horizon_rmse_rawz": np.sqrt((err ** 2).mean(axis=(0, 2))).tolist(),
            "horizon_mae_rawz": np.abs(err).mean(axis=(0, 2)).tolist()}
