"""utils.py: Helper Functions to keep this Repo Standalone"""

# System Imports
from math import sin, cos, radians, sqrt

__author__ = "Johannes Bayer"
__copyright__ = "Copyright 2023, DFKI"
__license__ = "CC"
__version__ = "0.0.1"
__email__ = "johannes.bayer@dfki.de"
__status__ = "Prototype"


def shift(p, q):
    """Shifts a Point by another point"""

    return [p[0]+q[0], p[1]+q[1]]


def rotate(p, angle):
    """Rotates a Point by an Angle"""

    return [p[0] * cos(angle) - p[1] * sin(angle),
            p[0] * sin(angle) + p[1] * cos(angle)]


def scale(p, scale_x, scale_y):
    """Scales a Point in two Dimensions"""

    return [p[0]*scale_x, p[1]*scale_y]


def transform(port, bb):
    """Transforms a Point from Unit Space (classes ports) to Global Bounding Box (image)"""

    p = shift(port['position'], (-.5, -0.5))  # Normalize: [0.0, 1.0]^2 -> [-0.5, 0-5]^2
    p = scale(p, 1.0, -1.0)                   # Flip
    p = rotate(p, -radians(bb['rotation']))
    p = scale(p, bb["xmax"] - bb["xmin"], bb["ymax"] - bb["ymin"])
    p = shift(p, [(bb["xmin"]+bb["xmax"])/2, (bb["ymin"]+bb["ymax"])/2])

    return {"name": port['name'], "position": p}


def bbdist(bb1, bb2):
    """Calculates the Distance between two Bounding Box Annotations"""

    return sqrt(((bb1["xmin"]+bb1["xmax"])/2 - (bb2["xmin"]+bb2["xmax"])/2)**2 +
                ((bb1["ymin"]+bb1["ymax"])/2 - (bb2["ymin"]+bb2["ymax"])/2)**2)


def overlap(bbox1, bbox2):

    if bbox1["xmin"] > bbox2["xmax"] or bbox1["xmax"] < bbox2["xmin"]:
        return False

    if bbox1["ymin"] > bbox2["ymax"] or bbox1["ymax"] < bbox2["ymin"]:
        return False

    return True


def associated_keypoints(instances, shape):
    """Returns the points with same group id as the provided polygon"""

    return [point for point in instances["points"]
            if point["group"] == shape["group"] and point["class"] == "connector"]


def IoU(bb1, bb2):
    """Intersection over Union"""

    intersection = 1
    union = 1

    return intersection/union


if __name__ == "__main__":

    import sys
    from loader import read_pascal_voc, write_pascal_voc
    import numpy as np
    import random

    if len(sys.argv) == 3:
        source = sys.argv[1]
        target = sys.argv[2]

        ann1, ann2 = [[bbox for bbox in read_pascal_voc(path)['bboxes'] if bbox['class'] == "text"]
                      for path in [source, target]]

        if not len(ann1) == len(ann2):

            print(f"Warning: Unequal Text Count ({len(ann1)} vs. {len(ann2)}), cropping..")
            consensus = min(len(ann1), len(ann2))
            ann1 = ann1[:consensus]
            ann2 = ann2[:consensus]

        x1 = np.array([(bbox['xmin']+bbox['xmax'])/2 for bbox in ann1])
        y1 = np.array([(bbox['ymin']+bbox['ymax'])/2 for bbox in ann1])
        x2 = np.array([(bbox['xmin']+bbox['xmax'])/2 for bbox in ann2])
        y2 = np.array([(bbox['ymin']+bbox['ymax'])/2 for bbox in ann2])
        x1 = ((x1-np.min(x1))/(np.max(x1)-np.min(x1))) * (np.max(x2)-np.min(x2)) + np.min(x2)
        y1 = ((y1-np.min(y1))/(np.max(y1)-np.min(y1))) * (np.max(y2)-np.min(y2)) + np.min(y2)
        dist = np.sqrt((x1-x2[np.newaxis].T)**2 + (y1-y2[np.newaxis].T)**2)
        indices_1 = np.arange(len(ann1))
        indices_2 = np.arange(len(ann2))
        print(np.sum(np.diagonal(dist)))

        for i in range(10000):
            if random.random() > 0.5:
                max_dist_pos = np.argmax(np.diagonal(dist))  # Mitigate Largest Cost

            else:
                max_dist_pos = random.randint(0, len(ann1)-1)

            if np.min(dist[max_dist_pos, :]) < np.min(dist[:, max_dist_pos]):
                min_dist_pos = np.argmin(dist[max_dist_pos, :])
                dist[:, [max_dist_pos, min_dist_pos]] = dist[:, [min_dist_pos, max_dist_pos]]  # Swap Columns
                indices_1[[max_dist_pos, min_dist_pos]] = indices_1[[min_dist_pos, max_dist_pos]]

            else:
                min_dist_pos = np.argmin(dist[:, max_dist_pos])
                dist[[max_dist_pos, min_dist_pos], :] = dist[[min_dist_pos, max_dist_pos], :]  # Swap Rows
                indices_2[[max_dist_pos, min_dist_pos]] = indices_2[[min_dist_pos, max_dist_pos]]

        print(np.sum(np.diagonal(dist)))

        wb = read_pascal_voc(target)

        for i in range(len(ann1)):
            ann2[indices_2[i]]['text'] = ann1[indices_1[i]]['text']
            bbox_match = [bbox for bbox in wb['bboxes']
                          if bbox['xmin'] == ann2[indices_2[i]]['xmin'] and
                             bbox['xmax'] == ann2[indices_2[i]]['xmax'] and
                             bbox['ymin'] == ann2[indices_2[i]]['ymin'] and
                             bbox['ymax'] == ann2[indices_2[i]]['ymax']]

            if len(bbox_match) == 1:
                bbox_match[0]['text'] = ann1[indices_1[i]]['text']
                bbox_match[0]['rotation'] = ann1[indices_1[i]]['rotation']

        write_pascal_voc(wb)

    else:
        print("Args: source target")
