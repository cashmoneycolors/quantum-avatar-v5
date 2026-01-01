from __future__ import annotations

import os

try:
    from diffusers import StableDiffusionPipeline  # type: ignore
except Exception:  # pragma: no cover
    StableDiffusionPipeline = None

try:
    import torch  # type: ignore
except Exception:  # pragma: no cover
    torch = None


class ImageGenerator:
    def __init__(self, model_id: str = "CompVis/stable-diffusion-v1-4"):
        self.model_id = model_id
        self.pipe = None
        self.device = "cpu"

        if (
            torch is not None
            and hasattr(torch, "cuda")
            and torch.cuda.is_available()
        ):
            self.device = "cuda"

    def _ensure_loaded(self) -> bool:
        if self.pipe is not None:
            return True
        if StableDiffusionPipeline is None or torch is None:
            return False

        if os.getenv("HF_HUB_OFFLINE") in {"1", "true", "TRUE"}:
            return False
        if os.getenv("TRANSFORMERS_OFFLINE") in {"1", "true", "TRUE"}:
            return False

        try:
            self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id)
            self.pipe.to(self.device)
            return True
        except Exception:
            self.pipe = None
            return False

    def generate_image(self, prompt: str):
        if not self._ensure_loaded():
            return None
        assert self.pipe is not None
        return self.pipe(prompt).images[0]

    def generate_fleischtheke_poster(self, freshness_score: float, theme: str):
        prompt = (
            f"Butcher counter poster, freshness {freshness_score:.2f}, "
            f"theme: {theme}"
        )
        return self.generate_image(prompt)
