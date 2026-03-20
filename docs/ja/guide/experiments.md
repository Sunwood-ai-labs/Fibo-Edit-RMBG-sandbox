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

## 入力ごとの比較ボード

### `car-palette-team-style-2k.png`

車体の長いスポイラー曲線、細いパーツ、ロゴ付近の境界を含むケースです。曲面の輪郭が階段状にならず、自然なアルファになっているかを確認しやすい入力です。

最初は `balanced / 320 / 4 steps` を見てください。

<img alt="car-palette-team-style-2k の比較ボード。スポイラー付近の境界表現を比較" src="/edge-gallery/car-palette-team-style-2k.compare.png" width="1040" />

### `delpmaspu-2k.png`

なだらかなクリーム色のカーブを含む、フラットなイラスト系の入力です。ハローの出方と、丸い境界のアンチエイリアスの質を見比べるのに向いています。

最初は `balanced / 320 / 4 steps` を見るのがおすすめです。

<img alt="delpmaspu-2k の比較ボード。なだらかな曲線境界の滑らかさを比較" src="/edge-gallery/delpmaspu-2k.compare.png" width="1040" />

### `grok-image-square.png`

斜めのフィンや尖った角を含む、戦闘機風シルエットの入力です。角のシャープさを保ちつつ、`hard` のようなブロック感を避けられているかが見どころです。

最初は `balanced / 320 / 4 steps` を確認してください。

<img alt="grok-image-square の比較ボード。斜めのフィンと鋭い角の表現を比較" src="/edge-gallery/grok-image-square.compare.png" width="1040" />

### `kling-generate-square.png`

ドット感を残した犬のピクセルアート入力です。意図的なカクつきは活かしつつ、不自然なハードマスク化を避けられるかを見るためのケースです。

この入力だけは `320 / 4 steps` がこのマシンで失敗したため、`balanced / 256 / 4 steps` を先に見るのが安全です。

<img alt="kling-generate-square の比較ボード。ピクセルアート輪郭の扱いを比較" src="/edge-gallery/kling-generate-square.compare.png" width="1040" />

## リポジトリ参照

- [Experiment gallery README](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/blob/main/experiments/README.md)
- [Canonical summary CSV](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/blob/main/experiments/summary.csv)
- [Per-input compare boards](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/tree/main/experiments/by-input)
