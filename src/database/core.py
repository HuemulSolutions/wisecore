from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from contextlib import asynccontextmanager
from .models import Base
from typing import AsyncGenerator
from sqlalchemy.orm import sessionmaker
from src.config import config

DATABASE_URL = config.DATABASE_URL

engine = create_async_engine(DATABASE_URL)

session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@asynccontextmanager
async def get_graph_session() -> AsyncGenerator[AsyncSession, None]:
    async with session() as db_session:
        yield db_session
        
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session() as db_session:
        yield db_session

async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database created successfully.")
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(create_database())