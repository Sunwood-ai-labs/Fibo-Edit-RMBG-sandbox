<p align="center">
  <img src="./docs/public/logo.svg" alt="Fibo-Edit-RMBG Sandbox logo" width="112" />
</p>

<h1 align="center">Fibo-Edit-RMBG Sandbox</h1>

<p align="center">
  UV-powered wrapper CLI and experiment workspace for the gated
  <a href="https://huggingface.co/briaai/Fibo-Edit-RMBG">BRIA Fibo-Edit-RMBG</a> model.
</p>

<p align="center">
  <a href="./README.md"><strong>English</strong></a>
  |
  <a href="./README.ja.md"><strong>日本語</strong></a>
</p>

<p align="center">
  <a href="https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/actions/workflows/ci.yml"><img src="https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/actions/workflows/docs.yml"><img src="https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/actions/workflows/docs.yml/badge.svg" alt="Docs" /></a>
  <img src="https://img.shields.io/badge/python-3.11--3.12-3776AB?logo=python&logoColor=white" alt="Python 3.11-3.12" />
  <img src="https://img.shields.io/badge/uv-workflow-4B8BBE" alt="UV workflow" />
  <img src="https://img.shields.io/badge/license-MIT-2EA043" alt="MIT license" />
</p>

## ✨ Overview

This repository wraps a local workflow around `briaai/Fibo-Edit-RMBG` so you can:

- install the Python environment with `uv`
- run background removal from a local CLI
- compare edge behavior across `soft`, `balanced`, and `hard`
- keep outputs, compare boards, and summary CSVs under version control

This repo contains wrapper code, docs, and recorded experiment artifacts.
It does **not** redistribute the upstream model weights. Access to the model still depends on
Hugging Face approval and BRIA's gated `bria-fibo-edit` terms.

Primary links:

- [Docs site](https://sunwood-ai-labs.github.io/Fibo-Edit-RMBG-sandbox/)
- [Experiment gallery](./experiments/README.md)

## 🚀 Quick Start

1. Request access to the upstream model:
   [briaai/Fibo-Edit-RMBG](https://huggingface.co/briaai/Fibo-Edit-RMBG)
2. Copy `.env.example` to `.env`
3. Set `HF_TOKEN`
4. Install dependencies with `uv`

```powershell
uv sync --python 3.11 --index https://download.pytorch.org/whl/cu128
```

Fastest verified baseline on the current Windows + RTX 3060 6GB setup:

```powershell
uv run fibo-rmbg `
  --input .\example\grok-image-square.png `
  --output .\outputs\grok-image-square.rmbg.png `
  --mask-output .\outputs\grok-image-square.mask.png `
  --max-side 256 `
  --num-inference-steps 1 `
  --dtype bfloat16
```

Safer anti-jaggy fallback on the same machine:

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

## 🧪 Edge Experiments

The repository includes recorded edge-comparison sweeps for the example inputs.

- `balanced` is the safest anti-jaggy default on the verified Windows + RTX 3060 6GB setup
- `balanced / 320 / 4 steps` looked best on three inputs in the recorded sweep
- `kling-generate-square.png` falls back to `balanced / 256 / 4 steps` on this machine
- `hard` is kept as a staircase-artifact reference, not as the default recommendation

Run the sweep:

```powershell
uv run python .\scripts\run_edge_experiments.py
```

Resume only missing runs:

```powershell
uv run python .\scripts\run_edge_experiments.py --resume
```

Rebuild compare boards and summaries without rerunning inference:

```powershell
uv run python .\scripts\run_edge_experiments.py --postprocess-only
```

<img src="./experiments/overview.png" alt="Overview gallery comparing edge masks across four example inputs" width="1200" />

See also:

- [Experiment overview](./experiments/README.md)
- [Per-input compare boards](./experiments/by-input/)
- [Canonical CSV summary](./experiments/summary.csv)

## ⚙️ CLI Notes

The current CLI supports:

- `--mask-style soft|balanced|hard`
- `--num-inference-steps`
- `--max-side`
- `--alpha-threshold`
- `--cpu-offload` for experiments only

Local guidance from the saved runs:

- `balanced` keeps edges smoother than `hard` without adding as much halo as `soft`
- `hard` tends to create staircase edges on curved boundaries
- `soft` can hide jaggies but often fattens the alpha edge
- `--cpu-offload` was not reliable on the verified Windows setup because the VAE path hit backend issues

More detail:

- [Documentation site](https://sunwood-ai-labs.github.io/Fibo-Edit-RMBG-sandbox/)
- [Getting Started](./docs/guide/getting-started.md)
- [CLI Guide](./docs/guide/cli.md)
- [Experiments Guide](./docs/guide/experiments.md)
- [Troubleshooting](./docs/guide/troubleshooting.md)

## 📁 Repository Layout

```text
example/                      Input images used for local runs
experiments/                  Saved experiment summaries and compare boards
fibo_edit_rmbg_sandbox/       Python package and CLI entry point
outputs/                      Selected output PNG samples
scripts/run_edge_experiments.py
docs/                         VitePress documentation site
```

## 🩺 Troubleshooting

- If model loading fails before inference starts, confirm that your Hugging Face access request was approved and that `HF_TOKEN` is valid
- If a larger run fails on Windows with `os error 1455` or `MemoryError`, reduce `--max-side` or `--num-inference-steps`
- If edges look too hard, move from `hard` to `balanced`
- If edges look too blurry, keep `balanced` and raise `--num-inference-steps` before forcing `hard`

The troubleshooting guide collects the known local failure modes:
[docs/guide/troubleshooting.md](./docs/guide/troubleshooting.md)

## 📄 License

- Repository code and docs: [MIT](./LICENSE)
- Upstream model weights and access terms: BRIA's gated `bria-fibo-edit` license on Hugging Face

The repo license applies to this wrapper codebase only.
