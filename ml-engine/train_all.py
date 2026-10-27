"""Train all 4 local neural models and save checkpoints to ml-engine/models/."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import sys

# Setup paths
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "backend"))
sys.path.insert(0, str(root / "ml-engine"))

from datasets.dataset_loader import DatasetLoader
from training.trainer import ModelTrainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("intentify.train_all")


def main():
    trainer = ModelTrainer(output_dir="ml-engine/models")

    logger.info("Loading datasets...")
    intent_data = DatasetLoader.load("ml-engine/datasets/intent_train.json")
    domain_data = DatasetLoader.load("ml-engine/datasets/domain_train.json")
    role_data = DatasetLoader.load("ml-engine/datasets/role_train.json")
    req_data = DatasetLoader.load("ml-engine/datasets/requirements_train.json")

    logger.info("Training Intent Classifier on %d samples...", len(intent_data))
    intent_metrics = trainer.train_intent_classifier(intent_data, epochs=8, batch_size=64, lr=0.01)
    logger.info("Intent metrics: %s", intent_metrics)

    logger.info("Training Domain Classifier on %d samples...", len(domain_data))
    domain_metrics = trainer.train_domain_classifier(domain_data, epochs=8, batch_size=64, lr=0.01)
    logger.info("Domain metrics: %s", domain_metrics)

    logger.info("Training Role Classifier on %d samples...", len(role_data))
    role_metrics = trainer.train_role_classifier(role_data, epochs=8, batch_size=64, lr=0.01)
    logger.info("Role metrics: %s", role_metrics)

    logger.info("Training Quality Scorer on %d samples...", len(req_data))
    qual_metrics = trainer.train_quality_scorer(req_data, epochs=8, batch_size=64, lr=0.01)
    logger.info("Quality metrics: %s", qual_metrics)

    logger.info("All 4 models successfully trained and checkpoints saved to ml-engine/models/")


if __name__ == "__main__":
    main()
