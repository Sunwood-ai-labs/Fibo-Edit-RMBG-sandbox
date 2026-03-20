# Repository Polish QA Inventory

## Requested Outcomes

- Fully polish the repository for public use.
- Use the repository-polish workflow in full-finish mode.
- Carry the work through docs, metadata, verification, commit, and push.

## Polish Mode

- Full polish (`完全整備`)

## Planned Deliverables

- Refresh the English `README.md`
- Add `README.ja.md`
- Add a browsable bilingual VitePress docs site under `docs/`
- Add a reusable docs/logo visual asset if it materially improves the project
- Add a repository `LICENSE`
- Add GitHub Actions workflows for Python CI and docs/Pages deployment
- Improve Python packaging metadata in `pyproject.toml`
- Add lightweight tests for repo-safe helper behavior
- Add a small repository support file set such as `.editorconfig`
- Update GitHub repository metadata when credentials are available

## User-Facing Artifacts Expected To Change

- `README.md`
- `README.ja.md`
- `docs/index.md`
- `docs/guide/getting-started.md`
- `docs/guide/cli.md`
- `docs/guide/experiments.md`
- `docs/guide/troubleshooting.md`
- `docs/guide/licensing.md`
- `docs/ja/index.md`
- `docs/ja/guide/getting-started.md`
- `docs/ja/guide/cli.md`
- `docs/ja/guide/experiments.md`
- `docs/ja/guide/troubleshooting.md`
- `docs/ja/guide/licensing.md`
- `docs/.vitepress/config.*`
- `docs/public/*`
- `.github/workflows/ci.yml`
- `.github/workflows/docs.yml`
- `LICENSE`
- `pyproject.toml`
- `.editorconfig`
- `tests/*`

## Planned Final Claims

- The repository has bilingual README support.
- The repository has a browsable docs site with English and Japanese pages.
- The docs build locally.
- The repository has CI for the Python package and helper tests.
- The repository has a Pages deployment workflow for the docs site.
- The repo code is licensed, while upstream model weights remain under the upstream license.
- The public metadata fields on GitHub were updated if auth remained available.
- The quick-start commands and CLI docs match the current code.
- Experiment comparison materials remain linked and readable.

## QA Coverage Checklist

- README links, headings, language switch, and commands
- `README.ja.md` structure parity with `README.md`
- Docs nav, page reachability, locale parity, and build output path
- Logo/icon references if added
- CI workflow triggers and commands
- Pages workflow build path and base URL assumptions
- `uv run` usage in Python-facing commands
- `pyproject.toml` metadata accuracy
- Test command execution
- GitHub metadata update confirmation if applied

## Validation Results

- `uv run --with pytest --with pillow --with python-dotenv pytest` -> passed (`6` tests)
- `uv run --with pillow --with python-dotenv python -m fibo_edit_rmbg_sandbox.cli --help` -> passed
- `uv run python .\scripts\run_edge_experiments.py --help` -> passed
- `uv run python .\scripts\run_edge_experiments.py --postprocess-only` -> passed
- `npm run docs:build` in `docs/` -> passed
- `uv build` -> passed
- Markdown sweep for stale public references to `runs/.../README.md`, `/experiments/overview.png`, and `/fibo-cutout-mark.svg` under `docs/` and `experiments/` -> passed
- GitHub repository metadata updated through `gh repo edit`
- GitHub Pages site created through workflow-backed Pages configuration

## Residual Notes

- Raw experiment retries remain local-only under `experiments/runs/` and are intentionally excluded from Git.
- The saved experiment gallery publishes representative run IDs instead of raw run-folder links.
- Vite/VitePress dev dependencies previously reported moderate audit findings, but no newer stable `vitepress` release was available during this polish pass.
