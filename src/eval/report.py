"""report.py: Formatted Evaluation Reporting for Console and JSON Export."""

from pathlib import Path
from typing import Dict, Any, Union
from src.common.schemas import EvaluationMetrics
from src.common.io import save_json, ensure_dir


class EvaluationReporter:
    """Generates formatted console summaries and JSON report artifacts."""

    @staticmethod
    def print_report(metrics: EvaluationMetrics, title: str = "CIRCUIT EVALUATION REPORT") -> None:
        """Prints a human-readable console report."""
        print("=" * 65)
        print(f"             {title}")
        print("=" * 65)
        print(f"Distance Score (GED):  {metrics.ged_score:.2f}")
        print("-" * 65)
        print("Component Metrics:")
        print(f"  Precision:           {metrics.component_precision * 100:.1f}%")
        print(f"  Recall:              {metrics.component_recall * 100:.1f}%")
        print(f"  F1 Score:            {metrics.component_f1 * 100:.1f}%")
        print("-" * 65)
        print("Electrical Net Connectivity:")
        print(f"  Net Precision:       {metrics.net_precision * 100:.1f}%")
        print(f"  Net Recall:          {metrics.net_recall * 100:.1f}%")
        print(f"  Net F1 Score:        {metrics.net_f1 * 100:.1f}%")
        print("-" * 65)
        print("Error Breakdown:")
        print(f"  Node Additions:      {metrics.node_insertions}")
        print(f"  Node Deletions:      {metrics.node_deletions}")
        print(f"  Type Mismatches:     {metrics.node_mismatches}")
        print(f"  Edge Additions:      {metrics.edge_insertions}")
        print(f"  Edge Deletions:      {metrics.edge_deletions}")
        print("=" * 65)

    @staticmethod
    def save_report_json(metrics: EvaluationMetrics, output_path: Union[str, Path]) -> None:
        """Writes evaluation metrics to JSON file."""
        ensure_dir(output_path)
        save_json(metrics.model_dump(), output_path)
