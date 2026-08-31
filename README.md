# NETLIST — Hand-Drawn Circuit to Canonical Graph & Netlist Engine

A modular, production-quality Computer Vision and Graph Reconstruction system that converts photographs of hand-drawn electronic circuit diagrams into canonical terminal-aware circuit graphs and simulation-ready SPICE netlists.

---

## ⚡ Key Capabilities

1. **Computer Vision Object Detection**: Locates 61+ hand-drawn electronic component symbol classes using **Ultralytics YOLO11s**.
2. **Terminal Geometry Estimation**: Class-aware terminal template mapping with stroke-level orientation estimation.
3. **Classical Wire Tracing**: Morphological 1-pixel skeleton thinning and 8-neighborhood degree junction detection ($D \ge 3$).
4. **Electrical Net Reconstruction**: Disjoint Set Union (DSU / Union-Find) clustering connecting endpoints to terminals.
5. **Deterministic Graph Normalization**: Standardized spatial relabeling (`R1, C1, Q1, V1...` and `NET1, NET2...`, `0`).
6. **Graph Edit Distance Evaluation**: Evaluates predicted graphs against LTspice `.asc` ground-truth schematics.
7. **Hackathon-Grade Developer Workspace**: Light-themed Next.js App Router frontend with interactive React Flow graph visualization, image-to-graph bidirectional linking, uncertainty warnings, and SPICE netlist export.

---

## 🚀 Quick Start

### 1. Frontend Web Workspace Setup

```bash
# 1. Install dependencies
npm install

# 2. Run local development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### 2. Environment Configuration

Create a `.env.local` file in the root directory:

```env
# Configurable FastAPI Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Set to true for offline mock mode development
NEXT_PUBLIC_USE_MOCK_API=false
```

---

### 3. Backend API Contract (`POST /api/analyze`)

The Next.js frontend expects the backend FastAPI service to implement the following contract:

**Endpoint**: `POST /api/analyze`  
**Content-Type**: `multipart/form-data`  
**Payload**: `image` (File / Blob)

#### JSON Response Schema:
```json
{
  "status": "success",
  "image_id": "circuit_001",
  "components": [
    {
      "id": "R1",
      "type": "resistor",
      "class_id": 10,
      "confidence": 0.94,
      "bbox": [220, 120, 340, 180],
      "value": "10kΩ",
      "terminals": [
        { "id": "T1", "position": [220, 150], "net": "NET1", "confidence": 0.96 },
        { "id": "T2", "position": [340, 150], "net": "NET2", "confidence": 0.92 }
      ]
    }
  ],
  "nets": {
    "NET1": ["V1.POS", "R1.T1", "Q1.C"],
    "NET2": ["R1.T2", "C1.T1", "D1.A"],
    "0": ["V1.NEG", "C1.T2", "Q1.E"]
  },
  "wires": [
    { "id": "W1", "points": [[120, 150], [220, 150]], "confidence": 0.97 }
  ],
  "metrics": {
    "components": 5,
    "nets": 3,
    "connections": 8
  },
  "confidence": 0.89
}
```

---

## 🛠️ Python CLI Pipeline Commands

```bash
# 1. Run unit test suite (10/10 tests)
python -m unittest discover -s tests -p "test_*.py" -v

# 2. Prepare YOLO dataset & drafter-isolated split
python scripts/prepare_dataset.py --seed 42

# 3. Generate synthetic circuit dataset samples
python src/data/synthetic_generator.py --count 10 --output data/synthetic

# 4. Train YOLO11 symbol detector
python scripts/train_detector.py --config configs/detection.yaml

# 5. Run end-to-end CV-to-Netlist pipeline on an image
python scripts/run_pipeline.py --image data/raw/cghd/drafter_1/images/C1_D1_P1.jpg --output output

# 6. Evaluate predicted graph against LTspice .asc ground truth
python scripts/evaluate.py --prediction output/C1_D1_P1_circuit_graph.json --ground-truth data/raw/cghd/drafter_1/spice/C1.asc
```

---

## 📁 Repository Structure

```text
├── configs/                  # YAML configurations (detection, wire_tracing, templates, eval)
├── src/                      # Core Computer Vision Engine
│   ├── common/               # Pydantic schemas, I/O, logging, math utilities
│   ├── data/                 # Dataset inspector, drafter splitter, VOC converter, synthetic generator
│   ├── geometry/             # Class templates, orientation estimator, terminal locator
│   ├── wire_tracing/         # Preprocessing, skeletonization, junction detector, endpoint matching
│   ├── graph_assembly/       # Circuit graph data structure, DSU net builder, normalizer, serializer
│   ├── eval/                 # LTspice .asc parser, GED evaluator, reporting
│   ├── detection/            # YOLO11 interface, trainer, postprocessing
│   └── visualization/        # Image overlay annotator & graph visualizers
├── src/                      # Frontend Next.js Workspace
│   ├── app/                  # Next.js App Router (layout.tsx, page.tsx, globals.css)
│   ├── components/           # Upload, Analysis, React Flow Graph, Netlist & Workspace UI
│   ├── lib/                  # API client, React Flow layout, export utilities, types, mock data
│   └── hooks/                # useCircuitAnalysis state hook
├── scripts/                  # Command line execution scripts
├── tests/                    # Automated unit test suite
├── notebooks/                # Google Colab GPU training notebook
└── README.md
```

---

## 📦 Production Build

```bash
# Typecheck and build production Next.js bundle
npm run build

# Start production server
npm start
```
