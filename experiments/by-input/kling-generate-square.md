# kling-generate-square.png

![comparison](./kling-generate-square.compare.png)

| Variant | Status | Runtime (s) | Run | Notes |
| --- | --- | ---: | --- | --- |
| Balanced / 256 / 2 steps | success | 90.89 | [20260320_220128_kling-generate-square_balanced_s256_n2_bf16](../runs/20260320_220128_kling-generate-square_balanced_s256_n2_bf16/README.md) | Safe anti-jaggy baseline. |
| Hard / 256 / 4 steps / thr128 | success | 114.61 | [20260320_225251_kling-generate-square_hard_s256_n4_t128_bf16](../runs/20260320_225251_kling-generate-square_hard_s256_n4_t128_bf16/README.md) | Crisp reference; likely to show staircase artifacts. |
| Soft / 256 / 4 steps | success | 117.17 | [20260320_225048_kling-generate-square_soft_s256_n4_bf16](../runs/20260320_225048_kling-generate-square_soft_s256_n4_bf16/README.md) | Smoothest edge reference; watch for halos. |
| Balanced / 256 / 4 steps | success | 117.36 | [20260320_220259_kling-generate-square_balanced_s256_n4_bf16](../runs/20260320_220259_kling-generate-square_balanced_s256_n4_bf16/README.md) | Primary quality candidate on this 6GB GPU. |
| Balanced / 320 / 2 steps | success | 180.1 | [20260320_224555_kling-generate-square_balanced_s320_n2_bf16](../runs/20260320_224555_kling-generate-square_balanced_s320_n2_bf16/README.md) | Higher mask resolution at a moderate runtime cost. |
| Balanced / 320 / 4 steps | failed | 11.62 | [20260320_224902_kling-generate-square_balanced_s320_n4_bf16](../runs/20260320_224902_kling-generate-square_balanced_s320_n4_bf16/README.md) | Stretch target for better edges if VRAM holds. Failure: MemoryError |

Recommended first check: `Balanced / 256 / 4 steps`
