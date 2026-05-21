import base64
import io
from dataclasses import dataclass

import numpy as np
import torch
from PIL import Image

from app.ml.grad_cam import GradCAM
from app.ml.model_loader import bundle
from app.ml.preprocess import load_image_from_bytes, preprocess_pil, tensor_to_heatmap_png_array
from app.services.explanation_service import build_explanation


@dataclass
class InferenceResult:
    diagnosis: str
    confidence: float
    probabilities: list[dict[str, float | str]]
    ai_explanation: str
    grad_cam_png: bytes
    overlay_png: bytes
    model_version: str


def _overlay_cam_on_image(pil_image: Image.Image, cam: np.ndarray, alpha: float = 0.45) -> Image.Image:
    img = pil_image.resize((224, 224)).convert("RGB")
    rgb = np.array(img).astype(np.float32) / 255.0
    heat = tensor_to_heatmap_png_array(cam).astype(np.float32) / 255.0
    # JET-like: red on high activation
    heat_color = np.zeros_like(rgb)
    heat_color[..., 0] = heat[..., 0]
    heat_color[..., 1] = heat[..., 0] * 0.4
    blended = (1 - alpha) * rgb + alpha * heat_color
    blended = (np.clip(blended, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(blended)


def run_inference(image_bytes: bytes) -> InferenceResult:
    if not bundle.is_loaded:
        bundle.load()

    pil = load_image_from_bytes(image_bytes)
    tensor = preprocess_pil(pil).to(bundle.device)

    with torch.no_grad():
        logits = bundle.model(tensor)
        probs = torch.softmax(logits, dim=1)[0]

    class_idx = int(torch.argmax(probs).item())
    confidence = float(probs[class_idx].item())
    diagnosis = bundle.classes[class_idx]

    probabilities = [
        {"label": bundle.classes[i], "confidence": float(probs[i].item())}
        for i in range(len(bundle.classes))
    ]

    grad_cam = GradCAM(bundle.model, bundle.target_layer)
    try:
        cam = grad_cam.generate(tensor, class_idx)
    finally:
        grad_cam.remove_hooks()

    grad_cam_img = Image.fromarray(tensor_to_heatmap_png_array(cam))
    buf_cam = io.BytesIO()
    grad_cam_img.save(buf_cam, format="PNG")

    overlay = _overlay_cam_on_image(pil, cam)
    buf_overlay = io.BytesIO()
    overlay.save(buf_overlay, format="PNG")

    explanation = build_explanation(diagnosis, confidence, probabilities)

    return InferenceResult(
        diagnosis=diagnosis,
        confidence=confidence,
        probabilities=probabilities,
        ai_explanation=explanation,
        grad_cam_png=buf_cam.getvalue(),
        overlay_png=buf_overlay.getvalue(),
        model_version="efficientnet_b0",
    )


def image_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")
