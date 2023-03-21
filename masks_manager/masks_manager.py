import cv2
import numpy as np
from typing import Tuple

from mrcnn.mrcnn import MRCNN
from grabcut.grabcut import GrabCut
from image_resizer.image_resizer import ImageResizer
from custom.mask_image import MaskImage

class MasksManager:
    IMAGES_PATH: str = "mrcnn\\data\\original_images\\"
    MRCNN_PATH: str = "mrcnn\\data\\mrcnn_images\\"
    
    def __init__(self, img: np.ndarray, user_id: str) -> None:
        self.img = self.__save_and_load_img(img, f"{self.IMAGES_PATH}{user_id}.png")
        self.user_id = user_id
        self.mrcnn_compatible_img = self.__get_mrcnn_compatible_img()

    def __save_and_load_img(self, img: np.ndarray, path: str) -> np.ndarray:
        cv2.imwrite(path, img)
        return cv2.imread(path)

    def __get_mrcnn_compatible_img(self) -> np.ndarray:
        if self.img is not None:
            return ImageResizer.get_formatted_img(self.img, MRCNN.IMAGE_SIZE)
        return np.array(...)

    def get_mrcnn(self) -> MaskImage:
        mask = self.__create_mrcnn_mask()
        return MaskImage(ImageResizer.resize_mask_to_original_size(self.img, mask))
    
    def get_grabcut(self) -> MaskImage:
        _, grabcut_mask = self.__create_mrcnn_and_grabcut_mask()
        return MaskImage(ImageResizer.resize_mask_to_original_size(self.img, grabcut_mask))

    def get_mrcnn_and_grabcut(self) -> Tuple[MaskImage, MaskImage]:
        mrcnn_mask, grabcut_mask = self.__create_mrcnn_and_grabcut_mask()
        resized_mrcnn = MaskImage(ImageResizer.resize_mask_to_original_size(self.img, mrcnn_mask))
        resized_grabcut = MaskImage(ImageResizer.resize_mask_to_original_size(self.img, grabcut_mask))
        return resized_mrcnn, resized_grabcut

    def __create_mrcnn_mask(self) -> np.ndarray:
        raw_mask = MRCNN.predict_mask(self.mrcnn_compatible_img)
        raw_mask = self.__save_and_load_img(
            raw_mask, 
            f"{self.MRCNN_PATH}{self.user_id}.png"
        ).astype("uint8") * 255

        return cv2.cvtColor(raw_mask, cv2.COLOR_BGR2GRAY)

    def __create_mrcnn_and_grabcut_mask(self) -> Tuple[np.ndarray, np.ndarray]:
        mrcnn_mask = self.__create_mrcnn_mask()
        grabcut_mask = GrabCut.get_refined_mask(self.mrcnn_compatible_img, mrcnn_mask)
        return mrcnn_mask, grabcut_mask
