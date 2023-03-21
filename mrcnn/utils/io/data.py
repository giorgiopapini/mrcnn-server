import numpy as np
from typing import List, Union


class DataGen:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def generate_batch(self, img: np.ndarray) -> Union[np.ndarray, List]:
        image_batch = []

        if img.shape[0] == self.x and img.shape[1] == self.y:
            image_batch.append(img.astype("float32"))
        else:
            print(f"The input image shape is not {self.x}x{self.y}")

        if image_batch:
            image_batch = normalize(np.array(image_batch))
        return image_batch


def normalize(arr: np.ndarray) -> np.ndarray:
    diff = np.amax(arr) - np.amin(arr)
    diff = 255 if diff == 0 else diff
    arr = arr / np.absolute(diff)
    return arr

