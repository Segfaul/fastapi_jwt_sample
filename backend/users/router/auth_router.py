from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status, Request, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.util import create_object_or_raise_400
from backend.users.util import authenticate_user, create_access_token, \
    REFRESH_TOKEN_EXPIRE_DAYS, ACCESS_TOKEN_EXPIRE_MINUTES, \
    auth_user
from backend.users.model import RefreshToken
from backend.users.schema import TokenSchema, UserSchema
from backend.users.service.db_service import get_session

router = APIRouter(
    prefix="/v1/auth",
    tags=['Auth']
)


@router.post("/token", status_code=status.HTTP_201_CREATED)
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: AsyncSession = Depends(get_session)
) -> TokenSchema:
    user = await authenticate_user(
        db_session, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = {"user_id": user.id, "username": user.username, "is_admin": user.is_admin}
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        data=token_data,
        expires_delta=refresh_token_expires
    )
    await create_object_or_raise_400(
        db_session, RefreshToken, user_id=user.id, token=refresh_token
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS
    )

    return TokenSchema(refresh_token=refresh_token, access_token=access_token, token_type="bearer")


@router.post("/refresh", status_code=status.HTTP_201_CREATED)
async def refresh_access_token(
    request: Request,
    response: Response,
    db_session: AsyncSession = Depends(get_session)
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify that the refresh token is in the database
    refresh_token_instance = [
        refresh_token async for refresh_token in RefreshToken.read_all(
            db_session, token=refresh_token
        )
    ]
    if len(refresh_token_instance) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = await auth_user(refresh_token, db_session)

    # Generate a new access token
    token_data = {
        "user_id": user['id'],
        "username": user['username'],
        "is_admin": user['is_admin']
    }
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    current_user: Annotated[UserSchema, Depends(auth_user)],
    db_session: AsyncSession = Depends(get_session)
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Delete the specific refresh token from the database
    refresh_token_instance = [
        refresh_token async for refresh_token in RefreshToken.read_all(
            db_session, token=refresh_token
        )
    ]
    if len(refresh_token_instance) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    await RefreshToken.delete(db_session, refresh_token_instance[0])

    # Clear the refresh token cookie
    response.delete_cookie("refresh_token")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
