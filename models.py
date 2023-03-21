from masks_manager.masks_manager import MasksManager
from wounds_finder.wounds_finder import WoundsFinder
from grabcut.grabcut import GrabCut
from typing import Tuple, List
from custom.mask_image import MaskImage
from custom.classes import Wound
from custom.functions import get_img_from_file, get_mask_image_from_file
from mrcnn.mrcnn import MRCNN


def load_mrcnn_model() -> None:
    """Loads the model inside of the class attribute MRCNN.model, it is called before starting the uvicorn server"""
    MRCNN.load_model()

def define_mask_manager(file, api_key: str) -> MasksManager:
    masks_manager = MasksManager(
        img=get_img_from_file(file),
        user_id=api_key
    )
    return masks_manager

def get_mrcnn_mask_img(file, api_key: str) -> MaskImage:
    masks_manager = define_mask_manager(file, api_key)
    return masks_manager.get_mrcnn()

def get_grabcut_mask_img(file, api_key: str) -> MaskImage:
    masks_manager = define_mask_manager(file, api_key)
    return masks_manager.get_grabcut()

def get_grabcut_from_mask(file, mask_image: MaskImage) -> MaskImage:
    ...

def get_mrcnn_and_grabcut_masks_img(file, api_key: str) -> Tuple[MaskImage, MaskImage]:
    mask_manager = define_mask_manager(file, api_key)
    return mask_manager.get_mrcnn_and_grabcut()

def get_wounds_from_mask_file(file, ratio: float) -> List[Wound]:
    mask = MaskImage(get_mask_image_from_file(file))
    return get_wounds_from_mask_img(mask, ratio)

def get_wounds_from_mask_img(mask_image: MaskImage, ratio: float) -> List[Wound]:
    wounds_finder = WoundsFinder(ratio)
    return wounds_finder.find_wounds(mask_image)
