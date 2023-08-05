from pydantic import BaseModel, Field
from typing import Tuple, List, Optional


class Wound(BaseModel):
    contour: List = Field(default_factory=list)
    perimeter: float
    area: float
    center_coordinates: Tuple[float, float]
    classification: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "contour": [[[300, 344]], [[421, 490]]],
                "perimeter": 12.2,
                "area": 9.2,
                "center_coordinates": (123.4, 110.1),
                "classification": '1'
            }
        }

class Mask(BaseModel):
    contour: List = Field(default_factory=list)
    perimeter_px: float = Field(description="Perimeter in pixels")
    area_px: float = Field(description="Area in pixels")

    class Config:
        schema_extra = {
            "example": {
                "contour": [[[300, 344]], [[421, 490]]],
                "perimeter_px": 2065.7,
                "area_px": 166125.5
            }
        }

class User(BaseModel):
    first_name: str
    last_name: str
    email: str = Field(exclude=True)
    password: str = Field(exclude=True)