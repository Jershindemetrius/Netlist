"""consistency.py: Integrity Check, Correction by Mapping for Annotation Class, Metadata Cleaning, Statistics"""

# System Imports
import os
import re
import argparse

# Project Imports
from loader import load_classes, load_properties, read_dataset, write_dataset, read_image, sample_name_tracable
from utils import bbdist

# Third-Party Imports
import matplotlib.pyplot as plt
import numpy as np

__author__ = "Johannes Bayer, Shabi Haider"
__copyright__ = "Copyright 2021-2023, DFKI, 2024-2025, Johannes Bayer"
__license__ = "CC"
__version__ = "0.0.2"
__email__ = "johannes.bayer@mail.de"
__status__ = "Prototype"




# Edit this lookup table for relabeling purposes
MAPPING_LOOKUP = {
    "integrated_cricuit": "integrated_circuit",
    "zener": "diode.zener"
}


def consistency(db: list, classes: dict, recover: dict = {}, check_texts=True, check_images=True) -> tuple:
    """Checks Whether Annotation Classes are in provided Classes Dict and Attempts Recovery"""

    total, ok, mapped, faulty, rotation, mirror_h, mirror_v, text = 0, 0, 0, 0, 0, 0, 0, 0

    for sample in db:
        for annotation in sample["bboxes"] + sample["polygons"] + sample["points"]:
            total += 1

            if annotation["class"] in classes:
                ok += 1

            if annotation["class"] in recover:
                annotation["class"] = recover[annotation["class"]]
                mapped += 1

            if annotation["class"] not in classes and annotation["class"] not in recover:
                print(f"Can't recover faulty label in {sample_name_tracable(sample)}: {annotation['class']}")
                faulty += 1

            if annotation["rotation"] is not None:
                rotation += 1

            if annotation["mirror_horizontal"]:
                mirror_h += 1

            if annotation["mirror_vertical"]:
                mirror_v += 1

            if check_texts:
                if annotation["class"] == "text" and annotation["text"] is None:
                    print(f"Missing Text in {sample_name_tracable(sample)}  ->  {annotation['xmin']}, {annotation['ymin']}")

                if annotation["text"] is not None:
                    if annotation["text"].strip() != annotation["text"]:
                        print(f"Removing leading of trailing spaces from: {annotation['text']}")
                        annotation["text"] = annotation["text"].strip()

                    if annotation["class"] != "text":
                        print(f"Text string outside Text Annotation in {sample_name_tracable(sample)} [{annotation['xmin']:4}, {annotation['ymin']:4}]: {annotation['class']}: {annotation['text']}")

                    text += 1

        if check_images:
            try:
                height, width, _ = read_image(sample).shape

                if (not sample['width'] == width) or (not sample['height'] == height):
                    sample['width'] = width
                    sample['height'] = height
                    print(f"Corrected Image Dimensions in Sample {sample_name_tracable(sample)}")

            except AttributeError:
                print(f"Missing or Corrupt Image for Sample {sample_name_tracable(sample)}")

    return total, ok, mapped, faulty, rotation, mirror_h, mirror_v, text


def consistency_circuit(db: list, classes: dict) -> None:
    """Checks whether the Amount of Annotation per Class is Consistent Among the Samples of a Circuits"""

    print("BBox Inconsistency Report:")
    sample_cls_bb_count = {(sample["circuit"], sample["drawing"], sample["picture"]):
                               {cls: len([bbox for bbox in sample["bboxes"] if bbox["class"] == cls])
                                for cls in classes} for sample in db}

    for circuit in set(sample["circuit"] for sample in db):
        circuit_samples = [sample for sample in sample_cls_bb_count if sample[0] == circuit]
        for cls in classes:
            check = [sample_cls_bb_count[sample][cls] for sample in circuit_samples]
            if not all(c == check[0] for c in check):
                print(f"  Circuit {circuit}:  {cls}: {check}")



def consistency_text(db: list) -> None:
    """Reports all Text Labels that Exist in a Strict Subset of Image Annotations of the same Circuit"""
    
    for circuit in set(sample["circuit"] for sample in db):
        circuit_samples = [sample for sample in db if sample["circuit"] == circuit]

        circuit_samples_texts = [sorted([bbox["text"] for bbox in sample["bboxes"] if bbox["text"]])
                                 for sample in circuit_samples]
	
        print(circuit)
        for c in circuit_samples_texts:
            print(c)



