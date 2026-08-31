"""graph_distance.py: Graph Edit Distance (GED) and Fast Canonical Circuit Graph Comparison."""

import time
from typing import Dict, Any, Tuple, Optional, Set
import networkx as nx

from src.common.schemas import CircuitGraph, EvaluationMetrics
from src.graph_assembly.circuit_graph import CircuitGraphManager
from src.graph_assembly.graph_normalizer import GraphNormalizer


class GraphEvaluator:
    """Evaluates predicted CircuitGraphs against ground truth using canonical bipartite comparison and GED."""

    def __init__(
        self,
        type_mismatch_cost: float = 2.0,
        node_insertion_cost: float = 1.5,
        node_deletion_cost: float = 1.5,
        edge_insertion_cost: float = 1.0,
        edge_deletion_cost: float = 1.0,
        exact_ged_max_nodes: int = 25,
        ged_timeout: float = 5.0
    ):
        self.type_mismatch_cost = type_mismatch_cost
        self.node_insertion_cost = node_insertion_cost
        self.node_deletion_cost = node_deletion_cost
        self.edge_insertion_cost = edge_insertion_cost
        self.edge_deletion_cost = edge_deletion_cost
        self.exact_ged_max_nodes = exact_ged_max_nodes
        self.ged_timeout = ged_timeout
        self.normalizer = GraphNormalizer()

    def evaluate(
        self,
        predicted: CircuitGraph,
        ground_truth: CircuitGraph,
        run_exact_ged: bool = False
    ) -> EvaluationMetrics:
        """Compares predicted and ground-truth graphs and outputs detailed error metrics."""
        pred_norm = self.normalizer.normalize(predicted)
        gt_norm = self.normalizer.normalize(ground_truth)

        # 1. Component Level Evaluation
        pred_comps = {c.id: c.type for c in pred_norm.components}
        gt_comps = {c.id: c.type for c in gt_norm.components}

        pred_ids = set(pred_comps.keys())
        gt_ids = set(gt_comps.keys())

        matched_ids = pred_ids.intersection(gt_ids)
        node_insertions = len(pred_ids - gt_ids)
        node_deletions = len(gt_ids - pred_ids)

        node_mismatches = 0
        correct_type_nodes = 0
        for cid in matched_ids:
            if pred_comps[cid] == gt_comps[cid]:
                correct_type_nodes += 1
            else:
                node_mismatches += 1

        comp_precision = correct_type_nodes / max(1, len(pred_comps))
        comp_recall = correct_type_nodes / max(1, len(gt_comps))
        comp_f1 = (2 * comp_precision * comp_recall) / max(1e-6, comp_precision + comp_recall)

        # 2. Net Level Evaluation
        # Represent each net as a sorted frozenset of terminal references
        pred_net_sets = {frozenset(v) for v in pred_norm.nets.values() if len(v) >= 2}
        gt_net_sets = {frozenset(v) for v in gt_norm.nets.values() if len(v) >= 2}

        matched_nets = pred_net_sets.intersection(gt_net_sets)
        net_precision = len(matched_nets) / max(1, len(pred_net_sets))
        net_recall = len(matched_nets) / max(1, len(gt_net_sets))
        net_f1 = (2 * net_precision * net_recall) / max(1e-6, net_precision + net_recall)

        # 3. Component MultiGraph Edge Comparison
        mg_pred = CircuitGraphManager.to_component_multigraph(pred_norm)
        mg_gt = CircuitGraphManager.to_component_multigraph(gt_norm)

        pred_edges = set()
        for u, v, k, d in mg_pred.edges(keys=True, data=True):
            pair = tuple(sorted([f"{u}.{d.get('c1_terminal', '')}", f"{v}.{d.get('c2_terminal', '')}"]))
            pred_edges.add(pair)

        gt_edges = set()
        for u, v, k, d in mg_gt.edges(keys=True, data=True):
            pair = tuple(sorted([f"{u}.{d.get('c1_terminal', '')}", f"{v}.{d.get('c2_terminal', '')}"]))
            gt_edges.add(pair)

        edge_insertions = len(pred_edges - gt_edges)
        edge_deletions = len(gt_edges - pred_edges)

        # 4. Compute Weighted Canonical Distance Score
        distance_score = (
            node_insertions * self.node_insertion_cost +
            node_deletions * self.node_deletion_cost +
            node_mismatches * self.type_mismatch_cost +
            edge_insertions * self.edge_insertion_cost +
            edge_deletions * self.edge_deletion_cost
        )

        details = {
            "predicted_components": len(pred_comps),
            "ground_truth_components": len(gt_comps),
            "matched_components": len(matched_ids),
            "predicted_nets": len(pred_net_sets),
            "ground_truth_nets": len(gt_net_sets),
            "matched_nets": len(matched_nets),
            "predicted_edges": len(pred_edges),
            "ground_truth_edges": len(gt_edges),
            "matched_edges": len(pred_edges.intersection(gt_edges)),
        }

        # Optional Exact NetworkX GED for small graphs
        if run_exact_ged and len(pred_comps) + len(gt_comps) <= self.exact_ged_max_nodes:
            try:
                g1 = CircuitGraphManager.to_bipartite_networkx(pred_norm)
                g2 = CircuitGraphManager.to_bipartite_networkx(gt_norm)
                exact_ged = nx.graph_edit_distance(g1, g2, timeout=self.ged_timeout)
                details["exact_networkx_ged"] = exact_ged
            except Exception as e:
                details["exact_networkx_ged_error"] = str(e)

        return EvaluationMetrics(
            ged_score=float(distance_score),
            component_precision=float(comp_precision),
            component_recall=float(comp_recall),
            component_f1=float(comp_f1),
            net_precision=float(net_precision),
            net_recall=float(net_recall),
            net_f1=float(net_f1),
            node_insertions=node_insertions,
            node_deletions=node_deletions,
            node_mismatches=node_mismatches,
            edge_insertions=edge_insertions,
            edge_deletions=edge_deletions,
            details=details
        )
