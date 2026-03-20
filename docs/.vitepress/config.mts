import { defineConfig } from "vitepress";

const repositoryUrl = "https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox";
const docsUrl = "https://sunwood-ai-labs.github.io/Fibo-Edit-RMBG-sandbox/";

export default defineConfig({
  title: "Fibo-Edit-RMBG Sandbox",
  description: "UV-powered wrapper CLI and experiment workspace for BRIA Fibo-Edit-RMBG.",
  lang: "en-US",
  base: "/Fibo-Edit-RMBG-sandbox/",
  cleanUrls: true,
  lastUpdated: true,
  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: "/logo.svg" }],
  ],
  themeConfig: {
    logo: "/logo.svg",
    socialLinks: [{ icon: "github", link: repositoryUrl }],
    search: {
      provider: "local",
    },
  },
  locales: {
    root: {
      label: "English",
      lang: "en-US",
      link: "/",
      themeConfig: {
        nav: [
          { text: "Guide", link: "/guide/getting-started" },
          { text: "CLI", link: "/guide/cli" },
          { text: "Experiments", link: "/guide/experiments" },
          { text: "Troubleshooting", link: "/guide/troubleshooting" },
          { text: "Licensing", link: "/guide/licensing" },
          { text: "GitHub", link: repositoryUrl },
        ],
        sidebar: {
          "/guide/": [
            {
              text: "Guide",
              items: [
                { text: "Getting Started", link: "/guide/getting-started" },
                { text: "CLI Usage", link: "/guide/cli" },
                { text: "Experiments", link: "/guide/experiments" },
                { text: "Troubleshooting", link: "/guide/troubleshooting" },
                { text: "Licensing", link: "/guide/licensing" },
              ],
            },
          ],
        },
        outlineTitle: "On this page",
        docFooter: {
          prev: "Previous page",
          next: "Next page",
        },
        footer: {
          message: "Repo code is MIT. Upstream BRIA model access remains gated and subject to BRIA terms.",
          copyright: "Copyright © 2026 Sunwood AI Labs",
        },
      },
    },
    ja: {
      label: "日本語",
      lang: "ja-JP",
      link: "/ja/",
      themeConfig: {
        nav: [
          { text: "ガイド", link: "/ja/guide/getting-started" },
          { text: "CLI", link: "/ja/guide/cli" },
          { text: "実験", link: "/ja/guide/experiments" },
          { text: "トラブルシューティング", link: "/ja/guide/troubleshooting" },
          { text: "ライセンス", link: "/ja/guide/licensing" },
          { text: "GitHub", link: repositoryUrl },
        ],
        sidebar: {
          "/ja/guide/": [
            {
              text: "ガイド",
              items: [
                { text: "はじめに", link: "/ja/guide/getting-started" },
                { text: "CLI の使い方", link: "/ja/guide/cli" },
                { text: "実験記録", link: "/ja/guide/experiments" },
                { text: "トラブルシューティング", link: "/ja/guide/troubleshooting" },
                { text: "ライセンス", link: "/ja/guide/licensing" },
              ],
            },
          ],
        },
        outlineTitle: "このページ",
        docFooter: {
          prev: "前のページ",
          next: "次のページ",
        },
        footer: {
          message: "MIT はこのリポジトリのコードに対して適用されます。上流 BRIA モデルは別ライセンスです。",
          copyright: "Copyright © 2026 Sunwood AI Labs",
        },
      },
    },
  },
  sitemap: {
    hostname: docsUrl,
  },
});
