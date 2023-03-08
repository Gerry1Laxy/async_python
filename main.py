import asyncio
from datetime import datetime

import aiohttp
from more_itertools import chunked

from models import SwapiPeople, engine, Session, Base


CHUNK_SIZE = 10
LAST_PEOPLE = 50

rewrited_filds = {
    'films': 'title',
    # 'homeworld': None,
    # 'species': None,
    # 'starships': None,
    # 'vehicles': None
}


async def get_people(
        ses: Session, people_id: int = None, subqueries: str = None
    ):
    if subqueries:
        url = subqueries
    else:
        url = f'https://swapi.dev/api/people/{people_id}'
    async with ses.get(url) as response:
        response_json = await response.json()
        if people_id:
            # await rewrite_item(ses, response_json)
            for field, name in rewrited_filds.items():
                items = await asyncio.gather(
                    *(get_people(ses, subqueries=subq) for subq in response_json[field])
                )
                response_json[field] = ', '.join([item[name] for item in items])
            # films = await asyncio.gather(*(get_people(ses, subqueries=subq) for subq in response_json['films']))
            # print(', '.join([film['title'] for film in films]))
        return response_json
    # session = aiohttp.ClientSession()
    # response = await session.get(f'https://swapi.dev/api/people/{people_id}')
    # response_json = await response.json()
    # await session.close()
    # return response_json

async def rewrite_item(ses, people):
    for field, name in rewrited_filds.items():
        items = await asyncio.gather(
            *(get_people(ses, subqueries=subq) for subq in people[field])
        )
        people[field] = ', '.join([item[name] for item in items])
    # for people in peoples:
    #     films = await asyncio.gather(*(get_people(ses, subqueries=subq) for subq in people['films']))
    #     print(', '.join([film['title'] for film in films]))

async def paste_to_db(items):
    # checking items
    # for item in items:
    #     print(item)
    items = [SwapiPeople(json=item) for item in items]
    async with Session() as session:
        session.add_all(items)
        await session.commit()

async def main():
    start = datetime.now()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = aiohttp.ClientSession()
    coroutins = (get_people(session, i) for i in range(1, LAST_PEOPLE))
    for chunk in chunked(coroutins, CHUNK_SIZE):
        results = await asyncio.gather(*chunk)
        # await rewrite_item(session, results)
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