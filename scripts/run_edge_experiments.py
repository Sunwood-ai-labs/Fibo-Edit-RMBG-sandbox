from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = REPO_ROOT / "example"
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
RUNS_DIR = EXPERIMENTS_DIR / "runs"
BY_INPUT_DIR = EXPERIMENTS_DIR / "by-input"
SUMMARY_CSV = EXPERIMENTS_DIR / "summary.csv"
EXPERIMENTS_README = EXPERIMENTS_DIR / "README.md"
OVERVIEW_IMAGE = EXPERIMENTS_DIR / "overview.png"


@dataclass(frozen=True)
class Variant:
    slug: str
    label: str
    max_side: int
    steps: int
    mask_style: str
    alpha_threshold: int | None
    notes: str


VARIANTS: list[Variant] = [
    Variant(
        slug="balanced_s256_n2",
        label="Balanced / 256 / 2 steps",
        max_side=256,
        steps=2,
        mask_style="balanced",
        alpha_threshold=None,
        notes="Safe anti-jaggy baseline.",
    ),
    Variant(
        slug="balanced_s256_n4",
        label="Balanced / 256 / 4 steps",
        max_side=256,
        steps=4,
        mask_style="balanced",
        alpha_threshold=None,
        notes="Primary quality candidate on this 6GB GPU.",
    ),
    Variant(
        slug="balanced_s320_n2",
        label="Balanced / 320 / 2 steps",
        max_side=320,
        steps=2,
        mask_style="balanced",
        alpha_threshold=None,
        notes="Higher mask resolution at a moderate runtime cost.",
    ),
    Variant(
        slug="balanced_s320_n4",
        label="Balanced / 320 / 4 steps",
        max_side=320,
        steps=4,
        mask_style="balanced",
        alpha_threshold=None,
        notes="Stretch target for better edges if VRAM holds.",
    ),
    Variant(
        slug="soft_s256_n4",
        label="Soft / 256 / 4 steps",
        max_side=256,
        steps=4,
        mask_style="soft",
        alpha_threshold=None,
        notes="Smoothest edge reference; watch for halos.",
    ),
    Variant(
        slug="hard_s256_n4_t128",
        label="Hard / 256 / 4 steps / thr128",
        max_side=256,
        steps=4,
        mask_style="hard",
        alpha_threshold=128,
        notes="Crisp reference; likely to show staircase artifacts.",
    ),
]


SUMMARY_FIELDS = [
    "run_id",
    "date",
    "input",
    "variant_slug",
    "label",
    "mask_style",
    "max_side",
    "num_inference_steps",
    "dtype",
    "vae_dtype",
    "cpu_offload",
    "alpha_threshold",
    "guidance_scale",
    "status",
    "runtime_sec",
    "run_dir",
    "result_path",
    "mask_path",
    "compare_path",
    "notes",
    "git_commit",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run or postprocess edge-focused Fibo-Edit-RMBG experiments."
    )
    parser.add_argument(
        "--input",
        dest="inputs",
        action="append",
        help="Limit runs to one or more input file names from example/.",
    )
    parser.add_argument(
        "--variant",
        dest="variants",
        action="append",
        help="Limit runs to one or more variant slugs.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip input/variant pairs that already have a successful run.json record.",
    )
    parser.add_argument(
        "--postprocess-only",
        action="store_true",
        help="Do not run inference; only rebuild summary and comparison artifacts from existing runs.",
    )
    return parser.parse_args(argv)


