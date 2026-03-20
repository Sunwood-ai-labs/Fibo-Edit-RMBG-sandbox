# Getting Started

## What you need

- Python 3.11
- `uv`
- a Hugging Face token in `.env`
- accepted access to `briaai/Fibo-Edit-RMBG`

## Setup

```powershell
Copy-Item .env.example .env
```

Add your token to `.env`:

```text
HF_TOKEN=hf_your_token_here
```

Install dependencies:

```powershell
uv sync --python 3.11 --index https://download.pytorch.org/whl/cu128
```

## First run

```powershell
uv run fibo-rmbg `
  --input .\example\grok-image-square.png `
  --output .\outputs\grok-image-square.rmbg.png `
  --mask-output .\outputs\grok-image-square.mask.png `
  --max-side 256 `
  --num-inference-steps 1 `
  --dtype bfloat16
```

If you want a less jagged result, start here instead:

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

## Output files

- RGBA cutouts go to `outputs/*.rmbg.png`
- grayscale masks go to `outputs/*.mask.png`
- sweep results and compare boards go to `experiments/`
