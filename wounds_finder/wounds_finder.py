from typing import List
from custom.mask_image import MaskImage
from custom.classes import Wound
from ranking.ranking import Ranking
import cv2


class WoundsFinder:
    def __init__(self, ratio: float) -> None:
        self.ratio = ratio
        self.wounds: List[Wound] = []

    def find_wounds(self, mask: MaskImage) -> List[Wound]:
        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            area_cm = WoundsFinder.calculate_cm(area, self.ratio ** 2)
            perim = cv2.arcLength(cnt, True)
            perim_cm = WoundsFinder.calculate_cm(perim, self.ratio)
            m = cv2.moments(cnt)
            if m['m00'] != 0:
                cx = int(m['m10'] / m['m00'])
                cy = int(m['m01'] / m['m00'])
                self.__add_wound(cnt, area_cm, perim_cm, cx, cy)
        
        return self.wounds
    
    def __add_wound(self, cnt, area_cm, perim_cm, cx, cy) -> None:
        wound = Wound(
            contour=cnt.tolist(),
            perimeter=perim_cm,
            area=area_cm,
            center_coordinates=(cx, cy),
            classification=Ranking.get_valutation_from_area(area_cm)
        )
        self.wounds.append(wound)

    @staticmethod
    def calculate_cm(pixels, ratio) -> float:
        return pixels / ratio
