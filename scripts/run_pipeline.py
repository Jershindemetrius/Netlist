"""run_pipeline.py: End-to-End Hand-Drawn Circuit to Canonical Netlist Execution Pipeline."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import cv2

from src.common.logging import logger
from src.common.io import load_image, save_image, PipelineCache
from src.common.schemas import CircuitGraph
from src.detection.detector import YOLO11Detector
from src.geometry.terminal_estimator import TerminalEstimator
from src.wire_tracing.preprocessing import WirePreprocessor
from src.wire_tracing.skeleton import WireSkeletonizer
from src.wire_tracing.skeleton_graph import SkeletonGraphBuilder
from src.graph_assembly.net_builder import NetBuilder
from src.graph_assembly.graph_normalizer import GraphNormalizer
from src.graph_assembly.serializer import CircuitSerializer
from src.visualization.image_overlay import ImageOverlayAnnotator


def run_pipeline(
    image_path: str,
    weights_path: str = "models/checkpoints/best.pt",
    output_dir: str = "output",
    classes_file: str = "classes.json"
) -> CircuitGraph:
    """Executes the complete CV-to-Netlist pipeline for an input photograph."""
    img_path = Path(image_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    image_id = img_path.stem

    logger.info(f"Processing circuit diagram image: {img_path}")
    image = load_image(img_path)

    # Initialize modules
    cache = PipelineCache(cache_dir="data/cache")
    detector = YOLO11Detector(weights_path=weights_path, classes_file=classes_file, cache=cache)
    terminal_estimator = TerminalEstimator()
    preprocessor = WirePreprocessor()
    skeletonizer = WireSkeletonizer()
    graph_builder = SkeletonGraphBuilder()
    net_builder = NetBuilder()
    normalizer = GraphNormalizer()
    annotator = ImageOverlayAnnotator()

    # Stage 1: Symbol Detection
    logger.info("Stage 1: Running symbol detection...")
    detections = detector.detect(image, image_id=image_id)
    logger.info(f"Detected {len(detections)} component candidate boxes.")

    # Stage 2: Terminal Estimation & Geometry
    logger.info("Stage 2: Estimating component terminals and orientation...")
    components = []
    for idx, det in enumerate(detections):
        comp_id = f"RAW_{idx+1}"
        comp = terminal_estimator.estimate_terminals(comp_id, det, image=image)
        components.append(comp)

    # Stage 3: Classical CV Wire Tracing & Skeletonization
    logger.info("Stage 3: Masking components & skeletonizing wire network...")
    wire_binary = preprocessor.preprocess(image, components=components)
    skeleton = skeletonizer.skeletonize(wire_binary)

    # Stage 4: Skeleton Graph & Junction Extraction
    logger.info("Stage 4: Building skeleton graph & detecting endpoints/junctions...")
    _, skeleton_data = graph_builder.build_graph(skeleton)
    logger.info(f"Extracted {len(skeleton_data.wire_segments)} wire segments, {len(skeleton_data.junctions)} junctions, {len(skeleton_data.endpoints)} endpoints.")

    # Stage 5: Electrical Net Reconstruction
    logger.info("Stage 5: Reconstructing electrical nets...")
    nets = net_builder.build_nets(components, skeleton_data)

    # Stage 6: Canonical Graph Normalization
    logger.info("Stage 6: Normalizing canonical CircuitGraph...")
    raw_graph = CircuitGraph(
        components=components,
        nets=nets,
        metadata={"source_image": img_path.name}
    )
    canonical_graph = normalizer.normalize(raw_graph)

    # Stage 7: Intelligent Circuit Graph Analysis
    logger.info("Stage 7: Running Intelligent Circuit Graph Analyzer (Confidence, Errors, Subcircuits)...")
    from src.graph_analysis.analyzer import IntelligentGraphAnalyzer
    analyzer = IntelligentGraphAnalyzer()
    analysis_report = analyzer.analyze(canonical_graph, image_id=image_id)

    # Stage 8: Serialized Exports & Visualization
    json_path = out_dir / f"{image_id}_circuit_graph.json"
    analysis_path = out_dir / f"{image_id}_analysis_report.json"
    spice_path = out_dir / f"{image_id}_netlist.cir"
    overlay_path = out_dir / f"{image_id}_annotated.png"

    CircuitSerializer.to_json_file(canonical_graph, json_path)
    CircuitSerializer.to_spice_file(canonical_graph, spice_path, title=f"Extracted from {img_path.name}")

    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write(analysis_report.model_dump_json(indent=2))

    annotated_img = annotator.annotate(image, circuit_graph=canonical_graph, skeleton_data=skeleton_data)
    save_image(annotated_img, overlay_path)

    print("=" * 65)
    print("               PIPELINE EXECUTION COMPLETE")
    print("=" * 65)
    print(f"Canonical Graph JSON: {json_path}")
    print(f"SPICE Netlist Text:   {spice_path}")
    print(f"Annotated Overlay:    {overlay_path}")
    print("=" * 65)

    print("\n--- SPICE NETLIST OUTPUT ---")
    print(canonical_graph.to_spice_netlist(title=img_path.name))
    print("----------------------------\n")

    return canonical_graph


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run end-to-end NETLIST pipeline on a circuit photograph.")
    parser.add_argument("--image", required=True, help="Path to input circuit image")
    parser.add_argument("--weights", default="models/checkpoints/best.pt", help="Path to YOLO weights")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    run_pipeline(image_path=args.image, weights_path=args.weights, output_dir=args.output)
