import asyncio
from datetime import datetime

import aiohttp
from more_itertools import chunked

from models import SwapiPeople, engine, Session, Base


CHUNK_SIZE = 10
LAST_PEOPLE = 83

rewrited_filds = {
    'films': 'title',
    'species': 'name',
    'starships': 'name',
    'vehicles': 'name'
}
deleted_filds = (
    'created',
    'edited',
    'url'
)

cashe_req = dict()

async def get_item(
        ses: Session, people_id: int = None, subqueries: str = None
    ):
    if subqueries:
        chek_cashe = cashe_req.get(subqueries)
        if chek_cashe:
            return chek_cashe
        url = subqueries
    else:
        url = f'https://swapi.dev/api/people/{people_id}'
    async with ses.get(url) as response:
        response_json = await response.json()
        if people_id and response.status == 200:
            response_json['id'] = people_id
            await rewrite_fields(ses, response_json)
            await delete_fields(response_json)
        else:
            cashe_req[subqueries] = response_json
        return response_json

async def rewrite_fields(ses: Session, people):
    homeworld = await get_item(ses, subqueries=people['homeworld'])
    people['homeworld'] = homeworld['name']
    for field, name in rewrited_filds.items():
        items = await asyncio.gather(
            *(get_item(ses, subqueries=subq) for subq in people[field])
        )
        people[field] = ', '.join([item[name] for item in items])

async def delete_fields(people):
    for field in deleted_filds:
        people.pop(field)

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
    coroutins = (get_item(session, i) for i in range(1, LAST_PEOPLE))
    for chunk in chunked(coroutins, CHUNK_SIZE):
        results = await asyncio.gather(*chunk)
        asyncio.create_task(paste_to_db(results))
        # break
    await session.close()
    for task in asyncio.all_tasks():
        if task != asyncio.current_task():
            await task
    
    print(results)

    print(datetime.now() - start)


asyncio.run(main())
