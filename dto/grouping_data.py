from pydantic import BaseModel
from typing import List


class Color(BaseModel):
    '''
    Color representation as RGB values.
    '''
    R: int
    G: int
    B: int


class GroupInfo(BaseModel):
    '''
    Information about a color: RGB and percentage of pixels across image.
    '''
    color: Color
    images: str


class VehicleGroupingRequest(BaseModel):
    '''
    Vehicle grouping request.
    '''
    images_path: str


class VehicleGroupingResponse(BaseModel):
    '''
    Image groups response.
    '''
    vehicle_groups: List[GroupInfo]