def circuit_annotations(db: list, classes: dict) -> None:
    """Plots the Annotations per Sample and Class"""

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 6))
    axes.plot([len(sample["bboxes"]) for sample in db], label="all")

    for cls in classes:
        axes.plot([len([annotation for annotation in sample["bboxes"]
                        if annotation["class"] == cls]) for sample in db], label=cls)

    plt.minorticks_on()
    axes.set_xticks(np.arange(0, len(db)+1, step=8))
    axes.set_xticks(np.arange(0, len(db), step=8)+4, minor=True)
    axes.grid(axis='x', linestyle='solid')
    axes.grid(axis='x', linestyle='dotted', alpha=0.7, which="minor")

    plt.title("Class Distribution in Samples")
    plt.xlabel("Image Sample")
    plt.ylabel("BB Annotation Count")

    plt.yscale('log')
    plt.legend(ncol=2, loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.show()


def annotation_distribution(db: list) -> None:

    amount_distribution([sample['bboxes'] for sample in db],
                        "Image Sample Count by BB Annotation Count",
                        "BB Annotation Count",
                        "Image Sample Count",
                        ticks=False)


def class_distribution(db: list, classes: dict) -> None:
    """Plots the Class Distribution over the Dataset"""

    class_nbrs = np.arange(len(classes))
    class_counts = [sum([len([annotation for annotation in sample["bboxes"] + sample["polygons"] + sample["points"]
                              if annotation["class"] == cls])
                         for sample in db]) for cls in classes]

    bars = plt.bar(class_nbrs, class_counts)
    plt.xticks(class_nbrs, labels=classes, rotation=90)
    plt.yscale('log')
    plt.title("Class Distribution")
    plt.xlabel("Class")
    plt.ylabel("BB Annotation Count")

    for rect in bars:
        height = rect.get_height()
        plt.annotate('{}'.format(height),
                     xy=(rect.get_x() + rect.get_width() / 2, height),
                     xytext=(0, -3), textcoords="offset points", ha='center', va='top', rotation=90)

    plt.show()


def image_sizes(db: list) -> None:
    """Statistics of the Raw Image's Widths and Heights"""

    widths = [sample['width'] for sample in db]
    heights = [sample['height'] for sample in db]
    print(f"Raw Image Width Range:  [{min(widths)}, {max(widths)}]")
    print(f"Raw Image Height Range:  [{min(heights)}, {max(heights)}]")

    plt.title('Image Sizes')
    plt.boxplot([heights, widths], vert=False)
    plt.yticks([2, 1], labels=["width", "height"])
    plt.show()


def class_sizes(db: list, classes: dict) -> None:
    """"""

    plt.title('BB Sizes')

    plt.boxplot([[max(bbox["xmax"]-bbox["xmin"], bbox["ymax"]-bbox["ymin"])
                  for sample in db for bbox in sample["bboxes"] if bbox["class"] == cls]
                 for cls in list(classes)[::-1]], vert=False)
    class_nbrs = np.arange(len(classes))+1
    plt.yticks(class_nbrs, labels=list(classes)[::-1])
    plt.tight_layout()
    plt.show()


def image_count(drafter: int = None, segmentation: bool = False) -> int:
    """Counts the Raw Images or Segmentation Maps in the Dataset"""

    return len([file_name for root, _, files in os.walk(".")
                for file_name in files
                if (f"segmentation{os.sep}" if segmentation else "annotation") in root and
                   (drafter is None or f"drafter_{drafter}{os.sep}" in root)])


def read_check_write(classes: dict, drafter: int = None, segmentation: bool = False,
                     check_images: bool = False, check_texts: bool = False) -> list:
    """Reads Annotations, Checks Consistency with Provided Classes
     Writes Corrected Annotations Back and Returns the Annotations"""

    db = read_dataset(drafter=drafter, segmentation=segmentation)
    ann_total, ann_ok, ann_mapped, ann_faulty, ann_rot, ann_mirror_h, ann_mirror_v, ann_text = consistency(db,
                                                                                                           classes,
                                                                                                           MAPPING_LOOKUP,
                                                                                                           check_texts=check_texts and not segmentation,
                                                                                                           check_images=check_images)
    write_dataset(db, segmentation=segmentation)

    print("")
    print("   Class and File Consistency Report")
    print(" -------------------------------------")
    print(f"Annotation Type: {'Polygon' if segmentation else 'Bounding Box'}")
    print(f"Class Label Count: {len(classes)}")
    print(f"Raw Image Files:            {image_count(drafter=drafter, segmentation=segmentation)}")
    print(f"Processed Annotation Files: {len(db)}")
    print(f"Total Annotation Count: {ann_total}")
    print(f"Consistent Annotations: {ann_ok}")
    print(f"Faulty Annotations (no recovery): {ann_faulty}")
    print(f"Corrected Annotations by Mapping: {ann_mapped}")
    print(f"Annotations with Rotation: {ann_rot}")
    print(f"Annotations with Mirror: {ann_mirror_h+ann_mirror_v} = {ann_mirror_h}(H) + {ann_mirror_v}(V)")
    print(f"Annotations with Text: {ann_text}")
    print("")

    return db


def unique_characters(texts: list) -> list:
    """Returns the Sorted Set of Unique Characters"""

    char_set = set([char for text in texts for char in text])
    return sorted(list(char_set))


def character_distribution(texts: list, chars: list):
    """Plots and Returns the Character Distribution"""

    char_nbrs = np.arange(len(chars))
    char_counts = [sum([len([None for text_char in text_label if text_char == char])
                        for text_label in texts])
                   for char in chars]
    plt.bar(char_nbrs, char_counts)
    plt.xticks(char_nbrs, chars)
    plt.title("Character Distribution")
    plt.xlabel("Character")
    plt.ylabel("Overall Count")
    plt.show()

    return char_counts


def amount_distribution(list_of_lists: list, title: str, x_label: str, y_label: str, ticks: bool = True) -> None:
    """Plots a Histogram of the Amount of Things Contained in a List of Lists"""

    max_bin = max([len(lst) for lst in list_of_lists])
    bin_numbers = np.arange(max_bin)+1
    text_count_by_length = [len([None for lst in list_of_lists if len(lst) == amount])
                            for amount in bin_numbers]
    plt.bar(bin_numbers, text_count_by_length)

    if ticks:
        plt.xticks(bin_numbers, rotation=90)

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()


def text_proximity(db: list, cls_name: str, cls_regex: str):
    """Proximity-Based Regex Validation"""

    cls_stat = {}

    for sample in db:
        bbs_text = [bbox for bbox in sample["bboxes"] if bbox["class"] == "text"]
        bbs_symbol = [bbox for bbox in sample["bboxes"] if bbox["class"] not in ["text", "junction", "crossover"]]

        for bb_text in bbs_text:
            if bb_text["text"]:
                if re.match(cls_regex, bb_text["text"]):
                    bb_closest_class = sorted(bbs_symbol, key=lambda bb: bbdist(bb_text, bb))[0]["class"]
                    cls_stat[bb_closest_class] = cls_stat.get(bb_closest_class, 0) + 1

    cls_stat = sorted(cls_stat.items(), key=lambda cls: -cls[1])
    print(cls_stat)
    plt.bar(range(len(cls_stat)), [name for _, name in cls_stat])
    plt.xticks(range(len(cls_stat)), labels=[name for name, _ in cls_stat], rotation=90)
    plt.title(f"Neighbor Distribution for {cls_name} Text Annotations")
    plt.xlabel("Symbol Class")
    plt.ylabel("Number of Closest Neighbors")
    plt.tight_layout()
    plt.show()


def text_statistics(db: list, plot_unique_labels: bool = False):
    """Generates and Plots Statistics on Text Classes"""

    text_bbs = [bbox for sample in db for bbox in sample["bboxes"] if bbox["class"] == "text"]
    text_labels = [bbox["text"] for bbox in text_bbs if type(bbox["text"]) is str and len(text_bbs) > 0]
    text_labels_unique = set(text_labels)
    chars_unique = unique_characters(text_labels)
    char_counts = character_distribution(text_labels, chars_unique)
    amount_distribution(text_labels, "Text Length Distribution", "Character Count", "Annotation Count")

    print("")
    print("   Text Statistics")
    print("---------------------")
    print(f"Text BB Annotations:      {len(text_bbs)}")
    print(f"Overall Text Label Count: {len(text_labels)}")
    print(f"Annotation Completeness:  {100*len(text_labels)/len(text_bbs):.2f}%")
    print(f"Unique Text Label Count:  {len(text_labels_unique)}")
    print(f"Total Character Count:    {sum([len(text_label) for text_label in text_labels])}")
    print(f"Character Types:          {len(chars_unique)}")
    print("\n\nSet of all characters occurring in all text labels:")
    print(chars_unique)
    print("\n\nSet of Text Labels:")
    print(text_labels_unique)

    print("\nCharacter Frequencies:")
    print({char: 1/char_count for char, char_count in zip(chars_unique, char_counts)})

    text_instances = text_labels_unique if plot_unique_labels else text_labels
    text_classes_names = []
    text_classes_instances = []

    for text_class in load_properties():
        text_classes_names.append(text_class["name"])
        text_classes_instances.append([text_instance for text_instance in text_instances
                                       if re.match(text_class["regex"], text_instance)])

    text_classified = [text for text_class_instances in text_classes_instances for text in text_class_instances]
    text_classes_names.append("Unclassified")
    text_classes_instances.append([text_instance for text_instance in text_instances
                                   if text_instance not in text_classified])

    for text_class_name, text_class_instances in zip(text_classes_names, text_classes_instances):
        print(f"\n{text_class_name}:")
        print(sorted(list(set(text_class_instances))))

    plt.bar(text_classes_names, [len(text_class_instances) for text_class_instances in text_classes_instances])
    plt.title('Count of matching pattern')
    plt.xlabel('Regex')
    plt.ylabel('No. of text matched')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

    text_proximity(db, "Capacitor Name", "^C[0-9]+$")
    text_proximity(db, "Resistor Name", "^R[0-9]+$")
    text_proximity(db, "Inductor Name", "^L[0-9]+$")



if __name__ == "__main__":

    # Prepare Argument Parser
    parser = argparse.ArgumentParser(prog='CGHD Consistency',
                                     description="Performs Integrity Checks and Statistics on the Dataset.")
    parser.add_argument("-d", "--drafter", type=int, default=None,
                        help="Performs the actions on a given drafter only. If none is given, the entire dataset is used.")
    parser.add_argument('-i', "--image-check", action='store_true',
                        help="Enables Image Dimension Verification")
    parser.add_argument('-c', "--text-check", action='store_true',
                        help="searches for text labels outside text annotations and text annotations without text Label")
    parser.add_argument('-a', "--annotation-consistency", action='store_true',
                        help="Enables Annotation Consistency Check (Class Count between Images of the Same Circuit)")
    parser.add_argument('-t', "--text-consistency", action='store_true',
                        help="Enables Text Consistency Check (Label Equality between Images of the same Circuit)")
    parser.add_argument('-s', "--statistics", action='store_true',
                        help="Performs Extended Statistics")
    args = parser.parse_args()

    # Load Class Info
    classes = load_classes()

    # Basic Integrity Checks
    db_bb = read_check_write(classes, args.drafter, segmentation=False,
                             check_images=args.image_check, check_texts=args.text_check)
    db_poly = read_check_write(classes, args.drafter, segmentation=True,
                               check_images=args.image_check, check_texts=args.text_check)

    # Consistency Checks between Images of the Same Circuit
    if args.annotation_consistency:
        consistency_circuit(db_bb, classes)

    if args.text_consistency:
        consistency_text(db_bb)

    # Statistics
    if args.statistics:
        image_sizes(db_bb)
        class_sizes(db_bb, classes)
        circuit_annotations(db_bb, classes)
        annotation_distribution(db_bb)
        class_distribution(db_bb, classes)
        class_distribution(db_poly, classes)
        text_statistics(db_bb)
