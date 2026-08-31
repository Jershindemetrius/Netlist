"""metrics.py: Standard Metric Formulations for Detection, Connectivity, and Graphs."""

from typing import Dict, Any, List
import numpy as np
from src.common.schemas import EvaluationMetrics


def compute_f1(precision: float, recall: float) -> float:
    """Computes F1 score with epsilon protection."""
    if precision + recall < 1e-7:
        return 0.0
    return 2.0 * (precision * recall) / (precision + recall)


def summarize_evaluation_metrics(metrics_list: List[EvaluationMetrics]) -> Dict[str, float]:
    """Averages metrics across a dataset batch."""
    if not metrics_list:
        return {}

    return {
        "mean_ged_score": float(np.mean([m.ged_score for m in metrics_list])),
        "mean_comp_precision": float(np.mean([m.component_precision for m in metrics_list])),
        "mean_comp_recall": float(np.mean([m.component_recall for m in metrics_list])),
        "mean_comp_f1": float(np.mean([m.component_f1 for m in metrics_list])),
        "mean_net_precision": float(np.mean([m.net_precision for m in metrics_list])),
        "mean_net_recall": float(np.mean([m.net_recall for m in metrics_list])),
        "mean_net_f1": float(np.mean([m.net_f1 for m in metrics_list])),
        "total_node_insertions": int(sum([m.node_insertions for m in metrics_list])),
        "total_node_deletions": int(sum([m.node_deletions for m in metrics_list])),
        "total_node_mismatches": int(sum([m.node_mismatches for m in metrics_list])),
        "total_edge_insertions": int(sum([m.edge_insertions for m in metrics_list])),
        "total_edge_deletions": int(sum([m.edge_deletions for m in metrics_list]))
    }
