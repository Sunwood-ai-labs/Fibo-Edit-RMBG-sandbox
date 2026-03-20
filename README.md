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

Tested command on this machine:

```powershell
uv run fibo-rmbg `
  --input .\example\grok-image-square.png `
  --output .\outputs\grok-image-square.rmbg.png `
  --mask-output .\outputs\grok-image-square.mask.png `
  --max-side 256 `
  --num-inference-steps 1 `
  --dtype bfloat16
```

## Notes

- This sandbox was verified on Windows with an RTX 3060 6GB environment.
- The current stable setting in this repo is `--max-side 256 --num-inference-steps 1 --dtype bfloat16`.
- Input examples live in `example/`.
- Generated results are written to `outputs/`.
