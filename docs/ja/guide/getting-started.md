# はじめに

## 必要なもの

- Python 3.11
- `uv`
- `.env` に入れる Hugging Face token
- `briaai/Fibo-Edit-RMBG` への承認済みアクセス

## セットアップ

```powershell
Copy-Item .env.example .env
```

`.env` に token を設定:

```text
HF_TOKEN=hf_your_token_here
```

依存関係の同期:

```powershell
uv sync --python 3.11 --index https://download.pytorch.org/whl/cu128
```

## 最初の実行

```powershell
uv run fibo-rmbg `
  --input .\example\grok-image-square.png `
  --output .\outputs\grok-image-square.rmbg.png `
  --mask-output .\outputs\grok-image-square.mask.png `
  --max-side 256 `
  --num-inference-steps 1 `
  --dtype bfloat16
```

ギザつきを抑えたいとき:

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
