from typing import List, Annotated

from fastapi import APIRouter, Depends, Path, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.util import get_object_or_raise_404, create_object_or_raise_400, \
    update_object_or_raise_400, process_query_params
from backend.users.util import get_password_hash, auth_user, auth_admin
from backend.users.model import User
from backend.users.schema import UserSchema, PartialUserSchema, UserResponse
from backend.users.service.db_service import get_session


router = APIRouter(
    prefix="/v1/user",
    tags=['User']
)


@router.get(
    "/", status_code=status.HTTP_200_OK, dependencies=[Depends(auth_admin)],
    response_model=List[UserResponse], response_model_exclude_unset=True
)
async def read_all_users(
    request: Request,
    db_session: AsyncSession = Depends(get_session)
):
    query_params: dict = process_query_params(request)
    return [
        UserResponse(**user.__dict__).model_dump(exclude_unset=True)
        async for user in User.read_all(
            db_session,
            **query_params
        )
    ]


@router.get(
    "/me", status_code=status.HTTP_200_OK,
    response_model=UserResponse, response_model_exclude_unset=True
)
async def read_user_me(
    request: Request,
    current_user: Annotated[UserSchema, Depends(auth_user)]
):
    return current_user


@router.get(
    "/{user_id}", status_code=status.HTTP_200_OK,
    response_model=UserResponse, response_model_exclude_unset=True
)
async def read_user(
    request: Request,
    current_user: Annotated[UserSchema, Depends(auth_user)],
    user_id: int = Path(...),
    db_session: AsyncSession = Depends(get_session)
):
    if (user_id == current_user['id']) or current_user['is_admin']:
        user = await get_object_or_raise_404(
            db_session, User, user_id,
        )
        return UserResponse(**user.__dict__).model_dump(exclude_unset=True)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )


@router.post(
    "/register", status_code=status.HTTP_201_CREATED,
    response_model=UserResponse, response_model_exclude_unset=True
)
async def create_user(
    request: Request,
    payload: UserSchema, db_session: AsyncSession = Depends(get_session)
):
    payload.password = await get_password_hash(payload.password)
    user = await create_object_or_raise_400(db_session, User, **payload.model_dump())
    return UserResponse(**user.__dict__).model_dump(exclude_unset=True)


@router.patch(
    "/{user_id}", status_code=status.HTTP_200_OK,
    response_model=UserResponse, response_model_exclude_unset=True
)
async def update_user(
    request: Request,
    payload: PartialUserSchema,
    current_user: Annotated[UserSchema, Depends(auth_user)],
    user_id: int = Path(...),
    db_session: AsyncSession = Depends(get_session)
):
    if (user_id == current_user['id'] and payload.is_admin is None) or current_user['is_admin']:
        user = await get_object_or_raise_404(db_session, User, user_id)
        if payload.password:
            payload.password = await get_password_hash(payload.password)
        await update_object_or_raise_400(db_session, User, user, **payload.model_dump())
        return UserResponse(**user.__dict__).model_dump(exclude_unset=True)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )


@router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    request: Request,
    current_user: Annotated[UserSchema, Depends(auth_user)],
    user_id: int = Path(...), db_session: AsyncSession = Depends(get_session)
):
    if (user_id == current_user['id']) or current_user['is_admin']:
        user = await get_object_or_raise_404(db_session, User, user_id)
        await User.delete(db_session, user)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
