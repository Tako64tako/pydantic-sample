from typing import Generic, List, Optional
from pydantic import field_validator, RootModel, ConfigDict, BaseModel, Field
from pyparsing import TypeVar

# 1. バリデーター使用例
class UserValidatorExample(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value.isalpha():
            raise ValueError("Name must only contain letters")
        return value


# 2. 基本的なデータモデル例
class UserBasicExample(BaseModel):
    name: Optional[str] = None  # Optionalを使用した型定義


# 3. Extra.forbidを使用したデータモデル例
class User(BaseModel):
    name: str
    model_config = ConfigDict(extra="forbid")


# 4. Fieldを使用したデータモデル例
class UserField(BaseModel):
    name: List[str] = Field(..., min_length=1) # min_items -> min_length


# 5. GenericModelの使用例
T = TypeVar('T')

class UserGeneric(BaseModel, Generic[T]):
    name: str

# 6. Rootモデルの使用例
class Users(RootModel[List[User]]):
    pass
