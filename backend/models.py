from pydantic import BaseModel, Field, EmailStr
from typing import Annotated, Optional

class Customer(BaseModel):
    name: Annotated[str, Field(..., description="Full name of the user")]
    email: Annotated[EmailStr, Field(..., description="Email of the user")]
    phone: Annotated[int, Field(..., gt = 5999999999, lt= 10000000000, description = "10 digit phone number of the user")]
    business_name: Annotated[str, Field(..., description="Name of the Business of the Customer")]

