from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from backend.users.model.base import Base
from backend.common.model.mixin import CRUDMixin
from backend.users.model.user import User


class RefreshToken(Base, CRUDMixin):
    '''
    Refresh token instance

    Attributes
    ----------
    user_id : int
        id of the user associated with the record
    token : str
        valid refresh token
    '''
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        "user_id", ForeignKey('user.id'), nullable=False
    )
    token: Mapped[str] = mapped_column(
        "token", String(length=512), nullable=False
    )

    user: Mapped[User] = relationship(
        'User', back_populates='refresh_tokens'
    )
