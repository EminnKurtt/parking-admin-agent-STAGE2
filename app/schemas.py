from typing import Literal
from pydantic import BaseModel, Field


class ReservationRequest(BaseModel):
    """Schema for a reservation approval request."""
    request_id: str = Field(..., description="Unique identifier for the request")
    user_name: str = Field(..., description="Name of the user requesting reservation")
    car_number: str = Field(..., description="Car license plate number")
    reservation_period: str = Field(..., description="Duration of the reservation")
    formatted_message: str = Field(..., description="LLM-generated professional message")
    status: Literal["PENDING", "APPROVED", "REJECTED"] = "PENDING"


class StatusResponse(BaseModel):
    """Schema for status check response."""
    request_id: str
    status: str
