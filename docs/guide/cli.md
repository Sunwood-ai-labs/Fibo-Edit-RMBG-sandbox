# CLI

The installed command is:

```powershell
uv run fibo-rmbg --help
```

## Core arguments

| Argument | Purpose |
| --- | --- |
| `--input` | Source image path |
| `--output` | RGBA output path |
| `--mask-output` | Optional grayscale mask path |
| `--device` | `auto`, `cuda`, or `cpu` |
| `--dtype` | `auto`, `bfloat16`, `float16`, or `float32` |
| `--num-inference-steps` | Denoising steps |
| `--guidance-scale` | Guidance scale |
| `--max-side` | Longest-edge resize cap before inference |
| `--cpu-offload` | Reduce GPU pressure, but not reliable in this tested Windows setup |
| `--vae-dtype` | Optional VAE dtype override |
| `--mask-style` | `soft`, `balanced`, or `hard` |
| `--alpha-threshold` | Optional post-resize alpha threshold |

## Practical guidance

- `soft`: smoothest edges, but most likely to blur or halo
- `balanced`: best default tradeoff from the saved experiment sweep
- `hard`: useful for comparison, but it can staircase curved edges

## Typical commands

Fast baseline:

```powershell
uv run fibo-rmbg --input .\example\grok-image-square.png --max-side 256 --num-inference-steps 1 --dtype bfloat16
```

Sharper fallback:

```powershell
uv run fibo-rmbg --input .\example\grok-image-square.png --max-side 256 --num-inference-steps 4 --dtype bfloat16 --mask-style balanced
```
