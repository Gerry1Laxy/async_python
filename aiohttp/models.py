from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from aiohttp.web import middleware, Request


PG_DSN = 'postgresql+asyncpg://postgres:1@localhost:5432/hw_aiohttp'

engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def orm_context(app):
    print('START ORM CTX')

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield
    
    await engine.dispose()

    print('FINISH ORM CTX')

@middleware
async def session_middleware(requests: Request, handler):
    
    async with Session() as session:
        requests['session'] = session
        return await handler(requests)

class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())

