"""Tests for Step 11: AI Model Training Pipeline across Data Generation, Architectures, Training, and Evaluation."""

import json
from pathlib import Path

import numpy as np
import pytest

from datasets.dataset_loader import DatasetLoader
from evaluation.evaluator import ModelEvaluator
from models.model_architectures import (
    NumpyMLPClassifier,
    NumpyMLPRegressor,
    create_domain_model,
    create_intent_model,
    create_quality_model,
    create_role_model,
)
from training.data_generator import SyntheticDataGenerator
from training.trainer import ModelTrainer


class TestSyntheticDataGenerator:
    """Verifies synthetic dataset generation exceeding the 5000+ samples requirement."""

    def test_generate_intent_dataset_size_and_classes(self):
        generator = SyntheticDataGenerator()
        dataset = generator.generate_intent_dataset(num_samples=5200)

        assert len(dataset) >= 5000
        labels = {s["label"] for s in dataset}
        # All 13 intents must be represented
        assert len(labels) == 13
        assert "create" in labels
        assert "debug" in labels
        assert "plan" in labels
        assert "decide" in labels

    def test_generate_domain_dataset_coverage(self):
        generator = SyntheticDataGenerator()
        dataset = generator.generate_domain_dataset(num_samples=300)

        assert len(dataset) >= 200
        domains = {s["domain"] for s in dataset}
        assert len(domains) >= 30
        assert any("Software" in d for d in domains)

    def test_generate_role_dataset_coverage(self):
        generator = SyntheticDataGenerator()
        dataset = generator.generate_role_dataset(num_samples=300)

        assert len(dataset) >= 200
        roles = {s["role"] for s in dataset}
        assert len(roles) >= 30
        assert any("Engineer" in r or "Architect" in r for r in roles)

    def test_generate_requirements_dataset(self):
        generator = SyntheticDataGenerator()
        dataset = generator.generate_requirements_dataset(num_samples=200)

        assert len(dataset) >= 200
        sample = dataset[0]
        assert "goal" in sample
        assert "audience" in sample
        assert "format" in sample
        assert "budget" in sample
        assert "deadline" in sample
        assert "location" in sample
        assert "constraints" in sample


class TestModelArchitectures:
    """Verifies neural network model shapes, forward passes, and weight serialization."""

    def test_intent_classifier_forward_and_predict(self):
        model = create_intent_model(input_dim=384, num_classes=13)
        dummy_x = np.random.randn(8, 384).astype(np.float32)

        probs = model.forward(dummy_x)
        assert probs.shape == (8, 13)
        # Probabilities sum to 1.0 along class dimension
        assert np.allclose(np.sum(probs, axis=1), 1.0, atol=1e-5)

        preds = model.predict(dummy_x)
        assert preds.shape == (8,)

    def test_domain_classifier_dimensions(self):
        model = create_domain_model(input_dim=384, num_classes=88)
        dummy_x = np.random.randn(4, 384).astype(np.float32)
        probs = model.forward(dummy_x)
        assert probs.shape == (4, 88)

    def test_role_classifier_dimensions(self):
        model = create_role_model(input_dim=384, num_classes=121)
        dummy_x = np.random.randn(4, 384).astype(np.float32)
        probs = model.forward(dummy_x)
        assert probs.shape == (4, 121)

    def test_quality_scorer_regression_bounds(self):
        model = create_quality_model(input_dim=384)
        dummy_x = np.random.randn(6, 384).astype(np.float32)
        preds = model.forward(dummy_x)

        assert preds.shape == (6, 6)
        # Outputs must be strictly bounded in [0, 1]
        assert np.all(preds >= 0.0)
        assert np.all(preds <= 1.0)

    def test_weight_save_and_load(self, tmp_path):
        model = create_intent_model(input_dim=384, num_classes=13)
        weights_file = tmp_path / "test_weights.npz"

        model.save(weights_file)
        assert weights_file.exists()

        new_model = create_intent_model(input_dim=384, num_classes=13)
        new_model.load(weights_file)

        # Check weights match
        assert np.allclose(model.layers[0].weights, new_model.layers[0].weights)


class TestModelTrainer:
    """Verifies training loops and model saving to models/ directory."""

    def test_train_and_save_all_4_models(self, tmp_path):
        trainer = ModelTrainer(output_dir=tmp_path)
        gen = SyntheticDataGenerator()

        # Generate small subsets for fast automated unit test execution
        intent_data = gen.generate_intent_dataset(num_samples=130)
        domain_data = gen.generate_domain_dataset(num_samples=150)
        role_data = gen.generate_role_dataset(num_samples=150)
        req_data = gen.generate_requirements_dataset(num_samples=100)

        # 1. Train Intent Classifier
        intent_metrics = trainer.train_intent_classifier(intent_data, epochs=2, batch_size=32)
        assert intent_metrics["final_loss"] >= 0.0
        assert intent_metrics["num_classes"] == 13
        assert (tmp_path / "intent_model" / "weights.npz").exists()
        assert (tmp_path / "intent_model" / "metadata.json").exists()

        # 2. Train Domain Classifier
        dom_metrics = trainer.train_domain_classifier(domain_data, epochs=2, batch_size=32)
        assert dom_metrics["final_loss"] >= 0.0
        assert (tmp_path / "domain_model" / "weights.npz").exists()
        assert (tmp_path / "domain_model" / "metadata.json").exists()

        # 3. Train Role Classifier
        role_metrics = trainer.train_role_classifier(role_data, epochs=2, batch_size=32)
        assert role_metrics["final_loss"] >= 0.0
        assert (tmp_path / "role_model" / "weights.npz").exists()
        assert (tmp_path / "role_model" / "metadata.json").exists()

        # 4. Train Quality Scorer
        qual_metrics = trainer.train_quality_scorer(req_data, epochs=2, batch_size=32)
        assert qual_metrics["final_loss_mse"] >= 0.0
        assert (tmp_path / "quality_model" / "weights.npz").exists()
        assert (tmp_path / "quality_model" / "metadata.json").exists()


class TestModelEvaluatorAndDatasetLoader:
    """Verifies metrics computation and dataset loading."""

    def test_classification_metrics_perfect(self):
        y_true = ["create", "debug", "plan", "analyze"]
        y_pred = ["create", "debug", "plan", "analyze"]
        metrics = ModelEvaluator.compute_classification_metrics(y_true, y_pred)

        assert metrics["accuracy"] == 1.0
        assert metrics["macro_f1"] == 1.0

    def test_classification_metrics_partial(self):
        y_true = ["create", "debug", "plan", "analyze"]
        y_pred = ["create", "debug", "create", "plan"]
        metrics = ModelEvaluator.compute_classification_metrics(y_true, y_pred)

        assert metrics["accuracy"] == 0.5
        assert metrics["num_samples"] == 4

    def test_regression_metrics(self):
        y_true = np.array([[0.8, 0.9], [0.7, 0.6]], dtype=np.float32)
        y_pred = np.array([[0.85, 0.95], [0.65, 0.55]], dtype=np.float32)
        metrics = ModelEvaluator.compute_regression_metrics(y_true, y_pred)

        assert metrics["mae"] > 0.0
        assert metrics["mse"] > 0.0

    def test_dataset_loader_split(self):
        data = [{"id": i, "val": i * 2} for i in range(100)]
        train, val, test = DatasetLoader.split(data, train_ratio=0.8, val_ratio=0.1)

        assert len(train) == 80
        assert len(val) == 10
        assert len(test) == 10

    def test_dataset_loader_batches(self):
        data = list(range(25))
        batches = DatasetLoader.get_batches(data, batch_size=10)
        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[2]) == 5
