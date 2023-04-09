from typing import Optional
from pydantic import BaseModel

class SignInfor(BaseModel):
    email : Optional[str]
    pw : Optional[str]

class AccountInfor(BaseModel):
    price : Optional[int]
    memo : str
    date : Optional[str]