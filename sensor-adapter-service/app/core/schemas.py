from datetime import datetime

from pydantic import BaseModel


class CoordinateResponse(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime
    light: float | None = None
