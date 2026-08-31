"""loader.py: Load and Store Functions for the Dataset"""

# System Imports
import os, sys
from os.path import join, realpath
import json
import xml.etree.ElementTree as ET

# Third Party Imports
import cv2
import numpy as np
from lxml import etree

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2022-2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"



def load_classes() -> dict:
    """Returns the List of Classes as Encoding Map"""

    with open("classes.json") as classes_file:
        return json.loads(classes_file.read())


def load_classes_ports() -> dict:
    """Reads Symbol Library from File"""

    with open("classes_ports.json") as json_file:
        return json.loads(json_file.read())


def load_properties() -> dict:
    """Loads the Properties RegEx File"""

    with open("properties.json") as json_file:
        return json.loads(json_file.read())


def _sample_info_from_path(path: str) -> tuple:
    """Extracts Sample Metadata from File Path"""

    drafter, _, file_name = os.path.normpath(path).split(os.sep)[-3:]
    circuit, drawing, picture = file_name.split("_")
    picture, suffix = picture.split(".")
    return drafter.split("_")[1], int(circuit[1:]), int(drawing[1:]), int(picture[1:]), suffix


def sample_name(sample: dict) -> str:
    """Returns the Name of a Sample"""

    return f"C{sample['circuit']}_D{sample['drawing']}_P{sample['picture']}"


def sample_name_tracable(sample: dict) -> str:
    """Returns the Unambiguous, Human-Readable Sample Name"""

    return f"Drafter{sample['drafter']}/{sample_name(sample)}"


def file_name(sample: dict) -> str:
    """return the Raw Image File Name of a Sample"""

    return f"{sample_name(sample)}.{sample['format']}"


def read_pascal_voc(path: str) -> dict:
    """Reads the Content of a Pascal VOC Annotation File"""

    root = ET.parse(path).getroot()
    circuit, drawing, picture = root.find("filename").text.split("_")
    drafter = int(os.path.normpath(path).split(os.sep)[-3].split("_")[1])

    return {"drafter": drafter,
            "circuit": int(circuit[1:]),
            "drawing": int(drawing[1:]),
            "picture": int(picture.split(".")[0][1:]),
            "format": picture.split(".")[-1],
            "width": int(root.find("size/width").text),
            "height": int(int(root.find("size/height").text)),
            "bboxes": [{"class": annotation.find("name").text,
                        "xmin": int(annotation.find("bndbox/xmin").text),
                        "xmax": int(annotation.find("bndbox/xmax").text),
                        "ymin": int(annotation.find("bndbox/ymin").text),
                        "ymax": int(annotation.find("bndbox/ymax").text),
                        "rotation": int(annotation.find("bndbox/rotation").text) if annotation.find("bndbox/rotation") is not None else None,
                        "mirror_horizontal": len([tag for tag in annotation.findall("bndbox/mirror") if tag.text=="horizontal"])>0,
                        "mirror_vertical": len([tag for tag in annotation.findall("bndbox/mirror") if tag.text=="vertical"])>0,
                        "text": annotation.find("text").text if annotation.find("text") is not None else None}
                       for annotation in root.findall('object')],
            "polygons": [], "points": []}


def write_pascal_voc(sample: dict) -> None:
    """Writes a Sample's Content to an Pascal VOC Annotation File"""

    root = etree.Element("annotation")
    etree.SubElement(root, "folder").text = "images"
    etree.SubElement(root, "filename").text = file_name(sample)
    etree.SubElement(root, "path").text = join(".", f"drafter_{sample['drafter']}", "images", file_name(sample))
    src = etree.SubElement(root, "source")
    etree.SubElement(src, "database").text = "CGHD"
    size = etree.SubElement(root, "size")
    etree.SubElement(size, "width").text = str(sample["width"])
    etree.SubElement(size, "height").text = str(sample["height"])
    etree.SubElement(size, "depth").text = "3"
    etree.SubElement(root, "segmented").text = "0"

    for bbox in sample["bboxes"]:
        xml_obj = etree.SubElement(root, "object")
        etree.SubElement(xml_obj, "name").text = bbox["class"]
        etree.SubElement(xml_obj, "pose").text = "Unspecified"
        etree.SubElement(xml_obj, "truncated").text = "0"
        etree.SubElement(xml_obj, "difficult").text = "0"
        xml_bbox = etree.SubElement(xml_obj, "bndbox")

        for elem in ["xmin", "ymin", "xmax", "ymax"]:
            etree.SubElement(xml_bbox, elem).text = str(bbox[elem])

        if bbox["rotation"] is not None:
            etree.SubElement(xml_bbox, "rotation").text = str(bbox["rotation"])

        if bbox["mirror_horizontal"]:
            etree.SubElement(xml_bbox, "mirror").text = "horizontal"

        if bbox["mirror_vertical"]:
            etree.SubElement(xml_bbox, "mirror").text = "vertical"

        if bbox["text"]:
            etree.SubElement(xml_obj, "text").text = bbox["text"]

    etree.indent(root, space="\t")
    etree.ElementTree(root).write(join(".", f"drafter_{sample['drafter']}", "annotations",
                                       f"C{sample['circuit']}_D{sample['drawing']}_P{sample['picture']}.xml"),
                                  pretty_print=True)


