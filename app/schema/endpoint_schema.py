# endpoint_schema.py

## lib
from pydantic import BaseModel, Field


### signup


### login
class LoginSchema(BaseModel):
    name:str = Field( default=..., min_length=3, max_length=45 )
    password:str = Field( default=..., min_length=3, max_length=45 )



class EmailSchema(BaseModel):
    email:str = Field( default=..., min_length=3, max_length=45 )


class SignSchema(BaseModel):
    name:str = Field( default=..., min_length=3, max_length=45 )
    password:str = Field( default=..., min_length=3, max_length=45 )
    email:str = Field( default=..., min_length=3, max_length=45 )