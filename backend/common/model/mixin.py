from typing import AsyncIterator

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, Load
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDMixin:
    '''
    CRUD mixin class

    Methods
    ----------
    create(session: AsyncSession, **kwargs):
        Creates and returns a new object in the table.
    read_all(session: AsyncSession, **kwargs):
        Returns all objects in the table.
    read_by_id(session: AsyncSession, item_id: int, **kwargs):
        Returns an object by its ID.
    update(session: AsyncSession, item: T, **kwargs):
        Updates an object.
    delete(session: AsyncSession, item: T):
        Deletes an object.
    '''

    @classmethod
    def apply_includes(cls, stmt, *args, **kwargs):
        '''
        Apply include and filter options to the statement.

        Parameters
        ----------
        stmt: SQL statement
            SQL statement to modify.
        *args: tuple
            positional arguments for includes and orders.
        **kwargs: dict
            keyword arguments for includes and filters.

        Returns
        -------
        stmt
            modified SQL statement.
        '''
        if kwargs:
            for key, value in kwargs.items():
                if key.startswith('include_'):
                    related_attr = getattr(cls, key[8:], None)
                    if related_attr and int(value):
                        stmt = stmt.options(selectinload(related_attr))
                else:
                    desc = key[0] == '_'
                    related_attr = getattr(cls, key[1:] if desc else key, None)
                    if related_attr:
                        if len(str(value)) > 0:
                            stmt = stmt.filter(related_attr == value)
                        else:
                            stmt = stmt.order_by(related_attr.desc() if desc else related_attr)

        if args:
            for arg in args:
                if isinstance(arg, Load):
                    stmt = stmt.options(arg)
                elif isinstance(arg, str):
                    desc = arg[0] == '_'
                    related_attr = getattr(cls, arg[1:] if desc else arg, None)
                    if related_attr:
                        stmt = stmt.order_by(related_attr.desc() if desc else related_attr.asc())
        return stmt

    @classmethod
    async def read_all(cls, session: AsyncSession, *args, **kwargs) -> AsyncIterator:
        '''
        Read all objects from the table.

        Parameters
        ----------
        session: AsyncSession
            database session.
        *args: tuple
            positional arguments for includes and orders.
        **kwargs: dict
            keyword arguments for includes, filters, limits, and offsets.

        Returns
        -------
        AsyncIterator
            iterator of all objects.
        '''
        stmt = select(cls)
        stmt = cls.apply_includes(stmt, *args, **kwargs)
        limit = int(kwargs.get('limit')) if str(kwargs.get('limit')).isdigit() else None
        offset = int(kwargs.get('offset')) if str(kwargs.get('offset')).isdigit() else 0
        stream = await session.stream_scalars(
            stmt.order_by(cls.id).limit(limit).offset(offset)
        )
        async for row in stream.unique():
            yield row

    @classmethod
    async def read_by_id(cls, session: AsyncSession, item_id: int, *args, **kwargs):
        '''
        Read an object by its ID.

        Parameters
        ----------
        session: AsyncSession
            database session.
        item_id: int
            ID of an object.
        *args: tuple
            positional arguments for includes and orders.
        **kwargs: dict
            keyword arguments for includes and filters.

        Returns
        -------
            object with the specified ID.
        '''
        stmt = select(cls).where(cls.id == item_id)
        stmt = cls.apply_includes(stmt, *args, **kwargs)
        return await session.scalar(stmt.order_by(cls.id))

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        '''
        Create a new object.

        Parameters
        ----------
        session: AsyncSession
            database session.
        **kwargs: dict
            attributes of the object.

        Returns
        -------
            created object.

        Raises
        ------
        RuntimeError
            if object creation fails.
        '''
        item = cls(**kwargs)
        session.add(item)
        await session.commit()
        new_item = await cls.read_by_id(session, item_id=item.id)
        if new_item:
            return new_item
        else:
            raise RuntimeError("Failed to create item")

    @classmethod
    async def update(cls, session: AsyncSession, item, **kwargs):
        '''
        Update an existing object.

        Parameters
        ----------
        session: AsyncSession
            database session.
        item: instance
            object to update.
        **kwargs: dict
            attributes to update.

        Returns
        -------
            updated object.
        '''
        if item:
            for key, value in kwargs.items():
                if hasattr(item, key) and value is not None:
                    setattr(item, key, value)
            await session.commit()
        return item

    @classmethod
    async def delete(cls, session: AsyncSession, item) -> None:
        '''
        Delete an object.

        Parameters
        ----------
        session: AsyncSession
            database session.
        item: instance
            object to delete.
        '''
        await session.delete(item)
        await session.commit()
