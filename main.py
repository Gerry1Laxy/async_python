import asyncio
from datetime import datetime

import aiohttp
from more_itertools import chunked

from models import SwapiPeople, engine, Session, Base


CHUNK_SIZE = 10
LAST_PEOPLE = 50


async def get_people(people_id: int, ses):
    async with ses.get(f'https://swapi.dev/api/people/{people_id}') as response:
        return await response.json()
    # session = aiohttp.ClientSession()
    # response = await session.get(f'https://swapi.dev/api/people/{people_id}')
    # response_json = await response.json()
    # await session.close()
    # return response_json

async def paste_to_db(items):
    items = [SwapiPeople(json=item) for item in items]
    async with Session() as session:
        session.add_all(items)
        await session.commit()

async def main():
    start = datetime.now()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = aiohttp.ClientSession()
    coroutins = (get_people(i, session) for i in range(1, LAST_PEOPLE))
    for chunk in chunked(coroutins, CHUNK_SIZE):
        results = await asyncio.gather(*chunk)
        asyncio.create_task(paste_to_db(results))
        break
    # result = await asyncio.gather(*result)
    await session.close()
    for task in asyncio.all_tasks():
        if task != asyncio.current_task():
            await task
    print(results)

    print(datetime.now() - start)


asyncio.run(main())
