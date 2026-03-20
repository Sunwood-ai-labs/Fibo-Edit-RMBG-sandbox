# Edge Experiments

Parameter sweep focused on reducing jagged cutout edges on the current Windows + RTX 3060 6GB environment.

- Representative rows: `24` (`23` success / `1` failed)
- Raw run folders: [`runs/`](./runs/)
- CSV summary: [`summary.csv`](./summary.csv)

## Current Recommendation

- `car-palette-team-style-2k.png`: start by reviewing `Balanced / 320 / 4 steps` in [`20260320_213504_car-palette-team-style-2k_balanced_s320_n4_bf16`](./runs/20260320_213504_car-palette-team-style-2k_balanced_s320_n4_bf16/README.md)
- `delpmaspu-2k.png`: start by reviewing `Balanced / 320 / 4 steps` in [`20260320_214442_delpmaspu-2k_balanced_s320_n4_bf16`](./runs/20260320_214442_delpmaspu-2k_balanced_s320_n4_bf16/README.md)
- `grok-image-square.png`: start by reviewing `Balanced / 320 / 4 steps` in [`20260320_215508_grok-image-square_balanced_s320_n4_bf16`](./runs/20260320_215508_grok-image-square_balanced_s320_n4_bf16/README.md)
- `kling-generate-square.png`: start by reviewing `Balanced / 256 / 4 steps` in [`20260320_220259_kling-generate-square_balanced_s256_n4_bf16`](./runs/20260320_220259_kling-generate-square_balanced_s256_n4_bf16/README.md)

## Overview Gallery

<img alt="Edge experiment overview" src="./overview.png" width="1200" />

## What To Look For

- `balanced` is the main anti-jaggy setting. It keeps edges smoother than `hard` without adding as much halo as `soft`.
- `hard` is included as a failure-mode reference. It tends to turn curved edges into visible staircase pixels.
- `soft` can hide jaggies, but it also fattens boundaries and can leave a blurred edge halo.
- `320 / 4 steps` produced the nicest edges on three inputs, but `kling-generate-square.png` had to fall back to `256 / 4 steps` because the higher-cost variant failed on this machine.

## Per Input

- [`car-palette-team-style-2k.png`](./by-input/car-palette-team-style-2k.md)
- [`delpmaspu-2k.png`](./by-input/delpmaspu-2k.md)
- [`grok-image-square.png`](./by-input/grok-image-square.md)
- [`kling-generate-square.png`](./by-input/kling-generate-square.md)

## Embedded Compare Boards

### car-palette-team-style-2k.png

[Open notes and run table](./by-input/car-palette-team-style-2k.md)

<img alt="car-palette-team-style-2k.png edge comparison" src="./by-input/car-palette-team-style-2k.compare.png" width="1200" />

### delpmaspu-2k.png

[Open notes and run table](./by-input/delpmaspu-2k.md)

<img alt="delpmaspu-2k.png edge comparison" src="./by-input/delpmaspu-2k.compare.png" width="1200" />

### grok-image-square.png

[Open notes and run table](./by-input/grok-image-square.md)

<img alt="grok-image-square.png edge comparison" src="./by-input/grok-image-square.compare.png" width="1200" />

### kling-generate-square.png

[Open notes and run table](./by-input/kling-generate-square.md)

<img alt="kling-generate-square.png edge comparison" src="./by-input/kling-generate-square.compare.png" width="1200" />


## Failure Notes

- `balanced / 320 / 4 steps` can trip `MemoryError` on the heaviest input in this 6GB GPU + Windows setup.
- One `hard / 256 / 4 steps / thr128` retry ended in a native crash during pipeline load; the run folder is kept for reference.
- Raw retries are preserved under [`runs/`](./runs/), while [`summary.csv`](./summary.csv) and the `by-input/` pages keep one representative row per input x variant.
