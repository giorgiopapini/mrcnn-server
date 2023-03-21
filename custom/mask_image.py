import numpy as np
from io import BytesIO
from custom.classes import Mask
from typing import List
import cv2

class MaskImage(np.ndarray):
    def __new__(cls, input_array):
        return np.asarray(input_array).view(cls)
    
    def to_bytes(self) -> BytesIO:
        _, encoded_mask = cv2.imencode(".png", self)
        return BytesIO(encoded_mask.tobytes())

    @property
    def masks(self) -> List[Mask]:
        masks: List[Mask] = []
        contours, _ = cv2.findContours(self, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            mask = Mask(
                contour=cnt.tolist(), 
                area_px=cv2.contourArea(contour=cnt), 
                perimeter_px=cv2.arcLength(cnt, True)
            )
            masks.append(mask)
        return masks
