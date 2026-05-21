import numpy as np
import torch
import torch.nn.functional as F


class GradCAM:
    """Grad-CAM for torchvision EfficientNet-style models."""

    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.activations: torch.Tensor | None = None
        self.gradients: torch.Tensor | None = None
        self._handles: list = []

        def forward_hook(_module, _input, output):
            self.activations = output.detach()

        def backward_hook(_module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        self._handles.append(target_layer.register_forward_hook(forward_hook))
        self._handles.append(
            target_layer.register_full_backward_hook(backward_hook)
        )

    def remove_hooks(self) -> None:
        for h in self._handles:
            h.remove()
        self._handles.clear()

    def generate(
        self, input_tensor: torch.Tensor, class_idx: int
    ) -> np.ndarray:
        self.model.zero_grad(set_to_none=True)
        logits = self.model(input_tensor)
        score = logits[0, class_idx]
        score.backward()

        if self.gradients is None or self.activations is None:
            raise RuntimeError("Grad-CAM hooks did not capture tensors")

        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(
            cam,
            size=input_tensor.shape[2:],
            mode="bilinear",
            align_corners=False,
        )
        cam = cam.squeeze().cpu().numpy()
        return cam
