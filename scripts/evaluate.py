"""evaluate.py: Graph Edit Distance and Canonical Circuit Graph Evaluator CLI."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
from src.common.logging import logger
from src.graph_assembly.serializer import CircuitSerializer
from src.eval.asc_parser import AscParser
from src.eval.graph_distance import GraphEvaluator
from src.eval.report import EvaluationReporter


def evaluate_prediction(
    prediction_path: str,
    ground_truth_path: str,
    output_report: str = "output/evaluation_report.json"
) -> None:
    """Evaluates prediction JSON graph against ground truth (.asc or .json)."""
    pred_p = Path(prediction_path)
    gt_p = Path(ground_truth_path)

    logger.info(f"Loading prediction from: {pred_p}")
    pred_graph = CircuitSerializer.from_json_file(pred_p)

    logger.info(f"Loading ground truth from: {gt_p}")
    if gt_p.suffix.lower() == ".asc":
        asc_parser = AscParser()
        gt_graph = asc_parser.parse_file(str(gt_p))
    else:
        gt_graph = CircuitSerializer.from_json_file(gt_p)

    evaluator = GraphEvaluator()
    metrics = evaluator.evaluate(pred_graph, gt_graph, run_exact_ged=True)

    EvaluationReporter.print_report(metrics, title=f"EVALUATION: {pred_p.name} vs {gt_p.name}")
    EvaluationReporter.save_report_json(metrics, output_report)
    logger.info(f"Saved evaluation report to: {output_report}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate predicted CircuitGraph against ground truth.")
    parser.add_argument("--prediction", required=True, help="Path to predicted CircuitGraph JSON")
    parser.add_argument("--ground-truth", required=True, help="Path to ground truth .asc or .json")
    parser.add_argument("--output", default="output/evaluation_report.json", help="Path to output JSON report")
    args = parser.parse_args()

    evaluate_prediction(args.prediction, args.ground_truth, args.output)
