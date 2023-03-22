import numpy as np
from PIL import Image, ImageOps
from io import BytesIO
import cv2


def get_img_from_file(file) -> np.ndarray:
    data = file.file.read()
    image = Image.open(BytesIO(data))
    image = __try_rotate_img(image)  # this line rotates the img based on exif tag
    np_array = np.array(image)
    return cv2.cvtColor(np_array, cv2.COLOR_BGR2RGB)

def __try_rotate_img(image):
    try:
        return ImageOps.exif_transpose(image)
    except:
        return image

def get_mask_image_from_file(file) -> np.ndarray:
    data = file.file.read()
    image = np.array(Image.open(BytesIO(data)), np.uint8)
    if len(image.shape) < 3:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
