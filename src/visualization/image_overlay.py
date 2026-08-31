"""image_overlay.py: Visual Debugging Overlay on Input Photograph."""

from typing import List, Tuple, Optional
import numpy as np
import cv2

from src.common.schemas import Component, SkeletonGraphData, CircuitGraph


class ImageOverlayAnnotator:
    """Draws visual debugging overlays on input photographs."""

    # Color palette (BGR)
    COLOR_BBOX = (255, 140, 0)        # Deep orange
    COLOR_TERMINAL = (0, 255, 255)     # Yellow
    COLOR_JUNCTION = (0, 255, 0)       # Bright green
    COLOR_ENDPOINT = (0, 0, 255)       # Red
    COLOR_WIRE = (255, 0, 255)         # Magenta
    COLOR_TEXT = (255, 255, 255)       # White

    def annotate(
        self,
        image: np.ndarray,
        circuit_graph: Optional[CircuitGraph] = None,
        skeleton_data: Optional[SkeletonGraphData] = None,
        components: Optional[List[Component]] = None
    ) -> np.ndarray:
        """Annotates image with components, terminals, wire skeletons, junctions, and nets."""
        annotated = image.copy()
        if len(annotated.shape) == 2:
            annotated = cv2.cvtColor(annotated, cv2.COLOR_GRAY2BGR)

        # 1. Draw Skeleton Wires & Junctions
        if skeleton_data:
            # Wire segments
            for wire in skeleton_data.wire_segments:
                pts = np.array(wire.points, dtype=np.int32)
                if len(pts) >= 2:
                    cv2.polylines(annotated, [pts], isClosed=False, color=self.COLOR_WIRE, thickness=2)

            # Endpoints
            for ep in skeleton_data.endpoints:
                cv2.circle(annotated, (int(round(ep[0])), int(round(ep[1]))), 4, self.COLOR_ENDPOINT, -1)

            # Junctions
            for junc in skeleton_data.junctions:
                jx, jy = int(round(junc.position[0])), int(round(junc.position[1]))
                cv2.circle(annotated, (jx, jy), 6, self.COLOR_JUNCTION, -1)
                cv2.putText(annotated, f"J({junc.degree})", (jx + 8, jy - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.COLOR_JUNCTION, 1)

        # 2. Draw Components & Terminals
        comp_list = components or (circuit_graph.components if circuit_graph else [])

        for comp in comp_list:
            bbox = comp.bbox
            x1, y1 = int(round(bbox.xmin)), int(round(bbox.ymin))
            x2, y2 = int(round(bbox.xmax)), int(round(bbox.ymax))

            # Bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), self.COLOR_BBOX, 2)

            # Label text: ID : Class (Conf)
            label = f"{comp.id}: {comp.type} ({comp.confidence:.2f})"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated, (x1, max(0, y1 - th - 6)), (x1 + tw + 6, y1), self.COLOR_BBOX, -1)
            cv2.putText(annotated, label, (x1 + 3, max(th, y1 - 4)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_TEXT, 1)

            # Terminals
            for term in comp.terminals:
                tx, ty = int(round(term.position[0])), int(round(term.position[1]))
                cv2.circle(annotated, (tx, ty), 5, self.COLOR_TERMINAL, -1)
                
                t_label = f"{term.id}"
                if term.connected_net:
                    t_label += f" [{term.connected_net}]"
                    
                cv2.putText(annotated, t_label, (tx + 6, ty + 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.COLOR_TERMINAL, 1)

        return annotated
