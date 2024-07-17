from pydantic import BaseModel, ConfigDict

from backend.common.util import _AllOptionalMeta


class AccessTokenSchema(BaseModel):
    """
    Pydantic schema for AccessToken

    Attributes:
    ----------
    - access_token: generated access token according to user's entry.
    - token_type: token generated type.
    """
    access_token: str
    token_type: str

    model_config = ConfigDict(from_attributes=True)


class TokenSchema(AccessTokenSchema):
    """
    Pydantic schema for AccessToken

    Attributes:
    ----------
    - refresh_token: generated refresh token according to user's entry.
    - access_token: generated access token according to user's entry.
    - token_type: token generated type.
    """
    refresh_token: str


class RefreshTokenSchema(BaseModel):
    """
    Pydantic schema for RefreshToken table data.

    Attributes:
    ----------
    - user_id: identifier of the user associated with the entry.
    - token: generated refresh token according to user's entry.
    """
    user_id: int
    token: str

    model_config = ConfigDict(from_attributes=True)


class PartialRefreshTokenSchema(RefreshTokenSchema, metaclass=_AllOptionalMeta):
    """
    Pydantic schema for RefreshToken table data (PATCH).
    """


class IndependentRefreshTokenSchema(RefreshTokenSchema):
    """
    Pydantic schema for RefreshToken table data (subqueries).

    Attributes:
    ----------
    - id: unique identifier of the token.
    - user_id: identifier of the user associated with the entry.
    - token: generated refresh token according to user's entry.
    """
    id: int


class RefreshTokenResponse(IndependentRefreshTokenSchema):
    """
    Pydantic schema for RefreshToken table data.

    Attributes:
    ----------
    - id: unique identifier of the token.
    - user_id: identifier of the user associated with the entry.
    - token: generated refresh token according to user's entry.
    """
