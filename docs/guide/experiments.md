# Experiments

The repository includes a sweep runner that records per-variant outputs, compare boards, and a canonical summary.

## Commands

Run the full sweep:

```powershell
uv run python .\scripts\run_edge_experiments.py
```

Resume only missing work:

```powershell
uv run python .\scripts\run_edge_experiments.py --resume
```

Rebuild Markdown and image artifacts without rerunning inference:

```powershell
uv run python .\scripts\run_edge_experiments.py --postprocess-only
```

## Saved overview

![Overview gallery comparing edge-mask behavior across four example inputs](/edge-overview.png)

## Current recommendation

- `balanced / 320 / 4 steps` looked best on:
  - `car-palette-team-style-2k.png`
  - `delpmaspu-2k.png`
  - `grok-image-square.png`
- `balanced / 256 / 4 steps` is the safer fallback and was the best successful option for `kling-generate-square.png`

## Per-input boards

### `car-palette-team-style-2k.png`

A vehicle cutout with a long curved spoiler edge, trim decals, and narrow protrusions. Use this board to judge whether the alpha stays smooth along curved bodywork without turning into staircase pixels.

Start with `balanced / 320 / 4 steps`.

<img alt="Per-input compare board for car-palette-team-style-2k showing spoiler-edge behavior across variants" src="/edge-gallery/car-palette-team-style-2k.compare.png" width="1040" />

### `delpmaspu-2k.png`

A flat illustration with a shallow cream-colored curve. This case is useful for separating soft halos from truly clean anti-aliased edges on rounded shapes.

Start with `balanced / 320 / 4 steps`.

<img alt="Per-input compare board for delpmaspu-2k focusing on a smooth curved illustration edge" src="/edge-gallery/delpmaspu-2k.compare.png" width="1040" />

### `grok-image-square.png`

A repeated jet-like silhouette with diagonal fins and sharp corners. This board is the easiest way to compare crispness on angular edges without falling into the blockiness of `hard`.

Start with `balanced / 320 / 4 steps`.

<img alt="Per-input compare board for grok-image-square focusing on diagonal fins and sharp corners" src="/edge-gallery/grok-image-square.compare.png" width="1040" />

### `kling-generate-square.png`

A low-resolution pixel-art dog. This board shows how well each setting respects intentionally chunky outlines while still avoiding over-quantized hard-mask artifacts.

Start with `balanced / 256 / 4 steps` because the `320 / 4 steps` variant failed on this machine.

<img alt="Per-input compare board for kling-generate-square showing pixel-art contour handling across variants" src="/edge-gallery/kling-generate-square.compare.png" width="1040" />

## Repository references

- [Experiment gallery README](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/blob/main/experiments/README.md)
- [Canonical summary CSV](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/blob/main/experiments/summary.csv)
- [Per-input compare boards](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/tree/main/experiments/by-input)
