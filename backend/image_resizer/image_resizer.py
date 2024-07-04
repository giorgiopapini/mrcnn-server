import cv2
import numpy as np


class ImageResizer:

    @staticmethod
    def try_format_img(img: np.ndarray, size: int) -> np.ndarray:
        """ Resize image for MRCNN execution """
        if ImageResizer.image_respects_sizes(img, size):
            return img
        return ImageResizer.get_formatted_img(img, size)
    
    @staticmethod
    def image_respects_sizes(img: np.ndarray, size: int) -> bool:
        if img.shape[0] == size and img.shape[1] == size:
            return True
        return False

    @staticmethod
    def get_formatted_img(img: np.ndarray, size: int) -> np.ndarray:
        height = img.shape[0]
        width = img.shape[1]
        new_img = None
        if height > width:
            delta = height - width
            new_img = cv2.copyMakeBorder(img, 0, 0, 0, delta, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        else:
            delta = width - height
            new_img = cv2.copyMakeBorder(img, 0, delta, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        return cv2.resize(new_img, (size, size))
    
    @staticmethod
    def resize_mask_to_original_size(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
        height = img.shape[0]
        width = img.shape[1]
        size = height if height > width else width
        return cv2.resize(mask, (size, size))
