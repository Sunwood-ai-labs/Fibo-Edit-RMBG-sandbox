# トラブルシュート

## token 周りの失敗

`HF_TOKEN` が見つからないと言われたら:

- `.env.example` を `.env` にコピー
- `HF_TOKEN` を設定
- Hugging Face 側でモデルアクセスが承認されているか確認

## 6GB GPU のメモリ圧迫

保存済み実験は RTX 3060 6GB 環境で取得しています。実務上の目安は次の通りです。

- `max-side 256` が最も安全
- `balanced / 320 / 4 steps` は重い入力で失敗することがある
- `hard` はメモリ改善ではなく、境界の二値化寄り挙動を変えるだけ

## CPU offload の注意

この Windows 環境では `--cpu-offload` が安定しません。デコード時にバックエンド/カーネル系の失敗を確認しています。

## docs のローカルビルド

```powershell
Set-Location .\docs
npm install
npm run docs:build
```
