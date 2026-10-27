"""Neural Network Model Architectures supporting both PyTorch and high-performance NumPy execution."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger("intentify.ml.models")

# Optional PyTorch integration
try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


# ─────────────────────────────────────────────────────────────────────────────
# NumPy Autonomous Neural Engine (Zero external heavy dependencies)
# ─────────────────────────────────────────────────────────────────────────────

class NumpyDenseLayer:
    """Fully-connected linear layer with He initialization and Adam optimizer updates."""

    def __init__(self, in_features: int, out_features: int) -> None:
        # He (Kaiming) initialization for ReLU activations
        limit = np.sqrt(2.0 / in_features)
        self.weights = np.random.randn(in_features, out_features).astype(np.float32) * limit
        self.bias = np.zeros((1, out_features), dtype=np.float32)

        # Gradients
        self.grad_w = np.zeros_like(self.weights)
        self.grad_b = np.zeros_like(self.bias)
        # Adam moments
        self.m_w = np.zeros_like(self.weights)
        self.v_w = np.zeros_like(self.weights)
        self.m_b = np.zeros_like(self.bias)
        self.v_b = np.zeros_like(self.bias)
        self.t = 0
        self._input: np.ndarray | None = None

    def forward(self, x: np.ndarray) -> np.ndarray:
        self._input = x
        return np.dot(x, self.weights) + self.bias

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        assert self._input is not None
        self.grad_w = np.dot(self._input.T, grad_output)
        self.grad_b = np.sum(grad_output, axis=0, keepdims=True)
        return np.dot(grad_output, self.weights.T)

    def step(self, lr: float = 0.005) -> None:
        self.t += 1
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        self.m_w = beta1 * self.m_w + (1.0 - beta1) * self.grad_w
        self.v_w = beta2 * self.v_w + (1.0 - beta2) * (self.grad_w ** 2)
        m_hat_w = self.m_w / (1.0 - beta1 ** self.t)
        v_hat_w = self.v_w / (1.0 - beta2 ** self.t)
        self.weights -= lr * m_hat_w / (np.sqrt(v_hat_w) + eps)

        self.m_b = beta1 * self.m_b + (1.0 - beta1) * self.grad_b
        self.v_b = beta2 * self.v_b + (1.0 - beta2) * (self.grad_b ** 2)
        m_hat_b = self.m_b / (1.0 - beta1 ** self.t)
        v_hat_b = self.v_b / (1.0 - beta2 ** self.t)
        self.bias -= lr * m_hat_b / (np.sqrt(v_hat_b) + eps)


class NumpyMLPClassifier:
    """Multilayer Perceptron for multi-class classification using Softmax & Cross-Entropy."""

    def __init__(self, layer_dims: list[int]) -> None:
        self.layer_dims = layer_dims
        self.layers: list[NumpyDenseLayer] = []
        for i in range(len(layer_dims) - 1):
            self.layers.append(NumpyDenseLayer(layer_dims[i], layer_dims[i + 1]))

    def forward(self, x: np.ndarray) -> np.ndarray:
        out = x
        for i, layer in enumerate(self.layers):
            out = layer.forward(out)
            if i < len(self.layers) - 1:
                # ReLU activation for hidden layers
                out = np.maximum(0, out)
        # Numerical stable Softmax for output layer
        exp_out = np.exp(out - np.max(out, axis=-1, keepdims=True))
        return exp_out / np.sum(exp_out, axis=-1, keepdims=True)

    def train_step(self, x: np.ndarray, y_indices: np.ndarray, lr: float = 0.01) -> float:
        """Execute single forward and backward propagation pass."""
        batch_size = x.shape[0]
        probs = self.forward(x)

        # Cross-Entropy loss
        log_likelihood = -np.log(np.clip(probs[np.arange(batch_size), y_indices], 1e-12, 1.0))
        loss = float(np.mean(log_likelihood))

        # Softmax + CrossEntropy gradient: (p - y) / N
        grad = probs.copy()
        grad[np.arange(batch_size), y_indices] -= 1.0
        grad /= batch_size

        # Backward propagation
        for i in reversed(range(len(self.layers))):
            if i < len(self.layers) - 1:
                # ReLU derivative
                grad = grad * (self.layers[i + 1]._input > 0)
            grad = self.layers[i].backward(grad)
            self.layers[i].step(lr)

        return loss

    def predict(self, x: np.ndarray) -> np.ndarray:
        probs = self.forward(x)
        return np.argmax(probs, axis=-1)

    def save(self, filepath: str | Path) -> None:
        weights_dict = {}
        for idx, layer in enumerate(self.layers):
            weights_dict[f"w_{idx}"] = layer.weights
            weights_dict[f"b_{idx}"] = layer.bias
        np.savez(filepath, **weights_dict)

    def load(self, filepath: str | Path) -> None:
        data = np.load(filepath)
        for idx, layer in enumerate(self.layers):
            layer.weights = data[f"w_{idx}"]
            layer.bias = data[f"b_{idx}"]


class NumpyMLPRegressor:
    """Multilayer Perceptron for continuous multi-output regression using MSE loss."""

    def __init__(self, layer_dims: list[int]) -> None:
        self.layer_dims = layer_dims
        self.layers: list[NumpyDenseLayer] = []
        for i in range(len(layer_dims) - 1):
            self.layers.append(NumpyDenseLayer(layer_dims[i], layer_dims[i + 1]))

    def forward(self, x: np.ndarray) -> np.ndarray:
        out = x
        for i, layer in enumerate(self.layers):
            out = layer.forward(out)
            if i < len(self.layers) - 1:
                out = np.maximum(0, out)
        # Sigmoid output in range [0, 1]
        return 1.0 / (1.0 + np.exp(-np.clip(out, -15.0, 15.0)))

    def train_step(self, x: np.ndarray, y: np.ndarray, lr: float = 0.01) -> float:
        batch_size = x.shape[0]
        preds = self.forward(x)
        loss = float(np.mean((preds - y) ** 2))

        # Sigmoid + MSE gradient
        grad = 2.0 * (preds - y) * preds * (1.0 - preds) / batch_size

        for i in reversed(range(len(self.layers))):
            if i < len(self.layers) - 1:
                grad = grad * (self.layers[i + 1]._input > 0)
            grad = self.layers[i].backward(grad)
            self.layers[i].step(lr)

        return loss

    def save(self, filepath: str | Path) -> None:
        weights_dict = {}
        for idx, layer in enumerate(self.layers):
            weights_dict[f"w_{idx}"] = layer.weights
            weights_dict[f"b_{idx}"] = layer.bias
        np.savez(filepath, **weights_dict)

    def load(self, filepath: str | Path) -> None:
        data = np.load(filepath)
        for idx, layer in enumerate(self.layers):
            layer.weights = data[f"w_{idx}"]
            layer.bias = data[f"b_{idx}"]


# ─────────────────────────────────────────────────────────────────────────────
# Factory model classes for Intent, Domain, Role, and Quality
# ─────────────────────────────────────────────────────────────────────────────

def create_intent_model(input_dim: int = 384, num_classes: int = 13) -> NumpyMLPClassifier:
    """Factory for Intent Classifier Neural Network (384 -> 256 -> 128 -> 13)."""
    return NumpyMLPClassifier([input_dim, 256, 128, num_classes])


def create_domain_model(input_dim: int = 384, num_classes: int = 88) -> NumpyMLPClassifier:
    """Factory for Domain Classifier Neural Network (384 -> 512 -> 256 -> 88)."""
    return NumpyMLPClassifier([input_dim, 512, 256, num_classes])


def create_role_model(input_dim: int = 384, num_classes: int = 121) -> NumpyMLPClassifier:
    """Factory for Role Classifier Neural Network (384 -> 512 -> 256 -> 121)."""
    return NumpyMLPClassifier([input_dim, 512, 256, num_classes])


def create_quality_model(input_dim: int = 384) -> NumpyMLPRegressor:
    """Factory for Quality Scorer Neural Network (384 -> 256 -> 6)."""
    return NumpyMLPRegressor([input_dim, 256, 6])


def create_audience_model(input_dim: int = 384, num_classes: int = 8) -> NumpyMLPClassifier:
    """Factory for Audience Classifier Neural Network (384 -> 256 -> 8)."""
    return NumpyMLPClassifier([input_dim, 256, num_classes])


def create_deliverable_model(input_dim: int = 384, num_classes: int = 10) -> NumpyMLPClassifier:
    """Factory for Deliverable Classifier Neural Network (384 -> 256 -> 10)."""
    return NumpyMLPClassifier([input_dim, 256, num_classes])


def create_ranker_model(input_dim: int = 384) -> NumpyMLPRegressor:
    """Factory for Knowledge Retrieval Ranker Neural Network (384 -> 128 -> 1)."""
    return NumpyMLPRegressor([input_dim, 128, 1])


# ─────────────────────────────────────────────────────────────────────────────
# Optional PyTorch Module Definitions (available when PyTorch is installed)
# ─────────────────────────────────────────────────────────────────────────────

if HAS_TORCH:
    class PyTorchIntentClassifier(nn.Module):
        def __init__(self, input_dim: int = 384, num_classes: int = 13, dropout: float = 0.2) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 256),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(256, 128),
                nn.ReLU(),
                nn.Linear(128, num_classes),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)

    class PyTorchDomainClassifier(nn.Module):
        def __init__(self, input_dim: int = 384, num_classes: int = 88, dropout: float = 0.2) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 512),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(512, num_classes),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)

    class PyTorchRoleClassifier(nn.Module):
        def __init__(self, input_dim: int = 384, num_classes: int = 121, dropout: float = 0.2) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 512),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(512, num_classes),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)

    class PyTorchQualityScorer(nn.Module):
        def __init__(self, input_dim: int = 384, dropout: float = 0.1) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 256),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(256, 6),
                nn.Sigmoid(),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)
