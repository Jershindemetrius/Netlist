"""graph_visualizer.py: Circuit Graph Visualization with Matplotlib & NetworkX."""

from pathlib import Path
from typing import Optional, Union
import matplotlib.pyplot as plt
import networkx as nx

from src.common.schemas import CircuitGraph
from src.graph_assembly.circuit_graph import CircuitGraphManager


class GraphVisualizer:
    """Renders Matplotlib visualizations of bipartite and component circuit graphs."""

    @staticmethod
    def render_bipartite(graph: CircuitGraph, save_path: Optional[Union[str, Path]] = None) -> None:
        """Renders bipartite graph with Component, Terminal, and Net nodes."""
        B = CircuitGraphManager.to_bipartite_networkx(graph)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        pos = nx.spring_layout(B, k=0.8, seed=42)

        # Node colors by type
        colors = []
        for node, data in B.nodes(data=True):
            ntype = data.get("type", "")
            if ntype == "component":
                colors.append("dodgerblue")
            elif ntype == "terminal":
                colors.append("gold")
            elif ntype == "net":
                colors.append("mediumseagreen")
            else:
                colors.append("lightgray")

        nx.draw_networkx_nodes(B, pos, node_color=colors, node_size=800, ax=ax)
        nx.draw_networkx_edges(B, pos, edge_color="gray", width=1.5, ax=ax)
        nx.draw_networkx_labels(B, pos, font_size=9, font_weight="bold", ax=ax)

        ax.set_title("Canonical Bipartite Circuit Graph (Components -> Terminals -> Nets)", fontsize=14)
        ax.axis("off")
        plt.tight_layout()

        if save_path:
            plt.savefig(str(save_path), dpi=150)
            plt.close(fig)
        else:
            plt.show()

    @staticmethod
    def render_component_multigraph(graph: CircuitGraph, save_path: Optional[Union[str, Path]] = None) -> None:
        """Renders component-level MultiGraph with labeled net connections."""
        MG = CircuitGraphManager.to_component_multigraph(graph)
        
        fig, ax = plt.subplots(figsize=(10, 7))
        pos = nx.circular_layout(MG)

        nx.draw_networkx_nodes(MG, pos, node_color="skyblue", node_size=1200, ax=ax)
        nx.draw_networkx_labels(MG, pos, font_size=11, font_weight="bold", ax=ax)

        # Draw multi-edges
        edge_labels = {}
        for u, v, k, d in MG.edges(keys=True, data=True):
            edge_labels[(u, v)] = d.get("net", "")

        nx.draw_networkx_edges(MG, pos, edge_color="darkgray", width=2.0, ax=ax)
        nx.draw_networkx_edge_labels(MG, pos, edge_labels=edge_labels, font_size=8, ax=ax)

        ax.set_title("Derived Component-Level Circuit Graph", fontsize=14)
        ax.axis("off")
        plt.tight_layout()

        if save_path:
            plt.savefig(str(save_path), dpi=150)
            plt.close(fig)
        else:
            plt.show()
