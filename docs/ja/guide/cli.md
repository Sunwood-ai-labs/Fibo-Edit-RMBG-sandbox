# CLI

インストール済みコマンド:

```powershell
uv run fibo-rmbg --help
```

## 主な引数

| 引数 | 役割 |
| --- | --- |
| `--input` | 入力画像 |
| `--output` | RGBA 出力先 |
| `--mask-output` | グレースケールマスク出力先 |
| `--device` | `auto`, `cuda`, `cpu` |
| `--dtype` | `auto`, `bfloat16`, `float16`, `float32` |
| `--num-inference-steps` | 推論ステップ数 |
| `--guidance-scale` | guidance scale |
| `--max-side` | 推論前リサイズの最大辺 |
| `--cpu-offload` | GPU 圧迫を減らすが、この環境では不安定 |
| `--vae-dtype` | VAE 側 dtype の上書き |
| `--mask-style` | `soft`, `balanced`, `hard` |
| `--alpha-threshold` | 後処理の alpha threshold |

## 実運用の目安

- `soft`: もっとも滑らかだが、境界が太りやすい
- `balanced`: 今回の保存済み実験では最も無難
- `hard`: 比較基準として有効だが、曲線が階段状になりやすい
