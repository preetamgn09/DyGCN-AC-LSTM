"""Additional forecasters for the broadened comparison.

All return [B, H, F] and accept forward(x_seq, adj_seq=None, y_seq=None, teacher_forcing=0.0)
so the runner and the Residual wrapper treat them like the other models.

  * LinearForecaster - channel-independent linear map from the L inputs to the H outputs,
    shared across flows (DLinear/NLinear-style strong simple baseline, Zeng et al. 2023).
  * STGCN            - Yu et al. (IJCAI'18): two ST-Conv blocks (gated temporal conv ->
    Chebyshev graph conv -> gated temporal conv) over the fixed adjacency, direct H-step output.
  * GraphWaveNet     - Wu et al. (IJCAI'19): gated dilated TCN + diffusion graph conv over the
    fixed adjacency (both directions) plus a learned adaptive adjacency, skip connections,
    direct H-step output.
STGCN and Graph WaveNet are compact faithful re-implementations, not the reference code.
"""
import torch
import torch.nn as nn
import torch.nn.functional as Fn


def _fixed_adj(adj_seq):
    A = adj_seq[0]
    return A[0] if A.dim() == 3 else A


class LinearForecaster(nn.Module):
    def __init__(self, L=12, H=12):
        super().__init__()
        self.lin = nn.Linear(L, H)

    def forward(self, x_seq, *_, **__):                         # x [B, L, F]
        return self.lin(x_seq.transpose(1, 2)).transpose(1, 2)


# ------------------------------- STGCN ---------------------------------------
class GatedTemporalConv(nn.Module):
    """Temporal conv with GLU gate and residual; [B,C,T,N] -> [B,C',T-Kt+1,N]."""
    def __init__(self, c_in, c_out, Kt=3):
        super().__init__()
        self.Kt = Kt
        self.conv = nn.Conv2d(c_in, 2 * c_out, (Kt, 1))
        self.align = nn.Conv2d(c_in, c_out, 1) if c_in != c_out else nn.Identity()

    def forward(self, x):
        res = self.align(x)[:, :, self.Kt - 1:, :]
        p, q = self.conv(x).chunk(2, dim=1)
        return (p + res) * torch.sigmoid(q)


class ChebGraphConv(nn.Module):
    """K-order Chebyshev graph conv with L~ = -A_hat (normalized Laplacian, lambda_max ~ 2)."""
    def __init__(self, c_in, c_out, K):
        super().__init__()
        self.K = K
        self.theta = nn.Linear(K * c_in, c_out)

    def forward(self, x, A):                                       # x [B,C,T,N], A [N,N]
        Lt = -A
        Tk = [x]
        if self.K > 1:
            Tk.append(torch.einsum("nm,bctm->bctn", Lt, x))
        for _ in range(2, self.K):
            Tk.append(2 * torch.einsum("nm,bctm->bctn", Lt, Tk[-1]) - Tk[-2])
        h = torch.cat(Tk, dim=1).permute(0, 2, 3, 1)               # [B,T,N,K*C]
        return self.theta(h).permute(0, 3, 1, 2)                    # [B,C',T,N]


class STConvBlock(nn.Module):
    def __init__(self, c_in, c_t, c_s, N, K, Kt=3, dropout=0.1):
        super().__init__()
        self.t1 = GatedTemporalConv(c_in, c_t, Kt)
        self.g = ChebGraphConv(c_t, c_s, K)
        self.t2 = GatedTemporalConv(c_s, c_t, Kt)
        self.norm = nn.LayerNorm([N, c_t])
        self.drop = nn.Dropout(dropout)

    def forward(self, x, A):
        x = self.t2(torch.relu(self.g(self.t1(x), A)))
        x = self.norm(x.permute(0, 2, 3, 1)).permute(0, 3, 1, 2)
        return self.drop(x)


