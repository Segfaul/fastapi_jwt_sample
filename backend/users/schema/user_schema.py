from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from backend.common.util import _AllOptionalMeta
from backend.users.schema.auth_schema import IndependentRefreshTokenSchema


class UserSchema(BaseModel):
    """
    Pydantic schema for User table data.

    Attributes:
    ----------
    - username: username.
    - password: user's password.
    """
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class PartialUserSchema(UserSchema, metaclass=_AllOptionalMeta):
    """
    Pydantic schema for User table data (PATCH).
    """
    is_admin: Optional[bool] = None


class IndependentUserSchema(UserSchema):
    """
    Pydantic schema for User table data (subqueries).

    Attributes:
    ----------
    - id: unique identifier of the user.
    - username: username.
    - password: user's password.
    """
    id: int
    is_admin: bool
    created_at: datetime


class UserResponse(IndependentUserSchema):
    """
    Pydantic schema for User table data.

    Attributes:
    ----------
    - id: unique identifier of the user.
    - username: username.
    - password: user's password.
    - refresh_tokens: refresh tokens related to the user.
    """
    refresh_tokens: Optional[List[IndependentRefreshTokenSchema]] = None