def ensure_dirs() -> None:
    for path in (EXPERIMENTS_DIR, RUNS_DIR, BY_INPUT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return "unknown"


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def build_run_id(input_stem: str, variant: Variant) -> str:
    return f"{now_stamp()}_{input_stem}_{variant.slug}_bf16"


def command_for(input_path: Path, run_dir: Path, variant: Variant) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "fibo_edit_rmbg_sandbox.cli",
        "--input",
        str(input_path),
        "--output",
        str(run_dir / "result.rmbg.png"),
        "--mask-output",
        str(run_dir / "result.mask.png"),
        "--max-side",
        str(variant.max_side),
        "--num-inference-steps",
        str(variant.steps),
        "--dtype",
        "bfloat16",
        "--mask-style",
        variant.mask_style,
    ]
    if variant.alpha_threshold is not None:
        command.extend(["--alpha-threshold", str(variant.alpha_threshold)])
    return command


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_variant(input_path: Path, variant: Variant, commit_hash: str) -> dict[str, object]:
    run_id = build_run_id(input_path.stem, variant)
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    command = command_for(input_path, run_dir, variant)
    command_text = " ".join(f'"{part}"' if " " in part else part for part in command)
    write_text(run_dir / "command.txt", command_text + "\n")

    started_at = datetime.now().isoformat(timespec="seconds")
    start = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "HF_HUB_DISABLE_PROGRESS_BARS": "1"},
        check=False,
    )
    runtime_sec = round(time.perf_counter() - start, 2)
    combined_output = (result.stdout or "") + ("\n" if result.stdout and result.stderr else "") + (result.stderr or "")
    write_text(run_dir / "stdout.log", combined_output)

    status = "success" if result.returncode == 0 else "failed"
    failure_reason = ""
    if status == "failed":
        lines = [line.strip() for line in combined_output.splitlines() if line.strip()]
        failure_reason = lines[-1] if lines else f"exit={result.returncode}"

    row = {
        "run_id": run_id,
        "date": started_at,
        "input": input_path.name,
        "variant_slug": variant.slug,
        "label": variant.label,
        "mask_style": variant.mask_style,
        "max_side": variant.max_side,
        "num_inference_steps": variant.steps,
        "dtype": "bfloat16",
        "vae_dtype": "auto",
        "cpu_offload": False,
        "alpha_threshold": variant.alpha_threshold if variant.alpha_threshold is not None else "",
        "guidance_scale": 1.0,
        "status": status,
        "runtime_sec": runtime_sec,
        "run_dir": run_dir.relative_to(REPO_ROOT).as_posix(),
        "result_path": (run_dir / "result.rmbg.png").relative_to(REPO_ROOT).as_posix(),
        "mask_path": (run_dir / "result.mask.png").relative_to(REPO_ROOT).as_posix(),
        "compare_path": "",
        "notes": variant.notes if status == "success" else f"{variant.notes} Failure: {failure_reason}",
        "git_commit": commit_hash,
    }

    run_json = {
        **row,
        "command": command,
        "stdout_log": (run_dir / "stdout.log").relative_to(REPO_ROOT).as_posix(),
        "return_code": result.returncode,
    }
    write_text(run_dir / "run.json", json.dumps(run_json, indent=2, ensure_ascii=False) + "\n")
    write_text(
        run_dir / "README.md",
        render_run_readme(row, failure_reason),
    )
    return row


def render_run_readme(row: dict[str, object], failure_reason: str) -> str:
    status = row["status"]
    body = [
        f"# {row['run_id']}",
        "",
        "## Summary",
        "",
        f"- Input: `{row['input']}`",
        f"- Variant: `{row['label']}`",
        f"- Status: `{status}`",
        f"- Runtime: `{row['runtime_sec']} sec`",
        f"- Git commit: `{row['git_commit']}`",
    ]
    if row["alpha_threshold"] != "":
        body.append(f"- Alpha threshold: `{row['alpha_threshold']}`")
    if failure_reason:
        body.extend(["", "## Failure", "", f"- `{failure_reason}`"])
    body.extend(
        [
            "",
            "## Files",
            "",
            f"- Command: [`command.txt`](./command.txt)",
            f"- Log: [`stdout.log`](./stdout.log)",
            f"- Metadata: [`run.json`](./run.json)",
        ]
    )
    if status == "success":
        body.extend(
            [
                f"- Output: [`result.rmbg.png`](./result.rmbg.png)",
                f"- Mask: [`result.mask.png`](./result.mask.png)",
            ]
        )
    return "\n".join(body) + "\n"


def load_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(RUNS_DIR.glob("*/run.json")):
        rows.append(normalize_row(json.loads(path.read_text(encoding="utf-8"))))
    return rows


