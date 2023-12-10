from typing import Any
from ultralytics import YOLO
import numpy as np
from image_resizer.image_resizer import ImageResizer
import cv2

class YOLO_WRAP:
    MODEL_PATH = "./yolov8/models/last.pt"
    IMAGE_SIZE = 224
    model: Any = None

    @staticmethod
    def load_model() -> None:
        YOLO_WRAP.model = YOLO(YOLO_WRAP.MODEL_PATH)

    @staticmethod
    def predict(img: np.ndarray) -> np.ndarray:
        img = ImageResizer.try_format_img(img, YOLO_WRAP.IMAGE_SIZE)  # It resizes the image to match the IMAGE_SIZE
        return YOLO_WRAP.model(img)