"""ModelTrainer – end-to-end training and checkpoint execution for Intent, Domain, Role, and Quality models."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

import numpy as np

from app.ml.embeddings import EmbeddingEngine
from models.model_architectures import (
    create_audience_model,
    create_deliverable_model,
    create_domain_model,
    create_intent_model,
    create_quality_model,
    create_ranker_model,
    create_role_model,
)

logger = logging.getLogger("intentify.ml.trainer")


class ModelTrainer:
    """Executes end-to-end neural training routines across all 4 core models:

    1. Intent Classifier (13 intents)
    2. Domain Classifier (88 catalog domains)
    3. Role Classifier (121 roles)
    4. Quality Scorer (6-dimensional continuous quality regression)
    """

    def __init__(
        self,
        output_dir: str | Path = "ml-engine/models",
        embedding_engine: EmbeddingEngine | None = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._embed = embedding_engine or EmbeddingEngine()

    def train_intent_classifier(
        self,
        dataset: list[dict[str, Any]],
        epochs: int = 5,
        batch_size: int = 64,
        lr: float = 0.02,
    ) -> dict[str, Any]:
        """Train neural Intent Classifier and save checkpoint to models/intent_model/."""
        logger.info("Training Intent Classifier on %d samples (epochs=%d)...", len(dataset), epochs)
        start_time = time.perf_counter()

        # Build label index
        labels = sorted(list({s["label"] for s in dataset}))
        label_to_idx = {l: i for i, l in enumerate(labels)}

        # Encode text to embeddings
        texts = [s["text"] for s in dataset]
        x_mat = self._embed.encode(texts)
        y_vec = np.array([label_to_idx[s["label"]] for s in dataset], dtype=np.int64)

        model = create_intent_model(input_dim=x_mat.shape[1], num_classes=len(labels))

        loss_history = []
        n_samples = len(dataset)
        for ep in range(epochs):
            indices = np.random.permutation(n_samples)
            epoch_losses = []
            for start_idx in range(0, n_samples, batch_size):
                b_idx = indices[start_idx : start_idx + batch_size]
                loss = model.train_step(x_mat[b_idx], y_vec[b_idx], lr=lr)
                epoch_losses.append(loss)
            avg_loss = float(np.mean(epoch_losses))
            loss_history.append(avg_loss)
            logger.debug("Intent Epoch %d/%d - Loss: %.4f", ep + 1, epochs, avg_loss)

        # Compute training accuracy
        preds = model.predict(x_mat)
        acc = float(np.mean(preds == y_vec))

        # Save model checkpoint
        checkpoint_dir = self.output_dir / "intent_model"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        model.save(checkpoint_dir / "weights.npz")

        metrics = {
            "model_type": "IntentClassifierModel",
            "epochs": epochs,
            "final_loss": round(loss_history[-1], 4),
            "train_accuracy": round(acc, 4),
            "num_classes": len(labels),
            "num_samples": n_samples,
            "training_time_sec": round(time.perf_counter() - start_time, 2),
            "classes": labels,
        }
        with open(checkpoint_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        logger.info("Intent Classifier trained successfully (Accuracy: %.2f%%)", acc * 100)
        return metrics

    def train_domain_classifier(
        self,
        dataset: list[dict[str, Any]],
        epochs: int = 5,
        batch_size: int = 64,
        lr: float = 0.02,
    ) -> dict[str, Any]:
        """Train neural Domain Classifier and save checkpoint to models/domain_model/."""
        logger.info("Training Domain Classifier on %d samples (epochs=%d)...", len(dataset), epochs)
        start_time = time.perf_counter()

        domains = sorted(list({s["domain"] for s in dataset}))
        dom_to_idx = {d: i for i, d in enumerate(domains)}

        texts = [s["text"] for s in dataset]
        x_mat = self._embed.encode(texts)
        y_vec = np.array([dom_to_idx[s["domain"]] for s in dataset], dtype=np.int64)

        model = create_domain_model(input_dim=x_mat.shape[1], num_classes=len(domains))

        loss_history = []
        n_samples = len(dataset)
        for ep in range(epochs):
            indices = np.random.permutation(n_samples)
            epoch_losses = []
            for start_idx in range(0, n_samples, batch_size):
                b_idx = indices[start_idx : start_idx + batch_size]
                loss = model.train_step(x_mat[b_idx], y_vec[b_idx], lr=lr)
                epoch_losses.append(loss)
            avg_loss = float(np.mean(epoch_losses))
            loss_history.append(avg_loss)

        preds = model.predict(x_mat)
        acc = float(np.mean(preds == y_vec))

        checkpoint_dir = self.output_dir / "domain_model"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        model.save(checkpoint_dir / "weights.npz")

        metrics = {
            "model_type": "DomainClassifierModel",
            "epochs": epochs,
            "final_loss": round(loss_history[-1], 4),
            "train_accuracy": round(acc, 4),
            "num_classes": len(domains),
            "num_samples": n_samples,
            "training_time_sec": round(time.perf_counter() - start_time, 2),
            "classes": domains,
        }
        with open(checkpoint_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        logger.info("Domain Classifier trained successfully (Accuracy: %.2f%%)", acc * 100)
        return metrics

    def train_role_classifier(
        self,
        dataset: list[dict[str, Any]],
        epochs: int = 5,
        batch_size: int = 64,
        lr: float = 0.02,
    ) -> dict[str, Any]:
        """Train neural Role Classifier and save checkpoint to models/role_model/."""
        logger.info("Training Role Classifier on %d samples (epochs=%d)...", len(dataset), epochs)
        start_time = time.perf_counter()

        roles = sorted(list({s["role"] for s in dataset}))
        role_to_idx = {r: i for i, r in enumerate(roles)}

        texts = [s["text"] for s in dataset]
        x_mat = self._embed.encode(texts)
        y_vec = np.array([role_to_idx[s["role"]] for s in dataset], dtype=np.int64)

        model = create_role_model(input_dim=x_mat.shape[1], num_classes=len(roles))

        loss_history = []
        n_samples = len(dataset)
        for ep in range(epochs):
            indices = np.random.permutation(n_samples)
            epoch_losses = []
            for start_idx in range(0, n_samples, batch_size):
                b_idx = indices[start_idx : start_idx + batch_size]
                loss = model.train_step(x_mat[b_idx], y_vec[b_idx], lr=lr)
                epoch_losses.append(loss)
            avg_loss = float(np.mean(epoch_losses))
            loss_history.append(avg_loss)

        preds = model.predict(x_mat)
        acc = float(np.mean(preds == y_vec))

        checkpoint_dir = self.output_dir / "role_model"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        model.save(checkpoint_dir / "weights.npz")

        metrics = {
            "model_type": "RoleClassifierModel",
            "epochs": epochs,
            "final_loss": round(loss_history[-1], 4),
            "train_accuracy": round(acc, 4),
            "num_classes": len(roles),
            "num_samples": n_samples,
            "training_time_sec": round(time.perf_counter() - start_time, 2),
            "classes": roles,
        }
        with open(checkpoint_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        logger.info("Role Classifier trained successfully (Accuracy: %.2f%%)", acc * 100)
        return metrics

    def train_quality_scorer(
        self,
        dataset: list[dict[str, Any]],
        epochs: int = 5,
        batch_size: int = 64,
        lr: float = 0.02,
    ) -> dict[str, Any]:
        """Train neural Quality Scorer regression model and save checkpoint to models/quality_model/."""
        logger.info("Training Quality Scorer regression on %d samples (epochs=%d)...", len(dataset), epochs)
        start_time = time.perf_counter()

        texts = [s["text"] for s in dataset]
        x_mat = self._embed.encode(texts)

        # Target 6-dimensional continuous scores normalized [0, 1]
        n_samples = len(dataset)
        y_mat = np.zeros((n_samples, 6), dtype=np.float32)
        for i, s in enumerate(dataset):
            # Synthetic quality ground truth based on prompt features
            t_len = len(s["text"].split())
            has_constraints = 1.0 if s.get("constraints") else 0.5
            y_mat[i, 0] = min(1.0, max(0.4, t_len / 40.0))  # clarity
            y_mat[i, 1] = 0.9 if s.get("deadline") else 0.6  # specificity
            y_mat[i, 2] = 0.95 if s.get("location") else 0.7 # context
            y_mat[i, 3] = has_constraints                   # constraints
            y_mat[i, 4] = 0.95 if s.get("format") else 0.65  # output format
            y_mat[i, 5] = 0.85                               # ambiguity handling

        model = create_quality_model(input_dim=x_mat.shape[1])

        loss_history = []
        for ep in range(epochs):
            indices = np.random.permutation(n_samples)
            epoch_losses = []
            for start_idx in range(0, n_samples, batch_size):
                b_idx = indices[start_idx : start_idx + batch_size]
                loss = model.train_step(x_mat[b_idx], y_mat[b_idx], lr=lr)
                epoch_losses.append(loss)
            avg_loss = float(np.mean(epoch_losses))
            loss_history.append(avg_loss)

        # Compute Mean Absolute Error
        preds = model.forward(x_mat)
        mae = float(np.mean(np.abs(preds - y_mat)))

        checkpoint_dir = self.output_dir / "quality_model"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        model.save(checkpoint_dir / "weights.npz")

        metrics = {
            "model_type": "QualityScorerModel",
            "epochs": epochs,
            "final_loss_mse": round(loss_history[-1], 5),
            "train_mae": round(mae, 4),
            "num_outputs": 6,
            "num_samples": n_samples,
            "training_time_sec": round(time.perf_counter() - start_time, 2),
        }
        with open(checkpoint_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        logger.info("Quality Scorer trained successfully (MAE: %.4f)", mae)
        return metrics

    def train_audience_classifier(
        self,
        dataset: list[dict[str, Any]],
        epochs: int = 5,
        batch_size: int = 64,
        lr: float = 0.02,
    ) -> dict[str, Any]:
        """Train neural Audience Classifier and save checkpoint to models/audience_model/."""
        logger.info("Training Audience Classifier on %d samples (epochs=%d)...", len(dataset), epochs)
        start_time = time.perf_counter()

        labels = sorted(list({s.get("audience", s.get("label", "General Stakeholders")) for s in dataset}))
        label_to_idx = {l: i for i, l in enumerate(labels)}

        texts = [s["text"] for s in dataset]
        x_mat = self._embed.encode(texts)
        y_vec = np.array([label_to_idx[s.get("audience", s.get("label", "General Stakeholders"))] for s in dataset], dtype=np.int64)

        model = create_audience_model(input_dim=x_mat.shape[1], num_classes=len(labels))

        loss_history = []
        n_samples = len(dataset)
        for ep in range(epochs):
            indices = np.random.permutation(n_samples)
            epoch_losses = []
            for start_idx in range(0, n_samples, batch_size):
                b_idx = indices[start_idx : start_idx + batch_size]
                loss = model.train_step(x_mat[b_idx], y_vec[b_idx], lr=lr)
                epoch_losses.append(loss)
            avg_loss = float(np.mean(epoch_losses))
            loss_history.append(avg_loss)

        preds = model.predict(x_mat)
        acc = float(np.mean(preds == y_vec))

        checkpoint_dir = self.output_dir / "audience_model"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        model.save(checkpoint_dir / "weights.npz")

        metrics = {
            "model_name": "audience_classifier",
            "accuracy": round(acc, 4),
            "final_loss": round(loss_history[-1], 4) if loss_history else 0.0,
            "epochs": epochs,
            "num_classes": len(labels),
            "labels": labels,
            "num_samples": n_samples,
            "training_time_sec": round(time.perf_counter() - start_time, 2),
        }
        with open(checkpoint_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        return metrics

    def train_deliverable_classifier(
        self,
        dataset: list[dict[str, Any]],
        epochs: int = 5,
        batch_size: int = 64,
        lr: float = 0.02,
    ) -> dict[str, Any]:
        """Train neural Deliverable Classifier and save checkpoint to models/deliverable_model/."""
        logger.info("Training Deliverable Classifier on %d samples (epochs=%d)...", len(dataset), epochs)
        start_time = time.perf_counter()

        labels = sorted(list({s.get("deliverable", s.get("label", "Standard Deliverable")) for s in dataset}))
        label_to_idx = {l: i for i, l in enumerate(labels)}

        texts = [s["text"] for s in dataset]
        x_mat = self._embed.encode(texts)
        y_vec = np.array([label_to_idx[s.get("deliverable", s.get("label", "Standard Deliverable"))] for s in dataset], dtype=np.int64)

        model = create_deliverable_model(input_dim=x_mat.shape[1], num_classes=len(labels))

        loss_history = []
        n_samples = len(dataset)
        for ep in range(epochs):
            indices = np.random.permutation(n_samples)
            epoch_losses = []
            for start_idx in range(0, n_samples, batch_size):
                b_idx = indices[start_idx : start_idx + batch_size]
                loss = model.train_step(x_mat[b_idx], y_vec[b_idx], lr=lr)
                epoch_losses.append(loss)
            avg_loss = float(np.mean(epoch_losses))
            loss_history.append(avg_loss)

        preds = model.predict(x_mat)
        acc = float(np.mean(preds == y_vec))

        checkpoint_dir = self.output_dir / "deliverable_model"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        model.save(checkpoint_dir / "weights.npz")

        metrics = {
            "model_name": "deliverable_classifier",
            "accuracy": round(acc, 4),
            "final_loss": round(loss_history[-1], 4) if loss_history else 0.0,
            "epochs": epochs,
            "num_classes": len(labels),
            "labels": labels,
            "num_samples": n_samples,
            "training_time_sec": round(time.perf_counter() - start_time, 2),
        }
        with open(checkpoint_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        return metrics

    def train_retrieval_ranker(
        self,
        dataset: list[dict[str, Any]],
        epochs: int = 5,
        batch_size: int = 64,
        lr: float = 0.01,
    ) -> dict[str, Any]:
        """Train neural Knowledge Retrieval Ranker and save checkpoint to models/ranker_model/."""
        logger.info("Training Retrieval Ranker on %d samples (epochs=%d)...", len(dataset), epochs)
        start_time = time.perf_counter()

        texts = [s["text"] for s in dataset]
        x_mat = self._embed.encode(texts)
        scores = np.array([float(s.get("relevance_score", s.get("score", 0.85))) for s in dataset], dtype=np.float32).reshape(-1, 1)

        model = create_ranker_model(input_dim=x_mat.shape[1])

        loss_history = []
        n_samples = len(dataset)
        for ep in range(epochs):
            indices = np.random.permutation(n_samples)
            epoch_losses = []
            for start_idx in range(0, n_samples, batch_size):
                b_idx = indices[start_idx : start_idx + batch_size]
                loss = model.train_step(x_mat[b_idx], scores[b_idx], lr=lr)
                epoch_losses.append(loss)
            avg_loss = float(np.mean(epoch_losses))
            loss_history.append(avg_loss)

        preds = model.predict(x_mat)
        mae = float(np.mean(np.abs(preds - scores)))

        checkpoint_dir = self.output_dir / "ranker_model"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        model.save(checkpoint_dir / "weights.npz")

        metrics = {
            "model_name": "retrieval_ranker",
            "mae": round(mae, 4),
            "final_loss": round(loss_history[-1], 4) if loss_history else 0.0,
            "epochs": epochs,
            "num_samples": n_samples,
            "training_time_sec": round(time.perf_counter() - start_time, 2),
        }
        with open(checkpoint_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        return metrics

    def train_all(self, datasets_dir: str | Path = "ml-engine/datasets") -> dict[str, Any]:
        """Execute full training pipeline for all 4 models."""
        from training.data_generator import SyntheticDataGenerator

        ds_path = Path(datasets_dir)
        gen = SyntheticDataGenerator()

        # Check or generate datasets
        intent_file = ds_path / "intent_train.json"
        if not intent_file.exists():
            gen.generate_all_datasets(output_dir=ds_path)

        with open(intent_file, "r", encoding="utf-8") as f:
            intent_data = json.load(f)
        with open(ds_path / "domain_train.json", "r", encoding="utf-8") as f:
            domain_data = json.load(f)
        with open(ds_path / "role_train.json", "r", encoding="utf-8") as f:
            role_data = json.load(f)
        with open(ds_path / "requirements_train.json", "r", encoding="utf-8") as f:
            req_data = json.load(f)

        logger.info("Starting complete model training pipeline...")
        # Train on high-speed batches
        intent_metrics = self.train_intent_classifier(intent_data[:1000], epochs=3)
        domain_metrics = self.train_domain_classifier(domain_data[:1000], epochs=3)
        role_metrics = self.train_role_classifier(role_data[:1000], epochs=3)
        quality_metrics = self.train_quality_scorer(req_data[:1000], epochs=3)

        return {
            "intent_model": intent_metrics,
            "domain_model": domain_metrics,
            "role_model": role_metrics,
            "quality_model": quality_metrics,
        }
