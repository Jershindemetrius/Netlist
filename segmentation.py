"""segmentation.py: Toolkit for Generation of Instance Segmentation Material"""

# System Imports
import sys
import os
from os.path import join, exists
import json
from math import dist

# Project Imports
from loader import read_pascal_voc, read_labelme, write_labelme, load_classes_ports
from utils import transform, associated_keypoints, overlap

# Third-Party Imports
import cv2
import numpy as np

__author__ = "Amit Kumar Roy"
__copyright__ = "Copyright 2022-2023, DFKI"
__credits__ = ["Amit Kumar Roy", "Johannes Bayer"]
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



def binary_to_multi_seg_map(drafter: str, sample: str, suffix: str, source_folder: str, target_folder: str,
                            color_map: dict) -> None:
    """Creates a Multi Class Segmentation File from a Binary Segmentation File and an Coarse Instance Polygon File"""

    bin_seg_map = cv2.imread(join(drafter, "segmentation", f"{sample}.{suffix}"))
    bin_seg_map[np.all(bin_seg_map <= (10, 10, 10), axis=-1)] = (0, 0, 0)
    shape_mask = np.ones(bin_seg_map.shape, dtype=np.uint8)*255
    geo_data = read_labelme(join(drafter, source_folder, f"{sample}.json"))

    for shape in sorted(geo_data["polygons"], key=lambda shape: -(shape['bbox']['xmax']-shape['bbox']['xmin']) *
                                                                 (shape['bbox']['ymax']-shape['bbox']['ymin'])):
        cv2.fillPoly(shape_mask,
                     pts=[np.array(shape["points"], dtype=np.int32)],
                     color=color_map[shape["class"]])

    multi_seg_map = cv2.bitwise_and(cv2.bitwise_not(bin_seg_map), shape_mask)

    for point in geo_data['points']:
        if point['class'] == "connector":
            x, y = point['points']
            cv2.line(multi_seg_map, (int(x-20), int(y-20)), (int(x+20), int(y+20)), (255, 255, 255), 2)
            cv2.line(multi_seg_map, (int(x-20), int(y+20)), (int(x+20), int(y-20)), (255, 255, 255), 2)

    cv2.imwrite(join(drafter, target_folder, f"{sample}.png"), multi_seg_map)


def generate_keypoints(drafter: str, sample: str, suffix: str, source_folder: str, target_folder: str,
                       keep_polygons: bool = True, margin=3) -> None:
    """Generates Connector Keypoints, optionally discarding existing polygons"""

    bin_seg_map = cv2.imread(join(drafter, "segmentation", f"{sample}.{suffix}"), cv2.IMREAD_GRAYSCALE)
    _, bin_seg_map = cv2.threshold(bin_seg_map, 127, 255, cv2.THRESH_BINARY_INV)
    geo_data = read_labelme(join(drafter, source_folder, f"{sample}.json"))
    detector_params = cv2.SimpleBlobDetector_Params()
    detector_params.minArea = 3
    detector_params.minDistBetweenBlobs = 3
    detector_params.minThreshold = 10
    detector_params.maxThreshold = 255
    detector_params.blobColor = 255
    detector_params.filterByArea = False
    detector_params.filterByCircularity = False
    detector_params.filterByConvexity = False
    detector_params.filterByInertia = False
    detector = cv2.SimpleBlobDetector_create(detector_params)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    for nbr, shape in enumerate(geo_data["polygons"]):
        if shape['class'] == "text":
            cv2.fillPoly(bin_seg_map, pts=[np.array(shape["points"], dtype=np.int32)], color=[0, 0, 0])

    for nbr, shape in enumerate(geo_data["polygons"]):
        shape['group'] = nbr

        if shape['class'] != "text" and shape['class'] != "wire":
            x_min = max(int(shape['bbox']['xmin'])-margin, 0)
            x_max = min(int(shape['bbox']['xmax'])+margin, bin_seg_map.shape[1])
            y_min = max(int(shape['bbox']['ymin'])-margin, 0)
            y_max = min(int(shape['bbox']['ymax'])+margin, bin_seg_map.shape[0])
            cropout = bin_seg_map[y_min:y_max, x_min:x_max]
            shape_mask = np.zeros((y_max-y_min, x_max-x_min), dtype=np.uint8)
            cv2.polylines(shape_mask, pts=[np.array(shape["points"]-np.array([[x_min, y_min]]), dtype=np.int32)],
                          isClosed=True, color=[255, 255, 255], thickness=2)
            intersect_map = cv2.bitwise_and(cropout, shape_mask)
            keypoints = detector.detect(intersect_map)
            geo_data['points'] += [{'class': "connector", 'points': (keypoint.pt[0]+x_min, keypoint.pt[1]+y_min),
                                    'group': nbr} for keypoint in keypoints]

    for shape in geo_data["polygons"]:
        if shape['class'] == "wire":
            wire_connectors = [point["points"] for point in geo_data['points']
                               if cv2.pointPolygonTest(np.array(shape["points"]), np.array(point['points']), True) > -4]

            if len(wire_connectors) != 2:
                print(f"    Anomaly Wire Connector Count: {len(wire_connectors)} -> {shape['points'][0]}")

            geo_data['points'] += [{'class': "connector", 'points': (point[0], point[1]),
                                    'group': shape['group']} for point in wire_connectors]

    geo_data['polygons'] = geo_data['polygons'] if keep_polygons else []
    write_labelme(geo_data, join(drafter, target_folder, f"{sample}.json"))


