from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, String, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column

from backend.common.config import MOSCOW_TZ
from backend.users.model.base import Base
from backend.common.model.mixin import CRUDMixin

if TYPE_CHECKING:
    from backend.users.model.refresh_token import RefreshToken
else:
    RefreshToken = "RefreshToken"


class User(Base, CRUDMixin):
    '''
    User instance

    Attributes
    ----------
    username : str
        username
    password : str
        hashed password
    is_admin : bool
        does user have admin rights
    created_at : datetime
        date the request was created
    '''
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    username: Mapped[str] = mapped_column(
        "username", String(length=64), nullable=False, unique=True
    )
    password: Mapped[str] = mapped_column(
        "password", String(length=255), nullable=False
    )
    is_admin: Mapped[Boolean] = mapped_column(
        "is_admin", Boolean(), default=False, nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        "created_at", DateTime(timezone=True),
        default=lambda: datetime.now(MOSCOW_TZ)
    )

    refresh_tokens: Mapped[List[RefreshToken]] = relationship(
        'RefreshToken', cascade='all, delete-orphan', back_populates='user'
    )