def normalize_row(row: dict[str, object]) -> dict[str, object]:
    normalized = dict(row)
    if normalized.get("status") != "failed":
        return normalized

    base_note, _, failure_note = str(normalized.get("notes", "")).partition(" Failure: ")
    failure_note = failure_note.strip()
    return_code = int(normalized.get("return_code", 0) or 0)
    raw_notes = str(normalized.get("notes", ""))

    if return_code == 3221225477:
        failure_note = "Native crash (0xC0000005 / access violation) while loading pipeline components"
    elif "os error 1455" in raw_notes:
        failure_note = "Windows paging file error (os error 1455) while loading weights"
    elif not failure_note:
        failure_note = f"Process exited with code {return_code}" if return_code else "Unknown failure"

    normalized["notes"] = f"{base_note} Failure: {failure_note}".strip()
    return normalized


def canonical_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    variant_rank = {variant.slug: index for index, variant in enumerate(VARIANTS)}
    picked: dict[tuple[str, str], dict[str, object]] = {}

    def score(row: dict[str, object]) -> tuple[int, str]:
        return (1 if row.get("status") == "success" else 0, str(row.get("date", "")))

    for row in rows:
        key = (str(row["input"]), str(row["variant_slug"]))
        current = picked.get(key)
        if current is None or score(row) > score(current):
            picked[key] = row

    return sorted(
        picked.values(),
        key=lambda row: (
            str(row["input"]),
            variant_rank.get(str(row["variant_slug"]), 999),
            str(row.get("date", "")),
        ),
    )


def select_inputs(requested: list[str] | None) -> list[Path]:
    inputs = sorted(path for path in EXAMPLE_DIR.glob("*") if path.is_file())
    if not inputs:
        raise FileNotFoundError(f"No input files found in {EXAMPLE_DIR}")
    if not requested:
        return inputs

    selected = [path for path in inputs if path.name in set(requested)]
    missing = sorted(set(requested) - {path.name for path in selected})
    if missing:
        raise FileNotFoundError(f"Requested input files were not found: {', '.join(missing)}")
    return selected


def select_variants(requested: list[str] | None) -> list[Variant]:
    if not requested:
        return VARIANTS

    by_slug = {variant.slug: variant for variant in VARIANTS}
    missing = [slug for slug in requested if slug not in by_slug]
    if missing:
        raise KeyError(f"Unknown variants requested: {', '.join(missing)}")
    return [by_slug[slug] for slug in requested]


def existing_success_keys() -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for row in canonical_rows(load_rows()):
        if row.get("status") == "success":
            keys.add((str(row["input"]), str(row["variant_slug"])))
    return keys


def write_summary_csv(rows: list[dict[str, object]]) -> None:
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in SUMMARY_FIELDS})


