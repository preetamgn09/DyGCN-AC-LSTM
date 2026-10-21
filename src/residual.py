"""Persistence-anchored (residual) wrapper for any forecaster.

The inner model sees inputs and targets re-centred on the last observed step and
predicts the CHANGE from it; the wrapper adds the last value back. Inputs, teacher-
forced targets and outputs all live in the same re-centred space, so the decoder's
own feedback stays consistent. With a zero output it reduces exactly to persistence.
"""
import torch.nn as nn


class Residual(nn.Module):
    def __init__(self, inner):
        super().__init__()
        self.inner = inner

    def forward(self, x_seq, *args, y_seq=None, teacher_forcing=0.0, **kw):
        last = x_seq[:, -1:, :]                                  # [B,1,F]
        y_c = None if y_seq is None else y_seq - last
        out = self.inner(x_seq - last, *args, y_seq=y_c, teacher_forcing=teacher_forcing, **kw)
        return out + last
