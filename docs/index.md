---
layout: home

hero:
  name: Fibo-Edit-RMBG Sandbox
  text: UV-first local background-removal workflow
  tagline: Run BRIA's gated Fibo-Edit-RMBG model locally, compare edge behavior, and document Windows GPU tradeoffs.
  image:
    src: /fibo-cutout-mark.svg
    alt: Fibo-Edit-RMBG Sandbox icon
  actions:
    - theme: brand
      text: Getting Started
      link: /guide/getting-started
    - theme: alt
      text: Experiment Guide
      link: /guide/experiments
    - theme: alt
      text: GitHub Repo
      link: https://github.com/Sunwood-ai-labs/Fibo-Edit-RMBG-sandbox

features:
  - title: Local CLI first
    details: The repo exposes a compact `uv`-managed CLI for single-image background removal without hiding the actual inference settings.
  - title: Edge comparison included
    details: Saved experiments compare `soft`, `balanced`, and `hard` mask behavior across four example inputs with reusable boards and summaries.
  - title: Practical Windows notes
    details: The docs call out the real constraints hit on a Windows RTX 3060 6GB machine, including CPU offload failures and memory pressure edges.
---

## What lives here

This project is intentionally narrow:

- a Python CLI under `fibo_edit_rmbg_sandbox/`
- saved example outputs under `outputs/`
- experiment reports under `experiments/`
- a reusable sweep script under `scripts/run_edge_experiments.py`

Use the guide pages for quickstart, CLI details, experiments, troubleshooting, and licensing boundaries.