def load_image(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def load_mask(path: Path) -> Image.Image:
    return Image.open(path).convert("L")


def checkerboard(size: tuple[int, int], tile: int = 16) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, (235, 235, 235))
    draw = ImageDraw.Draw(image)
    for top in range(0, height, tile):
        for left in range(0, width, tile):
            if (left // tile + top // tile) % 2 == 0:
                draw.rectangle([left, top, left + tile - 1, top + tile - 1], fill=(210, 210, 210))
    return image


def composite_on_checker(rgba: Image.Image) -> Image.Image:
    base = checkerboard(rgba.size)
    base.paste(rgba.convert("RGB"), mask=rgba.getchannel("A"))
    return base


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGB", size, (245, 245, 245))
    image = image.convert("RGB")
    image.thumbnail(size, Image.LANCZOS)
    left = (size[0] - image.width) // 2
    top = (size[1] - image.height) // 2
    canvas.paste(image, (left, top))
    return canvas


def find_edge_crop_box(mask_path: Path, crop_size: int = 320) -> tuple[int, int, int, int]:
    mask = load_mask(mask_path)
    arr = np.asarray(mask, dtype=np.float32)
    edge = np.abs(np.diff(arr, axis=0, prepend=arr[:1, :])) + np.abs(np.diff(arr, axis=1, prepend=arr[:, :1]))

    height, width = arr.shape
    crop_w = min(crop_size, width)
    crop_h = min(crop_size, height)
    step = max(16, min(crop_w, crop_h) // 8)

    best_score = -1.0
    best = (0, 0, crop_w, crop_h)
    for top in range(0, max(1, height - crop_h + 1), step):
        for left in range(0, max(1, width - crop_w + 1), step):
            bottom = min(height, top + crop_h)
            right = min(width, left + crop_w)
            window = edge[top:bottom, left:right]
            score = float(window.mean())
            if score > best_score:
                best_score = score
                best = (left, top, right, bottom)
    return best


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str) -> None:
    draw.multiline_text(xy, text, fill=(20, 20, 20), spacing=4)


def create_input_compare_board(input_path: Path, rows: list[dict[str, object]]) -> Path | None:
    success_rows = [row for row in rows if row["status"] == "success"]
    if not success_rows:
        return None

    mask_path = REPO_ROOT / str(success_rows[0]["mask_path"])
    crop_box = find_edge_crop_box(mask_path)

    label_width = 320
    thumb_size = (200, 200)
    crop_size = (220, 220)
    row_height = 250
    header_height = 100
    board_width = label_width + thumb_size[0] + crop_size[0] + crop_size[0] + 80
    board_height = header_height + row_height * len(success_rows)

    board = Image.new("RGB", (board_width, board_height), (255, 255, 255))
    draw = ImageDraw.Draw(board)
    title = f"{input_path.name} edge comparison"
    draw_text(draw, (24, 20), title)
    draw_text(draw, (24, 52), "Columns: label | full mask | zoomed alpha crop | zoomed cutout crop")

    for index, row in enumerate(success_rows):
        top = header_height + index * row_height
        run_dir = REPO_ROOT / str(row["run_dir"])
        mask = load_mask(REPO_ROOT / str(row["mask_path"]))
        rgba = load_image(REPO_ROOT / str(row["result_path"]))
        crop_mask = mask.crop(crop_box).resize(crop_size, Image.NEAREST)
        crop_cutout = composite_on_checker(rgba.crop(crop_box).resize(crop_size, Image.NEAREST))
        full_mask = fit_cover(mask.convert("RGB"), thumb_size)

        label = textwrap.fill(
            f"{row['label']}\nstatus={row['status']} runtime={row['runtime_sec']}s\nrun={Path(run_dir).name}",
            width=32,
        )
        draw.rectangle([0, top, board_width, top + row_height], outline=(230, 230, 230))
        draw_text(draw, (24, top + 18), label)
        board.paste(full_mask, (label_width, top + 20))
        board.paste(crop_mask.convert("RGB"), (label_width + thumb_size[0] + 20, top + 10))
        board.paste(crop_cutout, (label_width + thumb_size[0] + crop_size[0] + 40, top + 10))

    compare_path = BY_INPUT_DIR / f"{input_path.stem}.compare.png"
    compare_path.parent.mkdir(parents=True, exist_ok=True)
    board.save(compare_path)
    return compare_path


def preferred_row(input_rows: list[dict[str, object]]) -> dict[str, object] | None:
    success_rows = [row for row in input_rows if row["status"] == "success"]
    preferred = next((row for row in success_rows if row["variant_slug"] == "balanced_s320_n4"), None)
    if preferred is None:
        preferred = next((row for row in success_rows if row["variant_slug"] == "balanced_s256_n4"), None)
    if preferred is None and success_rows:
        preferred = success_rows[0]
    return preferred


def create_overview_board(rows: list[dict[str, object]]) -> Path | None:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["input"]), []).append(row)

    cards: list[Image.Image] = []
    card_width = 520
    card_padding = 20
    preview_box = (card_width - card_padding * 2, 720)
    for input_name in sorted(grouped):
        compare_path = BY_INPUT_DIR / f"{Path(input_name).stem}.compare.png"
        if not compare_path.exists():
            continue

        preview = Image.open(compare_path).convert("RGB")
        preview.thumbnail(preview_box, Image.LANCZOS)
        chosen = preferred_row(grouped[input_name])
        failed = sum(1 for row in grouped[input_name] if row["status"] != "success")
        note = "No successful run recorded."
        if chosen is not None:
            note = f"Recommended: {chosen['label']}"
        if failed:
            note += f" | failed variants: {failed}"

        card_height = 104 + preview.height + card_padding
        card = Image.new("RGB", (card_width, card_height), (255, 255, 255))
        draw = ImageDraw.Draw(card)
        draw.rounded_rectangle([0, 0, card_width - 1, card_height - 1], radius=18, outline=(220, 220, 220), width=2)
        draw_text(draw, (card_padding, 18), f"{input_name}\n{note}")
        card.paste(preview, ((card_width - preview.width) // 2, 84))
        cards.append(card)

    if not cards:
        return None

    cols = 2
    gap = 20
    padding = 24
    title_height = 72
    row_heights: list[int] = []
    for start in range(0, len(cards), cols):
        row_heights.append(max(card.height for card in cards[start:start + cols]))
    board_width = padding * 2 + cols * card_width + (cols - 1) * gap
    board_height = padding * 2 + title_height + sum(row_heights) + gap * max(0, len(row_heights) - 1)
    board = Image.new("RGB", (board_width, board_height), (248, 248, 246))
    draw = ImageDraw.Draw(board)
    draw_text(
        draw,
        (padding, padding),
        "Fibo-Edit-RMBG edge comparison gallery\nEach card links to a full compare board from experiments/by-input/.",
    )

    y = padding + title_height
    card_index = 0
    for row_height in row_heights:
        x = padding
        for _ in range(cols):
            if card_index >= len(cards):
                break
            card = cards[card_index]
            board.paste(card, (x, y))
            x += card_width + gap
            card_index += 1
        y += row_height + gap

    board.save(OVERVIEW_IMAGE)
    return OVERVIEW_IMAGE


def write_by_input_markdown(input_path: Path, rows: list[dict[str, object]], compare_path: Path | None) -> None:
    rows = sorted(rows, key=lambda row: (row["status"] != "success", row["runtime_sec"]))
    lines = [f"# {input_path.name}", ""]
    if compare_path is not None:
        lines.extend([f"![comparison](./{compare_path.name})", ""])
    lines.extend(
        [
            "| Variant | Status | Runtime (s) | Run | Notes |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for row in rows:
        run_dir = Path(str(row["run_dir"])).name
        run_link = f"[{run_dir}](../runs/{run_dir}/README.md)"
        notes = str(row["notes"]).replace("\n", " ")
        lines.append(
            f"| {row['label']} | {row['status']} | {row['runtime_sec']} | {run_link} | {notes} |"
        )

    best_hint = next((row for row in rows if row["variant_slug"] == "balanced_s320_n4" and row["status"] == "success"), None)
    if best_hint is None:
        best_hint = next((row for row in rows if row["variant_slug"] == "balanced_s256_n4" and row["status"] == "success"), None)
    if best_hint is not None:
        lines.extend(["", f"Recommended first check: `{best_hint['label']}`"])

    write_text(BY_INPUT_DIR / f"{input_path.stem}.md", "\n".join(lines) + "\n")


def write_experiments_readme(rows: list[dict[str, object]]) -> None:
    input_names = sorted({str(row["input"]) for row in rows})
    success_rows = [row for row in rows if row["status"] == "success"]
    failed_rows = [row for row in rows if row["status"] == "failed"]

    recommended = []
    for input_name in input_names:
        candidates = [row for row in success_rows if row["input"] == input_name]
        preferred = next((row for row in candidates if row["variant_slug"] == "balanced_s320_n4"), None)
        if preferred is None:
            preferred = next((row for row in candidates if row["variant_slug"] == "balanced_s256_n4"), None)
        if preferred is not None:
            recommended.append((input_name, preferred["label"], Path(str(preferred["run_dir"])).name))

    lines = [
        "# Edge Experiments",
        "",
        "Parameter sweep focused on reducing jagged cutout edges on the current Windows + RTX 3060 6GB environment.",
        "",
        f"- Representative rows: `{len(rows)}` (`{len(success_rows)}` success / `{len(failed_rows)}` failed)",
        f"- Raw run folders: [`runs/`](./runs/)",
        f"- CSV summary: [`summary.csv`](./summary.csv)",
        "",
        "## Current Recommendation",
        "",
    ]
    if recommended:
        for input_name, label, run_dir in recommended:
            lines.append(f"- `{input_name}`: start by reviewing `{label}` in [`{run_dir}`](./runs/{run_dir}/README.md)")
    else:
        lines.append("- No successful runs recorded yet.")

    lines.extend(
        [
            "",
            "## Overview Gallery",
            "",
            '<img alt="Edge experiment overview" src="./overview.png" width="1200" />',
            "",
            "## What To Look For",
            "",
            "- `balanced` is the main anti-jaggy setting. It keeps edges smoother than `hard` without adding as much halo as `soft`.",
            "- `hard` is included as a failure-mode reference. It tends to turn curved edges into visible staircase pixels.",
            "- `soft` can hide jaggies, but it also fattens boundaries and can leave a blurred edge halo.",
            "- `320 / 4 steps` produced the nicest edges on three inputs, but `kling-generate-square.png` had to fall back to `256 / 4 steps` because the higher-cost variant failed on this machine.",
            "",
            "## Per Input",
            "",
        ]
    )
    for input_name in input_names:
        stem = Path(input_name).stem
        lines.append(f"- [`{input_name}`](./by-input/{stem}.md)")

    lines.extend(
        [
            "",
            "## Embedded Compare Boards",
            "",
        ]
    )
    for input_name in input_names:
        stem = Path(input_name).stem
        lines.extend(
            [
                f"### {input_name}",
                "",
                f"[Open notes and run table](./by-input/{stem}.md)",
                "",
                f'<img alt="{input_name} edge comparison" src="./by-input/{stem}.compare.png" width="1200" />',
                "",
            ]
        )

    lines.extend(
        [
            "",
            "## Failure Notes",
            "",
            "- `balanced / 320 / 4 steps` can trip `MemoryError` on the heaviest input in this 6GB GPU + Windows setup.",
            "- One `hard / 256 / 4 steps / thr128` retry ended in a native crash during pipeline load; the run folder is kept for reference.",
            "- Raw retries are preserved under [`runs/`](./runs/), while [`summary.csv`](./summary.csv) and the `by-input/` pages keep one representative row per input x variant.",
        ]
    )

    write_text(EXPERIMENTS_README, "\n".join(lines) + "\n")


def update_compare_paths(rows: list[dict[str, object]]) -> None:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["input"]), []).append(row)

    for input_name, input_rows in grouped.items():
        input_path = EXAMPLE_DIR / input_name
        compare_path = create_input_compare_board(input_path, input_rows)
        if compare_path is not None:
            for row in input_rows:
                row["compare_path"] = compare_path.relative_to(REPO_ROOT).as_posix()
                run_json_path = REPO_ROOT / str(row["run_dir"]) / "run.json"
                data = json.loads(run_json_path.read_text(encoding="utf-8"))
                data["compare_path"] = row["compare_path"]
                write_text(run_json_path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        write_by_input_markdown(input_path, input_rows, compare_path)
    create_overview_board(rows)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ensure_dirs()
    if args.postprocess_only:
        raw_rows = load_rows()
        if not raw_rows:
            raise FileNotFoundError(f"No run.json files found in {RUNS_DIR}")
        rows = canonical_rows(raw_rows)
        update_compare_paths(rows)
        write_summary_csv(rows)
        write_experiments_readme(rows)
        return 0

    commit_hash = git_commit()
    inputs = select_inputs(args.inputs)
    variants = select_variants(args.variants)
    completed = existing_success_keys() if args.resume else set()
    for input_path in inputs:
        for variant in variants:
            if (input_path.name, variant.slug) in completed:
                print(f"SKIP {input_path.name} :: {variant.label}", flush=True)
                continue
            print(f"RUN {input_path.name} :: {variant.label}", flush=True)
            row = run_variant(input_path, variant, commit_hash)
            print(f"EXIT {row['status']} :: {row['run_id']}", flush=True)

    rows = canonical_rows(load_rows())
    update_compare_paths(rows)
    write_summary_csv(rows)
    write_experiments_readme(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
