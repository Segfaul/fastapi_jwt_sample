import os
from typing import Annotated
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.users.model import User
from backend.users.service.db_service import get_session
from backend.users.schema import UserResponse

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
# 7 days refresh / 15 minutes access
REFRESH_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_EXPIRE_MINUTES = 15

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def auth_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: AsyncSession = Depends(get_session)
):
    """
    OAUTH Depency to check if user is authenticated

    :param token : user's JWT token saved in Headers
    :type token : str
    :param db_session : database async session instance
    :type db_session : AsyncSession
    :returns : user instance
    :rtype : html.HtmlElement | None
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e
    user = [user async for user in User.read_all(db_session, id=user_id)]
    if user is None or len(user) == 0:
        raise credentials_exception
    return UserResponse(**user[0].__dict__).model_dump(exclude_unset=True)


async def auth_admin(
    current_user: Annotated[UserResponse, Depends(auth_user)]
):
    """
    Dependency to check if the current user has admin permissions.

    :param current_user: The current authenticated user.
    :type current_user: UserResponse
    :raises HTTPException: If the user is not an admin.
    :returns: The current authenticated user.
    :rtype: UserResponse
    """
    permission_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )
    if not current_user["is_admin"]:
        raise permission_exception
    return current_user


def verify_password(plain_password, hashed_password):
    """
    Verify plain text password against hashed one.

    :param plain_password: plain text password.
    :type plain_password: str
    :param hashed_password: hashed password.
    :type hashed_password: str
    :returns: True if the password matches, False otherwise.
    :rtype: bool
    """
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_byte_enc)


async def get_password_hash(password):
    """
    Hash plain text password using bcrypt.

    :param password: plain text password.
    :type password: str
    :returns: hashed password.
    :rtype: str
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create JWT access token.

    :param data: data to encode in token.
    :type data: dict
    :param expires_delta: time delta for token expiration.
    :type expires_delta: timedelta | None
    :returns: encoded JWT token.
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(db_session: AsyncSession, username: str, password: str):
    """
    Authenticate user by username and password.

    :param db_session: database session.
    :type db_session: AsyncSession
    :param username: user's username.
    :type username: str
    :param password: user's password.
    :type password: str
    :returns: authenticated user or False if authentication fails.
    :rtype: User | bool
    """
    user_instance = [user async for user in User.read_all(db_session, username=username)]
    if not user_instance:
        return False
    if not verify_password(password, user_instance[0].password):
        return False
    return user_instance[0]
