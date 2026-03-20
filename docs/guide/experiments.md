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

## Repository references

- [Experiment gallery README](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/blob/main/experiments/README.md)
- [Canonical summary CSV](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/blob/main/experiments/summary.csv)
- [Per-input compare boards](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/tree/main/experiments/by-input)
