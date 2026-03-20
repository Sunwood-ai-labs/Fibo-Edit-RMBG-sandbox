# 実験

このリポジトリには、比較ボードと要約 CSV を生成する sweep runner が入っています。

## コマンド

フルスイープ:

```powershell
uv run python .\scripts\run_edge_experiments.py
```

中断再開:

```powershell
uv run python .\scripts\run_edge_experiments.py --resume
```

Markdown と画像だけ再生成:

```powershell
uv run python .\scripts\run_edge_experiments.py --postprocess-only
```

## 保存済み overview

![4 枚の入力画像に対する境界マスク比較の overview](/edge-overview.png)

## 現在の推奨

- 3 枚は `balanced / 320 / 4 steps`
- `kling-generate-square.png` は `balanced / 256 / 4 steps`

## リポジトリ参照

- [Experiment gallery README](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/blob/main/experiments/README.md)
- [Canonical summary CSV](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/blob/main/experiments/summary.csv)
- [Per-input compare boards](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/tree/main/experiments/by-input)
