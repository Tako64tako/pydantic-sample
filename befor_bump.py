from typing import Generic, List, Optional
from pydantic import BaseModel, Field, validator, Extra
from pyparsing import TypeVar
from pydantic.generics import GenericModel

# 1. バリデーター使用例
class UserValidatorExample(BaseModel):
    name: str

    @validator("name")
    def validate_name(cls, value):
        if not value.isalpha():
            raise ValueError("Name must only contain letters")
        return value


# 2. 基本的なデータモデル例
class UserBasicExample(BaseModel):
    name: Optional[str]  # Optionalを使用した型定義


# 3. Extra.forbidを使用したデータモデル例
class User(BaseModel):
    name: str

    class Config:
        extra = Extra.forbid


# 4. Fieldを使用したデータモデル例
class UserField(BaseModel):
    name: List[str] = Field(..., min_items=1) # min_items -> min_length


# 5. GenericModelの使用例
T = TypeVar('T')

class UserGeneric(GenericModel, Generic[T]):
    name: str

# 6. Rootモデルの使用例
class Users(BaseModel):
    __root__ = List[User]
