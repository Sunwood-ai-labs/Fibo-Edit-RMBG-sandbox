# Fibo-Edit-RMBG-sandbox

Minimal `uv` sandbox for running `briaai/Fibo-Edit-RMBG` with a local image and an `HF_TOKEN` stored in `.env`.

## Setup

1. Copy `.env.example` to `.env`
2. Set `HF_TOKEN`
3. Sync dependencies

```powershell
uv sync --python 3.11 --index https://download.pytorch.org/whl/cu128
```

## Run

Fast baseline tested on this machine:

```powershell
uv run fibo-rmbg `
  --input .\example\grok-image-square.png `
  --output .\outputs\grok-image-square.rmbg.png `
  --mask-output .\outputs\grok-image-square.mask.png `
  --max-side 256 `
  --num-inference-steps 1 `
  --dtype bfloat16
```

Less jagged fallback that still fits this 6GB GPU:

```powershell
uv run fibo-rmbg `
  --input .\example\grok-image-square.png `
  --output .\outputs\grok-image-square.balanced.rmbg.png `
  --mask-output .\outputs\grok-image-square.balanced.mask.png `
  --max-side 256 `
  --num-inference-steps 4 `
  --dtype bfloat16 `
  --mask-style balanced
```

## Notes

- This sandbox was verified on Windows with an RTX 3060 6GB environment.
- The fastest stable setting in this repo is `--max-side 256 --num-inference-steps 1 --dtype bfloat16`.
- For less jagged boundaries, start with `--mask-style balanced` and increase `--num-inference-steps` before trying a larger `--max-side`.
- Use `--mask-style hard` only as a comparison reference when you want to inspect staircase artifacts.
- Input examples live in `example/`.
- Generated results are written to `outputs/`.

## Edge Experiments

To compare jagged versus blurred boundaries across all example inputs, use the experiment runner:

```powershell
uv run python .\scripts\run_edge_experiments.py
```

If the sweep is interrupted, resume only the missing work:

```powershell
uv run python .\scripts\run_edge_experiments.py --resume
```

To rebuild the comparison boards and summaries without rerunning inference:

```powershell
uv run python .\scripts\run_edge_experiments.py --postprocess-only
```

Experiment outputs are recorded here:

- Overview: [`experiments/README.md`](./experiments/README.md)
- Per-input comparison boards: `experiments/by-input/`
- Canonical CSV summary: `experiments/summary.csv`
- Raw per-run logs and artifacts: `experiments/runs/`

<img alt="Edge experiment overview" src="./experiments/overview.png" width="1200" />

Current readout from the saved sweep:

- `balanced` is the best default axis for reducing jagged edges on this machine.
- `balanced / 320 / 4 steps` looked best on three inputs.
- `kling-generate-square.png` fell back to `balanced / 256 / 4 steps` because the heavier `320 / 4 steps` run failed with memory pressure on this setup.
- `hard` is useful as a staircase-artifact reference, not as the default recommendation.

Direct compare boards:

- [`car-palette-team-style-2k`](./experiments/by-input/car-palette-team-style-2k.md)
- [`delpmaspu-2k`](./experiments/by-input/delpmaspu-2k.md)
- [`grok-image-square`](./experiments/by-input/grok-image-square.md)
- [`kling-generate-square`](./experiments/by-input/kling-generate-square.md)