class STGCN(nn.Module):
    def __init__(self, N, hidden=64, K=3, L=12, H=12, Kt=3):
        super().__init__()
        c_s = max(hidden // 4, 8)
        self.b1 = STConvBlock(1, hidden, c_s, N, K, Kt)
        self.b2 = STConvBlock(hidden, hidden, c_s, N, K, Kt)
        T_out = L - 4 * (Kt - 1)
        assert T_out >= 1, "sequence too short for two ST blocks"
        self.out = nn.Sequential(nn.Linear(T_out * hidden, hidden), nn.ReLU(), nn.Linear(hidden, H))

    def forward(self, x_seq, adj_seq=None, *_, **__):              # x [B,L,N]
        A = _fixed_adj(adj_seq)
        x = self.b2(self.b1(x_seq.unsqueeze(1), A), A)              # [B,C,T',N]
        B, C, T, N = x.shape
        return self.out(x.permute(0, 3, 2, 1).reshape(B, N, T * C)).transpose(1, 2)


# ---------------------------- Graph WaveNet ----------------------------------
class GWNGraphConv(nn.Module):
    """Diffusion conv over a list of supports up to `order` hops, then 1x1 conv."""
    def __init__(self, c_in, c_out, n_supports, order=2, dropout=0.3):
        super().__init__()
        self.order = order
        self.mlp = nn.Conv2d((order * n_supports + 1) * c_in, c_out, 1)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, supports):                                 # x [B,C,N,T]
        out = [x]
        for S in supports:
            x1 = x
            for _ in range(self.order):
                x1 = torch.einsum("bcnt,nm->bcmt", x1, S)
                out.append(x1)
        return self.drop(self.mlp(torch.cat(out, dim=1)))


class GraphWaveNet(nn.Module):
    def __init__(self, N, hidden=32, order=2, L=12, H=12, emb=10, blocks=4, layers=2):
        super().__init__()
        r, skip, end = hidden, 4 * hidden, 8 * hidden
        self.start = nn.Conv2d(1, r, 1)
        self.E1 = nn.Parameter(torch.randn(N, emb) * 0.1)
        self.E2 = nn.Parameter(torch.randn(emb, N) * 0.1)
        self.dil = [2 ** i for _ in range(blocks) for i in range(layers)]
        self.filt = nn.ModuleList([nn.Conv2d(r, r, (1, 2), dilation=(1, d)) for d in self.dil])
        self.gate = nn.ModuleList([nn.Conv2d(r, r, (1, 2), dilation=(1, d)) for d in self.dil])
        self.skipc = nn.ModuleList([nn.Conv2d(r, skip, 1) for _ in self.dil])
        self.gconv = nn.ModuleList([GWNGraphConv(r, r, 3, order) for _ in self.dil])
        self.bn = nn.ModuleList([nn.BatchNorm2d(r) for _ in self.dil])
        self.rf = 1 + sum(self.dil)
        self.end1 = nn.Conv2d(skip, end, 1)
        self.end2 = nn.Conv2d(end, H, 1)

    def forward(self, x_seq, adj_seq=None, *_, **__):              # x [B,L,N]
        A = _fixed_adj(adj_seq)
        adp = Fn.softmax(Fn.relu(self.E1 @ self.E2), dim=1)
        supports = [A, A.t(), adp]
        x = x_seq.transpose(1, 2).unsqueeze(1)                      # [B,1,N,L]
        if x.shape[-1] < self.rf:
            x = Fn.pad(x, (self.rf - x.shape[-1], 0))
        x = self.start(x)
        skip = None
        for i in range(len(self.dil)):
            res = x
            h = torch.tanh(self.filt[i](x)) * torch.sigmoid(self.gate[i](x))
            s = self.skipc[i](h)
            skip = s if skip is None else s + skip[..., -s.shape[-1]:]
            h = self.gconv[i](h, supports)
            x = self.bn[i](h + res[..., -h.shape[-1]:])
        out = self.end2(torch.relu(self.end1(torch.relu(skip))))   # [B,H,N,T']
        return out[..., -1]                                         # [B,H,N]
