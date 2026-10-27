"""ModelEvaluator – comprehensive metrics evaluation for classification and regression models."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger("intentify.ml.evaluation")


class ModelEvaluator:
    """Computes rigorous evaluation metrics: Accuracy, Precision, Recall, Macro-F1, MSE, MAE, R2."""

    @staticmethod
    def compute_classification_metrics(
        y_true: list[str] | np.ndarray,
        y_pred: list[str] | np.ndarray,
    ) -> dict[str, float]:
        """Compute multiclass accuracy, macro-precision, macro-recall, and macro-F1."""
        if len(y_true) == 0 or len(y_pred) == 0:
            return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}

        y_true_list = [str(x) for x in y_true]
        y_pred_list = [str(x) for x in y_pred]

        classes = sorted(list(set(y_true_list) | set(y_pred_list)))
        class_to_idx = {c: i for i, c in enumerate(classes)}

        n_classes = len(classes)
        confusion = np.zeros((n_classes, n_classes), dtype=np.int64)

        for yt, yp in zip(y_true_list, y_pred_list):
            confusion[class_to_idx[yt], class_to_idx[yp]] += 1

        # Accuracy
        correct = np.trace(confusion)
        total = np.sum(confusion)
        accuracy = float(correct / total) if total > 0 else 0.0

        precisions = []
        recalls = []
        f1s = []

        for c_idx in range(n_classes):
            tp = confusion[c_idx, c_idx]
            fp = np.sum(confusion[:, c_idx]) - tp
            fn = np.sum(confusion[c_idx, :]) - tp

            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2.0 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

            precisions.append(prec)
            recalls.append(rec)
            f1s.append(f1)

        macro_precision = float(np.mean(precisions))
        macro_recall = float(np.mean(recalls))
        macro_f1 = float(np.mean(f1s))

        return {
            "accuracy": round(accuracy, 4),
            "macro_precision": round(macro_precision, 4),
            "macro_recall": round(macro_recall, 4),
            "macro_f1": round(macro_f1, 4),
            "num_samples": total,
            "num_classes": n_classes,
        }

    @staticmethod
    def compute_regression_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> dict[str, float]:
        """Compute MSE, RMSE, MAE, and R-squared for continuous regression."""
        if len(y_true) == 0 or len(y_pred) == 0:
            return {"mse": 0.0, "rmse": 0.0, "mae": 0.0, "r2": 0.0}

        diff = y_pred - y_true
        mse = float(np.mean(diff ** 2))
        rmse = float(np.sqrt(mse))
        mae = float(np.mean(np.abs(diff)))

        # R-squared
        ss_res = np.sum(diff ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

        return {
            "mse": round(mse, 5),
            "rmse": round(rmse, 5),
            "mae": round(mae, 5),
            "r2": round(r2, 4),
        }
