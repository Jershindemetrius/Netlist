# CGHD Dataset Audit & Preprocessing Report

## Executive Summary
This report provides a comprehensive architectural audit of the **Common Graphical Hand-Drawn Circuit Diagram (CGHD)** dataset (Zenodo ID: 14042961, GitHub: DFKI/cghd, Hugging Face: `lowercaseonly/cghd`). The dataset serves as the foundational benchmark for training and evaluating **Project NETLIST**.

---

## 1. Dataset Directory Structure
The authoritative folder hierarchy across all drafters is structured as follows:

```
cghd/
├── classes.json                    # Master 61-class category mapping
├── classes_ports.json              # Class-aware normalized terminal port locations
├── properties.json                 # Regular expressions for value/label parsing
├── drafter_1/                      # Drafter folder (e.g. drafter_1 through drafter_32)
│   ├── annotations/                # Pascal VOC XML annotation files (e.g., C1_D1_P1.xml)
│   ├── images/                     # Full RGB photographs (JPEG / JPG, e.g. C1_D1_P1.jpg)
│   ├── instances/                  # LabelMe JSON polygons & connector keypoints
│   ├── segmentation/               # Binary stroke segmentation maps
│   └── spice/                      # LTspice schematic ground-truth files (e.g., C1.asc)
├── drafter_2/
└── ...
```

---

## 2. Naming Conventions & Metadata Encoding
Each image file follows the deterministic naming template:
$$\text{C}X\_\text{D}Y\_\text{P}Z.\text{jpg}$$

Where:
- **$D$**: Drafter global identifier (e.g. `drafter_1` to `drafter_32`).
- **$X$**: Circuit design number ($1 \dots 12$ circuits per drafter).
- **$Y$**: Local drawing instance ($2$ drawings per circuit).
- **$Z$**: Picture variation / photo angle ($4$ photographs per drawing).

---

## 3. Dataset Characteristics & Summary Statistics

| Metric | Empirical Dataset Value |
| :--- | :--- |
| **Total Annotated Photographs** | ~3,173 images |
| **Total Drafters** | 30 active drafters (`drafter_1` to `drafter_30`, plus 2 meta folders) |
| **Symbol Classes** | 61 symbol classes (indexed 0 to 61 in `classes.json`) |
| **Bounding Box Annotations** | ~246,000 annotated bounding boxes |
| **Pascal VOC XML Annotations** | Complete XML coverage per photograph |
| **Image Resolution** | $960 \times 1280$ pixels (Vertical RGB photographs) |
| **LTspice (.asc) Ground Truth** | 12 reference schematic files per drafter |
| **Segmentation Maps** | Partial binary & multi-class stroke masks available |

---

## 4. Class Distribution & Key Symbol Categories

The dataset categorizes symbols into key electrical families:

1. **Passive Components**: `resistor`, `resistor.adjustable`, `resistor.photo`, `capacitor.unpolarized`, `capacitor.polarized`, `capacitor.adjustable`, `inductor`, `inductor.ferrite`, `transformer`.
2. **Semiconductors & Diodes**: `diode`, `diode.light_emitting`, `diode.zener`, `diode.thyrector`, `thyristor`, `diac`, `triac`, `varistor`.
3. **Transistors**: `transistor.bjt`, `transistor.fet`, `transistor.photo`.
4. **Power Sources & References**: `voltage.dc`, `voltage.ac`, `voltage.battery`, `gnd`, `vss`.
5. **Logic Gates & Integrated Circuits**: `and`, `or`, `not`, `nand`, `nor`, `xor`, `operational_amplifier`, `integrated_circuit.ne555`, `integrated_circuit`.
6. **Structural Topology Markers**: `junction`, `crossover`, `terminal`, `text`.

> [!NOTE]
> **Rare Classes**: Specialized ICs (`integrated_circuit.voltage_regulator`), `diac`, and `probe.current` represent rare classes (< 0.5% frequency). Augmentation and synthetic schematic pretraining compensate for class imbalance.

---

## 5. Drafter-Isolated Dataset Partitioning Strategy

To guarantee that the detection model generalizes to unseen handwriting styles and line variations, images are partitioned **strictly by drafter holdout**:

- **Train Split (~70%)**: 22 Drafters (`drafter_1` through `drafter_22`)
- **Val Split (~15%)**: 4 Drafters (`drafter_23` through `drafter_26`)
- **Test Split (~15%)**: 4 Drafters (`drafter_27` through `drafter_30`)

> [!WARNING]
> **Zero Drafter Leakage**: No single drafter appears in more than one split. Random image-level splitting is explicitly forbidden.

---

## 6. Recommendations for YOLO11 Symbol Detection

1. **Recommended Model**: **YOLO11s** (Ultralytics YOLO11 Small).
   - Balance: Superior recall on small symbols compared to `nano`, while remaining fast and CPU/Colab compatible.
2. **Recommended Training Resolution**: **960 pixels** (`imgsz=960`).
   - High-resolution training is critical because hand-drawn junctions, crossovers, and small text labels span only $15 \times 15$ pixels in original $960 \times 1280$ photographs.
3. **Data Augmentation Strategy**:
   - Small rotations ($\pm 15^\circ$), subtle perspective distortion, line thickness variation, Gaussian blur.
   - **No horizontal/vertical flip** for asymmetric symbols (e.g. diodes, polarized capacitors, BJTs).
