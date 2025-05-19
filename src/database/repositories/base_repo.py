from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, TypeVar, Generic

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.model = model
        self.session = session
        
    async def add(self, instance: T) -> T:
        self.session.add(instance)
        await self.session.commit()
        
        return instance

    async def get_by_id(self, id: str) -> T:
        return await self.session.get(self.model, id)
    
    async def delete(self, instance: T) -> None:
        await self.session.delete(instance)
        await self.session.commit()
    
    