---
layout: home

hero:
  name: Fibo-Edit-RMBG Sandbox
  text: UV ベースのローカル背景除去ワークフロー
  tagline: BRIA のゲート付き Fibo-Edit-RMBG をローカル実行し、境界の差分比較と Windows GPU 上の制約を記録します。
  image:
    src: /logo.svg
    alt: Fibo-Edit-RMBG Sandbox icon
  actions:
    - theme: brand
      text: はじめに
      link: /ja/guide/getting-started
    - theme: alt
      text: 実験ガイド
      link: /ja/guide/experiments
    - theme: alt
      text: English Docs
      link: /

features:
  - title: ローカル CLI 中心
    details: 単一画像の背景除去を `uv` 管理の CLI からそのまま再現できます。
  - title: 比較実験を保存済み
    details: 4 枚の入力に対して `soft` / `balanced` / `hard` の境界差分を compare board と CSV で残しています。
  - title: 実機制約を文書化
    details: Windows RTX 3060 6GB 環境で発生した CPU offload 失敗やメモリ圧迫も含めて記録しています。
---

## このサイトにあるもの

- `uv` ベースの CLI 導入手順
- 実験結果の読み方
- 既知の制約
- ライセンス境界

英語版は [English docs](/) から開けます。

リポジトリ参照:

- [GitHub リポジトリ](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox)
- [実験ギャラリー](https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox/blob/main/experiments/README.md)
