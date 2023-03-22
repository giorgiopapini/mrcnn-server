from keras.models import load_model
import numpy as np
from typing import Any

from .models.deeplab import Deeplabv3, relu6, BilinearUpsampling, DepthwiseConv2D
from .utils.learning.metrics import dice_coef, precision, recall
from .utils.io.data import DataGen
from image_resizer.image_resizer import ImageResizer

class MRCNN:
    MODEL_PATH = "./mrcnn/training_history/2019-12-19 01%3A53%3A15.480800.hdf5"
    IMAGE_SIZE = 224
    model: Any = None

    @staticmethod
    def load_model():
        MRCNN.model = load_model(
            MRCNN.MODEL_PATH, 
            custom_objects={
                'recall': recall,
                'precision': precision,
                'dice_coef': dice_coef,
                'relu6': relu6,
                'DepthwiseConv2D': DepthwiseConv2D,
                'BilinearUpsampling': BilinearUpsampling
            }
        )

    @staticmethod
    def predict_mask(img: np.ndarray) -> np.ndarray:
        img = ImageResizer.try_format_img(img, MRCNN.IMAGE_SIZE)  # It resizes the image to match the IMAGE_SIZE
        data_gen = DataGen(x=MRCNN.IMAGE_SIZE, y=MRCNN.IMAGE_SIZE)
        image_batch = data_gen.generate_batch(img)
        prediction = MRCNN.model.predict(image_batch, verbose=1)
        mask = prediction[0] * 255.
        return mask
