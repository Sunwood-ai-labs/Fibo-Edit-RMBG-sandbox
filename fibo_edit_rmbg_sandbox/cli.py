from __future__ import annotations

import argparse
import os
import types
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageOps

MODEL_ID = "briaai/Fibo-Edit-RMBG"
SOFT_INSTRUCTION = (
    "Generate a detailed grayscale alpha matte. Map the opaque foreground to white "
    "and the background to black. Produce soft, anti-aliased grayscale gradients at "
    "the edges of the subject to represent fine details and transparency."
)
BALANCED_INSTRUCTION = (
    "Generate a clean grayscale alpha matte. Keep the main foreground solid white and "
    "the background black. Preserve only genuine semi-transparent details. Avoid weak "
    "gray halos and unnecessary blur around the subject boundary."
)
HARD_INSTRUCTION = (
    "Generate a crisp foreground cutout mask. Keep the subject solid white and the "
    "background black. Use hard, well-defined edges unless real transparency is clearly "
    "present. Avoid blur, halos, and low-contrast transitions around boundaries."
)
MASK_STYLE_TO_INSTRUCTION = {
    "soft": SOFT_INSTRUCTION,
    "balanced": BALANCED_INSTRUCTION,
    "hard": HARD_INSTRUCTION,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run BRIA Fibo-Edit-RMBG background removal on a local image."
    )
    parser.add_argument("--input", required=True, help="Path to the input image")
    parser.add_argument("--output", help="Path to the RGBA output image")
    parser.add_argument("--mask-output", help="Optional path to save the grayscale mask")
    parser.add_argument(
        "--device",
        default="auto",
        choices=("auto", "cuda", "cpu"),
        help="Execution device. Defaults to auto-detect.",
    )
    parser.add_argument(
        "--dtype",
        default="auto",
        choices=("auto", "bfloat16", "float16", "float32"),
        help="Torch dtype. Defaults to auto selection based on the device.",
    )
    parser.add_argument(
        "--num-inference-steps",
        type=int,
        default=10,
        help="Number of denoising steps. The model card recommends 10.",
    )
    parser.add_argument(
        "--guidance-scale",
        type=float,
        default=1.0,
        help="Classifier-free guidance scale. The model card recommends 1.0.",
    )
    parser.add_argument(
        "--max-side",
        type=int,
        default=768,
        help="Resize the input so the longest edge is at most this value before inference.",
    )
    parser.add_argument(
        "--cpu-offload",
        action="store_true",
        help="Enable model CPU offload to reduce GPU memory pressure.",
    )
    parser.add_argument(
        "--vae-dtype",
        default="auto",
        choices=("auto", "match", "bfloat16", "float16", "float32"),
        help="Optional override for the VAE dtype. Useful if mixed precision fails in VAE ops.",
    )
    parser.add_argument(
        "--mask-style",
        default="balanced",
        choices=("soft", "balanced", "hard"),
        help="Controls edge softness. Use hard for crisper cutout boundaries.",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        help="Optional 0-255 alpha threshold applied after resize. Most useful with --mask-style hard.",
    )
    return parser.parse_args()


def load_token() -> str:
    load_dotenv()

    for key in ("HF_TOKEN", "HUGGINGFACE_HUB_TOKEN"):
        value = os.getenv(key)
        if value:
            return value

    raise RuntimeError(
        "Hugging Face token not found. Set HF_TOKEN in .env or your environment."
    )


def resolve_device(requested: str, torch_module) -> str:
    if requested != "auto":
        return requested

    if torch_module.cuda.is_available():
        return "cuda"

    return "cpu"


def resolve_dtype(requested: str, device: str, torch_module):
    if requested == "float32":
        return torch_module.float32
    if requested == "float16":
        return torch_module.float16
    if requested == "bfloat16":
        return torch_module.bfloat16

    if device == "cuda":
        if hasattr(torch_module.cuda, "is_bf16_supported") and torch_module.cuda.is_bf16_supported():
            return torch_module.bfloat16
        return torch_module.float16

    return torch_module.float32


