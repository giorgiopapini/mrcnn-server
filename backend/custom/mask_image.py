import numpy as np
from io import BytesIO
from custom.classes import Mask
from typing import List
import cv2
from PIL import Image
import base64

class MaskImage(np.ndarray):
    def __new__(cls, input_array):
        return np.asarray(input_array).view(cls)
    
    def to_bytes(self) -> BytesIO:
        _, encoded_mask = cv2.imencode(".png", self)
        return BytesIO(encoded_mask.tobytes())
    
    def to_base64(self) -> str:
        img = Image.fromarray(self)
        buffer = BytesIO()
        img.save(buffer, format='png')
        base64_raw = base64.b64encode(buffer.getvalue())
        return base64_raw.decode('utf-8')

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