def read_labelme(path: str) -> dict:
    """Reads and Returns Geometric Objects from a LabelME JSON File"""

    with open(path) as json_file:
        json_data = json.load(json_file)

    drafter, circuit, drawing, picture, _ = _sample_info_from_path(path)
    suffix = json_data['imagePath'].split(".")[-1]

    return {'img_path': json_data['imagePath'].replace("\\", "/"), 'drafter': drafter, 'circuit': circuit,
            'drawing': drawing, 'picture': picture, 'format': suffix,
            'height': json_data['imageHeight'], 'width': json_data['imageWidth'], 'bboxes': [],
            'polygons': [{'class': shape['label'],
                          'bbox': {'xmin': min(point[0] for point in shape['points']),
                                   'ymin': min(point[1] for point in shape['points']),
                                   'xmax': max(point[0] for point in shape['points']),
                                   'ymax': max(point[1] for point in shape['points'])},
                          'points': shape['points'],
                          'rotation': shape.get('rotation', None),
                          'mirror_horizontal': shape.get('mirror_horizontal', None),
                          'mirror_vertical': shape.get('mirror_vertical', None),
                          'text': shape.get('text', None),
                          'group': shape.get('group_id', None)}
                         for shape in json_data['shapes']
                         if shape['shape_type'] == "polygon"],
            'points': [{'class': shape['label'], 'points': shape['points'][0],
                        'group': shape['group_id'] if 'group_id' in shape else None}
                       for shape in json_data['shapes']
                       if shape['shape_type'] == "point"]}


def write_labelme(geo_data: dict, path: str = None) -> None:
    """Writes Geometric Objects to a LabelMe JSON File"""

    if not path:
        path = join(f"drafter_{geo_data['drafter']}", "instances",
                    f"C{geo_data['circuit']}_D{geo_data['drawing']}_P{geo_data['picture']}.json")

    with open(path, 'w') as json_file:
        json.dump({'version': '5.2.0',
                   'flags': {},
                   'shapes': [{'line_color': None, 'fill_color': None,'label': polygon['class'],
                               'points': polygon['points'],
                               'group_id': polygon.get('group', None),
                               'description': polygon.get('description', None),
                               **({'rotation': polygon['rotation']} if polygon.get('rotation', None) else {}),
                               **({'mirror_horizontal': polygon['mirror_horizontal']} if polygon.get('mirror_horizontal') else {}),
                               **({'mirror_vertical': polygon['mirror_vertical']} if polygon.get('mirror_vertical') else {}),
                               **({'text': polygon['text']} if polygon.get('text', None) else {}),
                               'shape_type': 'polygon', 'flags': {}}
                              for polygon in geo_data['polygons']] +
                             [{'label': point['class'], 'points': [[point['points'][0], point['points'][1]]],
                               'group_id': point['group'], 'shape_type': 'point', 'flags': {}}
                              for point in geo_data['points']],
                   'imagePath': geo_data['img_path'],
                   'imageData': None,
                   'imageHeight': geo_data['height'],
                   'imageWidth': geo_data['width'],
                   'lineColor': [0, 255, 0, 128],
                   'fillColor': [255, 0, 0, 128]},
                  json_file, indent=2)


def read_dataset(drafter: int = None, circuit: int = None, segmentation=False, folder: str = None) -> list:
    """Reads all BB Annotation Files from Folder Structure
    This Method can be invoked from Anywhere, can be restricted to a specified drafter
    and can be use for both BB and Polygon Annotations. Alternative annotation sub-folder
    can be specified to read processed ground truth."""

    db_root = os.sep.join(realpath(__file__).split(os.sep)[:-1])

    return sorted([(read_labelme if segmentation else read_pascal_voc)(join(root, file_name))
                   for root, _, files in os.walk(db_root)
                   for file_name in files
                   if (folder if folder else (f"instances" if segmentation else f"annotations")) in root and
                      (not circuit or f"C{circuit}_" in file_name) and
                      (drafter is None or f"drafter_{drafter}{os.sep}" in root)],
                  key=lambda sample: sample["circuit"]*100+sample["drawing"]*10+sample["picture"])


def write_dataset(db: list, segmentation=False) -> None:
    """Writes a Dataset"""

    for sample in db:
        (write_labelme if segmentation else write_pascal_voc)(sample)


def read_image(sample: dict) -> np.ndarray:
    """Loads the Image Associated with a DB Sample"""

    db_root = os.sep.join(realpath(__file__).split(os.sep)[:-1])

    return cv2.imread(join(db_root, f"drafter_{sample['drafter']}", "images", file_name(sample)))


def read_images(**kwargs) -> list:
    """Loads Images and BB Annotations and returns them as as List of Pairs"""

    return [(read_image(sample), sample) for sample in read_dataset(**kwargs)]


def read_snippets(**kwargs):
    """Loads Image Snippets and BBoxes and returns them as List of Pairs"""

    snippets = []

    for img, annotations in read_images(**kwargs):
        for bbox in annotations['bboxes']:
            snippets += [(img[bbox['ymin']:bbox['ymax'], bbox['xmin']:bbox['xmax']], bbox, sample_name(annotations))]

    return snippets


if __name__ == "__main__":
    """Sample Loader Usage, Dumps All Text Snippets of (Selectable or All) Drafter to Test Folder"""

    os.mkdir("test")
    args = {'drafter': int(sys.argv[1])} if len(sys.argv) == 2 else {}

    for snippet, bbox, sample in read_snippets(**args):
        if bbox['class'] == "text" and bbox.get("text", ""):
            if bbox['rotation'] == 90:
                snippet = cv2.rotate(snippet, cv2.ROTATE_90_CLOCKWISE)
            if bbox['rotation'] == 270:
                snippet = cv2.rotate(snippet, cv2.ROTATE_90_COUNTERCLOCKWISE)

            cv2.imwrite(join("test", f"{bbox['text']}___{sample}_{bbox['ymin']}_{bbox['ymax']}_{bbox['xmin']}_{bbox['xmax']}.png"), snippet)