def generate_wires(drafter: str, sample: str, suffix: str, source_folder: str, target_folder: str) -> None:
    """Generates wire polygons"""

    geo_data = read_labelme(join(drafter, source_folder, f"{sample}.json"))
    bin_seg_map = cv2.imread(join(drafter, "segmentation", f"{sample}.{suffix}"), cv2.IMREAD_GRAYSCALE)
    _, bin_seg_map = cv2.threshold(bin_seg_map, 127, 255, cv2.THRESH_BINARY_INV)

    for nbr, shape in enumerate(geo_data["polygons"]):
        cv2.fillPoly(bin_seg_map, pts=[np.array(shape["points"], dtype=np.int32)], color=[0, 0, 0])

    cntrs = cv2.findContours(bin_seg_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = cntrs[0] if len(cntrs) == 2 else cntrs[1]

    for contour in contours:
        if len(contour) > 3:
            geo_data['polygons'] += [{'class': "wire", 'points': np.squeeze(contour).tolist(), 'group': None}]

    write_labelme(geo_data, join(drafter, target_folder, f"{sample}.json"))


def pascalvoc_to_labelme(drafter: str, sample: str, suffix: str, source_folder: str, target_folder: str,
                         keep_existing_json: bool = True) -> None:
    """Converts a Bounding Box (Rectangle) Annotation File to an Instance Mask (Polygon) File

    Has no Effect in its default Configuration on a
    consistently populated Dataset."""

    if keep_existing_json and exists(join(drafter, target_folder, f"{sample}.json")):
        print("  -> SKIP (already exists)")
        return None

    xml_data = read_pascal_voc(join(drafter, source_folder, f"{sample}.xml"))
    xml_data['points'] = []                                                   # Adapt to Segmentation Scenario
    xml_data['img_path'] = join("..", "segmentation", f"{sample}.{suffix}")   # Alter source image
    xml_data['polygons'] = [{'class': bbox['class'], 'group': None,           # Keep Class, Prune Rotation and Texts
                             'points': [[bbox['xmin'], bbox['ymin']],         # Turn Rectangles into Polygons
                                        [bbox['xmax'], bbox['ymin']],
                                        [bbox['xmax'], bbox['ymax']],
                                        [bbox['xmin'], bbox['ymax']]]}
                            for bbox in xml_data['bboxes']]
    write_labelme(xml_data, join(drafter, target_folder, f"{sample}.json"))


def labelme_raw_image(drafter: str, sample: str, suffix: str, source_folder: str, target_folder: str) -> None:
    """Resets the Source Images of a LabelME file to the Rwa Image"""

    geo_data = read_labelme(join(drafter, source_folder, f"{sample}.json"))
    geo_data['img_path'] = join("..", "images", f"{sample}.{suffix}")
    write_labelme(geo_data, join(drafter, target_folder, f"{sample}.json"))


def convex_hull(thresh_img: np.ndarray, polygon: np.ndarray) -> list:
    """Calculates the Convex Hull of a Binary Image, falling back to Polygon"""

    cntrs = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntrs = cntrs[0] if len(cntrs) == 2 else cntrs[1]
    good_contours = [contour for contour in cntrs if cv2.contourArea(contour) > 10]

    if good_contours:
        contours_combined = np.vstack(good_contours)
        hull = cv2.convexHull(contours_combined)
        return np.squeeze(hull).tolist()

    return polygon.tolist()


def refine_polygons(drafter: str, sample: str, suffix: str, source_folder: str, target_folder: str,
                    classes_discontinuous: list) -> None:
    """Main Function for Polygon Refinement"""

    geo_data = read_labelme(join(drafter, source_folder, f"{sample}.json"))
    img = cv2.imread(join(drafter, "segmentation", f"{sample}.{suffix}"))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (_, img) = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    background_mask = np.zeros(img.shape, dtype=np.uint8)

    for shape in geo_data['polygons']:
        if shape["class"] != "wire":
            polygon = np.array(shape["points"], dtype=np.int32)
            mask_single_components = cv2.fillPoly(background_mask, pts=[polygon], color=(255, 255, 255))
            bitwise_and_result = cv2.bitwise_and(img, mask_single_components)
            background_mask = np.zeros(img.shape, dtype=np.uint8)

            if shape["class"] in classes_discontinuous:
                hull_list = convex_hull(bitwise_and_result, polygon)
                shape['points'] = hull_list

            else:
                contours, _ = cv2.findContours(bitwise_and_result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    contour = max(contours, key=len)
                    contour = np.squeeze(contour)
                    contour_list = contour.tolist()
                    shape['points'] = contour_list

                else:
                    print(f"  !!!  WARNING: Empty Polygon: {shape['group']}  !!!")

    write_labelme(geo_data, join(drafter, target_folder, f"{sample}.json"))


def find_closest_points(list1, list2):
    reordered_list2 = []
    for x1, y1 in list1:
        min_distance = float("inf")
        min_point = None
        for x2, y2 in list2:
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if distance < min_distance:
                min_distance = distance
                min_point = (x2, y2)
        reordered_list2.append(min_point)
    return [list(row) for row in reordered_list2]


def connector_type_assignment(drafter: str, sample: str, suffix: str, source_folder: str, target_folder: str) -> None:
    """Connector Point to Port Type Assignment by Geometric Transformation Matching"""

    bboxes = read_pascal_voc(join(drafter, "annotations", f"{sample}.xml"))
    instances = read_labelme(join(drafter, source_folder, f"{sample}.json"))
    classes_ports = load_classes_ports()
    bad_connector_symbols = 0

    for shape in instances["polygons"]:
        if shape["class"] in classes_ports.keys():
            connectors = associated_keypoints(instances, shape)
            cls_ports = classes_ports[shape["class"]]
            bboxes_match = [bbox for bbox in bboxes['bboxes']
                            if overlap(bbox, shape["bbox"]) and bbox['class'] == shape['class']]

            if len(cls_ports) != len(connectors):
                print(f"    Bad Connector Count: {shape['class']}  {shape['points'][0]} -> {len(cls_ports)} vs. {len(connectors)}")
                bad_connector_symbols += 1

            if len(bboxes_match) != 1:
                print(f"    No BB for Polygon: {shape['class']}  {shape['points'][0]}")
                continue

            if bboxes_match[0]["rotation"] is None:
                print(f"    Missing Rotation in BB: {shape['class']}  {shape['points'][0]}")
                bboxes_match[0]["rotation"] = 0

            cls_ports_transformed = [transform(port, bboxes_match[0]) for port in cls_ports]

            for con in connectors:
                closest = sorted(cls_ports_transformed,
                                 key=lambda cls_port: dist(cls_port['position'], con['points']))[0]
                con['class'] = f"connector.{closest['name']}"

            shape['rotation'] = bboxes_match[0]['rotation']
            shape['text'] = bboxes_match[0]['text']

    write_labelme(instances, join(drafter, target_folder, f"{sample}.json"))
    return bad_connector_symbols


def pipeline(drafter: str, sample: str, suffix: str, source_folder: str, target_folder: str, **kwargs) -> None:
    """Standard Workflow"""

    generate_wires(drafter, sample, suffix, source_folder, target_folder)
    generate_keypoints(drafter, sample, suffix, target_folder, target_folder)
    refine_polygons(drafter, sample, suffix, target_folder, target_folder, kwargs["classes_discontinuous"])
    labelme_raw_image(drafter, sample, suffix, target_folder, target_folder)
    return connector_type_assignment(drafter, sample, suffix, target_folder, target_folder)


def execute(function: callable, source_folder: str, target_folder: str, drafter: str, info_msg: str, **kwargs):
    """Walks through the Dataset and applies the specified Function"""

    bad_connector_symbols = 0

    for drafter_dir in [f"drafter_{drafter}"] if drafter else sorted(next(os.walk('.'))[1]):
        if drafter_dir.startswith("drafter_"):

            if not os.path.isdir(join(drafter_dir, target_folder)):
                os.mkdir(join(drafter_dir, target_folder))

            for sample_raw in sorted(next(os.walk(join(drafter_dir, "segmentation")))[2]):
                sample, suffix = sample_raw.split(".")
                print(f"{info_msg} for: {drafter_dir} -> {sample}")
                res = function(drafter_dir, sample, suffix, source_folder, target_folder, **kwargs)
                if res is not None:
                    bad_connector_symbols += res

    print(f"Overall Symbols with incorrect Connector Count: {bad_connector_symbols}")


if __name__ == "__main__":

    with open("classes_discontinuous.json") as f:
        classes_discontinuous = json.load(f)

    with open('classes_color.json') as f:
        color_map = json.load(f)

    commands = {"transform": [pascalvoc_to_labelme, "annotations", "instances", "Transforming BBs -> Masks", {}],
                "wire":      [generate_wires, "instances", "wires", "Generating Wires", {}],
                "keypoint":  [generate_keypoints, "instances", "keypoints", "Generating Keypoints", {}],
                "create":    [binary_to_multi_seg_map, "instances", "segmentation_multi_class",
                              "Generating Multi-Class Segmentation Map", {"color_map": color_map}],
                "refine":    [refine_polygons, "instances", "instances_refined", "Refining Polygons",
                              {"classes_discontinuous": classes_discontinuous}],
                "reset":     [labelme_raw_image, "instances_refined", "instances_refined",
                              "Resetting Source Image", {}],
                "assign":    [connector_type_assignment, "instances_refined", "instances_refined",
                              "Assigning Connector Types", {}],
                "pipeline":  [pipeline, "instances", "instances_refined", "Processing",
                              {"classes_discontinuous": classes_discontinuous}]}

    if len(sys.argv) > 1 and sys.argv[1] in commands:
        fun, source, target, info, paras = commands[sys.argv[1]]
        drafter = sys.argv[2] if len(sys.argv) > 2 else ""
        target = sys.argv[3] if len(sys.argv) > 3 else target
        source = sys.argv[4] if len(sys.argv) > 4 else source
        execute(fun, source, target, drafter, info, **paras)

    else:
        print(f"Invalid command. Must be one of: {list(commands.keys())}")