def resolve_vae_dtype(requested: str, pipeline_dtype, torch_module):
    if requested == "match":
        return pipeline_dtype
    if requested == "float32":
        return torch_module.float32
    if requested == "float16":
        return torch_module.float16
    if requested == "bfloat16":
        return torch_module.bfloat16

    if pipeline_dtype == torch_module.bfloat16:
        return torch_module.float32

    return pipeline_dtype


def round_up_to_multiple(value: int, multiple: int) -> int:
    return max(multiple, ((value + multiple - 1) // multiple) * multiple)


def resize_for_inference(image: Image.Image, max_side: int, multiple: int = 32) -> Image.Image:
    if max_side <= 0:
        return image

    longest_edge = max(image.size)
    if longest_edge <= max_side:
        new_size = image.size
    else:
        scale = max_side / float(longest_edge)
        new_size = tuple(max(1, int(round(side * scale))) for side in image.size)

    if multiple > 1:
        new_size = tuple(round_up_to_multiple(side, multiple) for side in new_size)

    if new_size == image.size:
        return image

    return image.resize(new_size, Image.LANCZOS)


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}.rmbg.png")


def default_mask_path(output_path: Path) -> Path:
    return output_path.with_name(f"{output_path.stem}.mask.png")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def patch_prepare_image_latents_for_vae_dtype(pipe, torch_module) -> None:
    def prepare_image_latents_with_vae_dtype(
        self,
        image,
        batch_size,
        num_channels_latents,
        height,
        width,
        dtype,
        device,
        generator=None,
    ):
        vae_dtype = self.vae.dtype
        image = image.to(device=device, dtype=vae_dtype)

        height = int(height) // self.vae_scale_factor
        width = int(width) // self.vae_scale_factor

        latents_mean = (
            torch_module.tensor(self.vae.config.latents_mean)
            .view(1, self.vae.config.z_dim, 1, 1, 1)
            .to(device, vae_dtype)
        )
        latents_std = 1.0 / (
            torch_module.tensor(self.vae.config.latents_std)
            .view(1, self.vae.config.z_dim, 1, 1, 1)
            .to(device, vae_dtype)
        )

        image_latents_cthw = self.vae.encode(image.unsqueeze(2)).latent_dist.mean
        latents_scaled = [(latent - latents_mean) * latents_std for latent in image_latents_cthw]
        image_latents_cthw = torch_module.concat(latents_scaled, dim=0)
        image_latents_bchw = image_latents_cthw[:, :, 0, :, :]

        image_latent_height, image_latent_width = image_latents_bchw.shape[2:]
        image_latents_bsd = self._pack_latents_no_patch(
            latents=image_latents_bchw,
            batch_size=batch_size,
            num_channels_latents=num_channels_latents,
            height=image_latent_height,
            width=image_latent_width,
        ).to(dtype=dtype)
        image_ids = self._prepare_latent_image_ids(
            batch_size=batch_size,
            height=image_latent_height,
            width=image_latent_width,
            device=device,
            dtype=dtype,
        )
        image_ids[..., 0] = 1
        return image_latents_bsd, image_ids

    pipe.prepare_image_latents = types.MethodType(prepare_image_latents_with_vae_dtype, pipe)


def decode_latents_to_pil(pipe, latents, height: int, width: int, torch_module):
    decode_device = torch_module.device("cpu")
    pipe.vae.to(device=decode_device, dtype=torch_module.float32)

    latents = pipe._unpack_latents_no_patch(latents, height, width, pipe.vae_scale_factor)
    latents = latents.unsqueeze(dim=2).to(device=decode_device, dtype=torch_module.float32)

    latents_mean = (
        torch_module.tensor(pipe.vae.config.latents_mean)
        .view(1, pipe.vae.config.z_dim, 1, 1, 1)
        .to(device=decode_device, dtype=torch_module.float32)
    )
    latents_std = 1.0 / (
        torch_module.tensor(pipe.vae.config.latents_std)
        .view(1, pipe.vae.config.z_dim, 1, 1, 1)
        .to(device=decode_device, dtype=torch_module.float32)
    )

    scaled_latents = latents / latents_std + latents_mean
    decoded_images = []
    with torch_module.inference_mode():
        for scaled_latent in scaled_latents:
            decoded = pipe.vae.decode(scaled_latent.unsqueeze(0), return_dict=False)[0].detach()
            decoded_pil = pipe.image_processor.postprocess(decoded.squeeze(dim=2), output_type="pil")
            if isinstance(decoded_pil, list):
                if len(decoded_pil) != 1:
                    raise RuntimeError(f"Expected one decoded PIL image, got {len(decoded_pil)}")
                decoded_pil = decoded_pil[0]
            decoded_images.append(decoded_pil)

    if len(decoded_images) != 1:
        raise RuntimeError(f"Expected exactly one decoded image, got {len(decoded_images)}")

    return decoded_images[0]


def postprocess_alpha(mask: Image.Image, original_size: tuple[int, int], mask_style: str, alpha_threshold: int | None) -> Image.Image:
    resample = {
        "soft": Image.LANCZOS,
        "balanced": Image.BICUBIC,
        "hard": Image.NEAREST,
    }[mask_style]

    alpha = mask.convert("L").resize(original_size, resample)

    if mask_style in {"balanced", "hard"}:
        cutoff = 1 if mask_style == "balanced" else 2
        alpha = ImageOps.autocontrast(alpha, cutoff=cutoff)

    if alpha_threshold is not None:
        threshold = max(0, min(255, alpha_threshold))
        alpha = alpha.point(lambda value: 255 if value >= threshold else 0)
    elif mask_style == "hard":
        alpha = alpha.point(lambda value: 255 if value >= 160 else 0)

    return alpha


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    output_path = Path(args.output).expanduser().resolve() if args.output else default_output_path(input_path)
    mask_output_path = (
        Path(args.mask_output).expanduser().resolve()
        if args.mask_output
        else default_mask_path(output_path)
    )

    ensure_parent(output_path)
    ensure_parent(mask_output_path)

    token = load_token()

    import torch
    from diffusers import BriaFiboEditPipeline

    device = resolve_device(args.device, torch)
    dtype = resolve_dtype(args.dtype, device, torch)
    vae_dtype = resolve_vae_dtype(args.vae_dtype, dtype, torch)
    instruction = MASK_STYLE_TO_INSTRUCTION[args.mask_style]

    original_image = Image.open(input_path).convert("RGB")
    inference_image = resize_for_inference(original_image, args.max_side)
    inference_width, inference_height = inference_image.size

    print(f"Loading model: {MODEL_ID}")
    print(f"Device: {device}")
    print(f"Dtype: {dtype}")
    print(f"VAE dtype: {vae_dtype}")
    print(f"Mask style: {args.mask_style}")
    print(f"Input size: {original_image.size} -> inference size: {inference_image.size}")

    pipe = BriaFiboEditPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
        token=token,
    )

    if hasattr(pipe, "vae") and pipe.vae is not None and pipe.vae.dtype != vae_dtype:
        pipe.vae.to(dtype=vae_dtype)
        patch_prepare_image_latents_for_vae_dtype(pipe, torch)

    if device == "cuda":
        if args.cpu_offload:
            pipe.enable_model_cpu_offload()
        else:
            pipe.to("cuda")
    else:
        pipe.to("cpu")

    if hasattr(pipe, "enable_attention_slicing"):
        pipe.enable_attention_slicing()

    mask_latents = pipe(
        image=inference_image,
        prompt={"edit_instruction": instruction},
        height=inference_height,
        width=inference_width,
        num_inference_steps=args.num_inference_steps,
        guidance_scale=args.guidance_scale,
        output_type="latent",
    ).images
    mask = decode_latents_to_pil(pipe, mask_latents, inference_height, inference_width, torch)

    alpha = postprocess_alpha(mask, original_image.size, args.mask_style, args.alpha_threshold)
    rgba_image = original_image.copy()
    rgba_image.putalpha(alpha)

    rgba_image.save(output_path)
    alpha.save(mask_output_path)

    print(f"Saved RGBA output: {output_path}")
    print(f"Saved mask output: {mask_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
