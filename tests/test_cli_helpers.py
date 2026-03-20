from pathlib import Path

from PIL import Image

from fibo_edit_rmbg_sandbox.cli import (
    default_mask_path,
    default_output_path,
    postprocess_alpha,
    resize_for_inference,
)


def test_default_output_path_uses_rmbg_suffix() -> None:
    input_path = Path("example/sample.png")
    assert default_output_path(input_path) == Path("example/sample.rmbg.png")


def test_default_mask_path_uses_mask_suffix() -> None:
    output_path = Path("outputs/sample.rmbg.png")
    assert default_mask_path(output_path) == Path("outputs/sample.rmbg.mask.png")


def test_resize_for_inference_respects_max_side_and_multiple() -> None:
    image = Image.new("RGB", (2048, 1024), "white")
    resized = resize_for_inference(image, max_side=320)
    assert resized.size == (320, 160)


def test_resize_for_inference_rounds_up_small_images_to_multiple() -> None:
    image = Image.new("RGB", (300, 300), "white")
    resized = resize_for_inference(image, max_side=768)
    assert resized.size == (320, 320)


def test_postprocess_alpha_hard_thresholds_to_binary() -> None:
    mask = Image.new("L", (2, 2))
    mask.putdata([0, 100, 200, 255])
    alpha = postprocess_alpha(mask, (2, 2), mask_style="hard", alpha_threshold=128)
    assert list(alpha.getdata()) == [0, 0, 255, 255]


def test_postprocess_alpha_balanced_preserves_grayscale() -> None:
    mask = Image.new("L", (2, 2))
    mask.putdata([0, 96, 180, 255])
    alpha = postprocess_alpha(mask, (2, 2), mask_style="balanced", alpha_threshold=None)
    values = list(alpha.getdata())
    assert values[0] == 0
    assert values[-1] == 255
    assert 0 < values[1] < 255
    assert 0 < values[2] < 255
