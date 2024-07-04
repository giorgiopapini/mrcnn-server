from pydantic import BaseModel, Field
from typing import List
from custom.classes import Wound, Mask


class MultipleModelsWoundsResponse(BaseModel):
    mrcnn_wounds: List[Wound] = Field(default_factory=list)
    grabcut_wounds: List[Wound] = Field(default_factory=list)


class MultipleModelsMasksResponse(BaseModel):
    mrcnn_masks: List[Mask] = Field(default_factory=list)
    grabcut_masks: List[Mask] = Field(default_factory=list)