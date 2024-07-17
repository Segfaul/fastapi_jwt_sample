from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.util.endpoint_util import create_object_or_raise_400, \
    update_object_or_raise_400


async def get_or_create(db_session: AsyncSession, item, defaults: dict = None, **kwargs):
    """
    Response pattern for db models if item already exists.\n
    Also updates the instance with `defaults` param
    """
    stmt = select(item).filter_by(**kwargs)
    instance = (await db_session.execute(stmt)).scalar_one_or_none()
    if instance:
        # Check if any of the default values differ from the current values
        if defaults:
            updated_params: dict[item] = {}
            for key, value in defaults.items():
                if getattr(instance, key) != value:
                    updated_params[key] = value
            if updated_params:
                await update_object_or_raise_400(db_session, item, instance, **updated_params)
        return instance

    params = {**kwargs, **defaults} if defaults else kwargs
    return await create_object_or_raise_400(db_session, item, **params)
