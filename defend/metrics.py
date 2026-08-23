"""Evaluation Metrics & Benchmark Suite for AI Defense Grid.

Computes Precision, Recall, F1, PR-AUC, ROC-AUC, False Positive Rate (FPR),
and latency percentiles under production payment constraints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def compute_defense_metrics(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    threshold: float = 0.50,
    latencies_ms: Optional[List[float]] = None,
    attack_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Compute comprehensive classification and operational performance metrics.

    Args:
        y_true: Ground truth binary labels (0=legit, 1=fraud).
        y_scores: Continuous model predicted probabilities [0.0, 1.0].
        threshold: Decision cutoff threshold for positive classification.
        latencies_ms: Optional list of per-transaction evaluation latencies.
        attack_types: Optional list of ground truth attack IDs for per-vector breakdown.

    Returns:
        Dictionary of performance metrics.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_scores = np.asarray(y_scores, dtype=float)
    y_pred = (y_scores >= threshold).astype(int)

    # Basic classification metrics
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    # ROC-AUC & PR-AUC
    try:
        roc_auc = float(roc_auc_score(y_true, y_scores))
    except Exception:
        roc_auc = 0.5
    try:
        pr_auc = float(average_precision_score(y_true, y_scores))
    except Exception:
        pr_auc = 0.0

    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = float(fp / max(1, (fp + tn)))
    fnr = float(fn / max(1, (fn + tp)))

    metrics: Dict[str, Any] = {
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
        "threshold": threshold,
        "sample_count": len(y_true),
    }

    # Operational latency benchmarks
    if latencies_ms and len(latencies_ms) > 0:
        lats = sorted(latencies_ms)
        metrics["latency_benchmarks"] = {
            "p50_ms": round(float(np.percentile(lats, 50)), 2),
            "p95_ms": round(float(np.percentile(lats, 95)), 2),
            "p99_ms": round(float(np.percentile(lats, 99)), 2),
            "mean_ms": round(float(np.mean(lats)), 2),
            "max_ms": round(float(np.max(lats)), 2),
        }

    # Per-Attack Vector Recall Breakdown
    if attack_types is not None and len(attack_types) == len(y_true):
        df_eval = pd.DataFrame({
            "true": y_true,
            "pred": y_pred,
            "score": y_scores,
            "attack": attack_types,
        })
        fraud_subset = df_eval[df_eval["true"] == 1]
        per_attack = {}
        for atk, grp in fraud_subset.groupby("attack"):
            if str(atk) and str(atk) != "None":
                atk_rec = float(grp["pred"].mean())
                per_attack[str(atk)] = {
                    "count": len(grp),
                    "recall": round(atk_rec, 4),
                    "mean_score": round(float(grp["score"].mean()), 4),
                }
        metrics["per_attack_recall"] = per_attack

    return metrics
