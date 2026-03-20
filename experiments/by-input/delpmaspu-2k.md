# delpmaspu-2k.png

![Comparison board highlighting full-mask and edge-crop differences for delpmaspu-2k.png](./delpmaspu-2k.compare.png)

Published pages keep the representative run ID for traceability. Raw `experiments/runs/` folders stay local-only and are ignored by Git.

| Variant | Status | Runtime (s) | Run ID | Notes |
| --- | --- | ---: | --- | --- |
| Balanced / 256 / 2 steps | success | 80.26 | `20260320_214015_delpmaspu-2k_balanced_s256_n2_bf16` | Safe anti-jaggy baseline. |
| Balanced / 320 / 2 steps | success | 89.8 | `20260320_214312_delpmaspu-2k_balanced_s320_n2_bf16` | Higher mask resolution at a moderate runtime cost. |
| Balanced / 256 / 4 steps | success | 97.09 | `20260320_214135_delpmaspu-2k_balanced_s256_n4_bf16` | Primary quality candidate on this 6GB GPU. |
| Hard / 256 / 4 steps / thr128 | success | 98.06 | `20260320_214816_delpmaspu-2k_hard_s256_n4_t128_bf16` | Crisp reference; likely to show staircase artifacts. |
| Soft / 256 / 4 steps | success | 98.16 | `20260320_214638_delpmaspu-2k_soft_s256_n4_bf16` | Smoothest edge reference; watch for halos. |
| Balanced / 320 / 4 steps | success | 115.64 | `20260320_214442_delpmaspu-2k_balanced_s320_n4_bf16` | Stretch target for better edges if VRAM holds. |

Recommended first check: `Balanced / 320 / 4 steps`
