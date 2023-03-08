import asyncio

from sqlalchemy import Column, Integer, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select


PG_DSN = 'postgresql+asyncpg://postgres:1@localhost:5432/async_netology'

engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class SwapiPeople(Base):

    __tablename__ = 'swapi_people'

    id = Column(Integer, primary_key=True, autoincrement=True)
    json = Column(JSON)


async def main():
    async with Session() as session:
        selected = select(SwapiPeople)
        result = await session.execute(selected)
        for people in result.scalars():
            print(people.id)

if __name__ == '__main__':
    asyncio.run(main())
