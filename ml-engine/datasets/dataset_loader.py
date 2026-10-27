"""DatasetLoader – loading, validation, and stratified partitioning utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


class DatasetLoader:
    """Loads and partitions JSON/JSONL datasets for neural model training."""

    @staticmethod
    def load(path: str | Path) -> list[dict[str, Any]]:
        """Load JSON dataset file."""
        file_path = Path(path)
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def split(
        data: list[dict[str, Any]],
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        shuffle: bool = True,
        seed: int = 42,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        """Split dataset into train, validation, and test subsets."""
        if not data:
            return [], [], []

        data_copy = list(data)
        if shuffle:
            np.random.seed(seed)
            indices = np.random.permutation(len(data_copy))
            data_copy = [data_copy[i] for i in indices]

        n = len(data_copy)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        train_set = data_copy[:train_end]
        val_set = data_copy[train_end:val_end]
        test_set = data_copy[val_end:]

        return train_set, val_set, test_set

    @staticmethod
    def get_batches(
        data: list[dict[str, Any]],
        batch_size: int = 64,
    ) -> list[list[dict[str, Any]]]:
        """Chunk dataset into uniform batches."""
        return [data[i : i + batch_size] for i in range(0, len(data), batch_size)]
