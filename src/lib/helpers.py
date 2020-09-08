import math
from queue import Full, Queue
from typing import Any, Tuple

import cv2
import slugify as unicode_slug


def calculate_relative_coords(
    bounding_box: Tuple[int, int, int, int], resolution: Tuple[int, int]
) -> Tuple[float, float, float, float]:
    x1_relative = bounding_box[0] / resolution[0]
    y1_relative = bounding_box[1] / resolution[1]
    x2_relative = bounding_box[2] / resolution[0]
    y2_relative = bounding_box[3] / resolution[1]
    return x1_relative, y1_relative, x2_relative, y2_relative


def calculate_absolute_coords(bounding_box, frame_res):
    return (
        math.floor(bounding_box[0] * frame_res[0]),
        math.floor(bounding_box[1] * frame_res[1]),
        math.floor(bounding_box[2] * frame_res[0]),
        math.floor(bounding_box[3] * frame_res[1]),
    )


def scale_bounding_box(image_size, bounding_box, target_size):
    """Scales a bounding box to target image size"""
    x1p = bounding_box[0] / image_size[0]
    y1p = bounding_box[1] / image_size[1]
    x2p = bounding_box[2] / image_size[0]
    y2p = bounding_box[3] / image_size[1]
    return (
        x1p * target_size[0],
        y1p * target_size[1],
        x2p * target_size[0],
        y2p * target_size[1],
    )


def draw_bounding_box_relative(frame, bounding_box, frame_res):
    topleft = (
        math.floor(bounding_box[0] * frame_res[0]),
        math.floor(bounding_box[1] * frame_res[1]),
    )
    bottomright = (
        math.floor(bounding_box[2] * frame_res[0]),
        math.floor(bounding_box[3] * frame_res[1]),
    )
    return cv2.rectangle(frame, topleft, bottomright, (255, 0, 0), 3)


def draw_object(frame, obj, camera_resolution):
    """ Draws a single pbject on supplied frame """
    frame = draw_bounding_box_relative(
        frame,
        (
            obj["relative_x1"],
            obj["relative_y1"],
            obj["relative_x2"],
            obj["relative_y2"],
        ),
        camera_resolution,
    )


def draw_objects(frame, objects, camera_resolution):
    """ Draws objects on supplied frame """
    for obj in objects:
        draw_object(frame, obj, camera_resolution)


def draw_zones(frame, zones):
    for zone in zones:
        if zone.objects_in_zone:
            color = (0, 255, 0)
        else:
            color = (0, 0, 255)
        cv2.polylines(frame, [zone.coordinates], True, color, 3)


def pop_if_full(queue: Queue, item: Any):
    """If queue is full, pop oldest item and put the new item"""
    try:
        queue.put_nowait(item)
    except Full:
        queue.get()
        queue.put_nowait(item)


def slugify(text: str) -> str:
    """Slugify a given text."""
    return unicode_slug.slugify(text, separator="_")


class Filter:
    def __init__(self, object_filter):
        self._label = object_filter.label
        self._confidence = object_filter.confidence
        self._width_min = object_filter.width_min
        self._width_max = object_filter.width_max
        self._height_min = object_filter.height_min
        self._height_max = object_filter.height_max

    def filter_confidence(self, obj):
        if obj["confidence"] > self._confidence:
            return True
        return False

    def filter_width(self, obj):
        if self._width_max > obj["width"] > self._width_min:
            return True
        return False

    def filter_height(self, obj):
        if self._height_max > obj["height"] > self._height_min:
            return True
        return False

    def filter_object(self, obj):
        return (
            self.filter_confidence(obj)
            and self.filter_width(obj)
            and self.filter_height(obj)
        )
