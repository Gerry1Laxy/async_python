import asyncio
from aiohttp import ClientSession


async def main():

    async with ClientSession() as session:

        response = await session.post(
            'http://localhost:8080/users/',
            json={
                'name': 'user_1',
                'password': '4321',
            }
        )
        print(response.status)
        print(await response.json())
        response = await session.patch(
            'http://localhost:8080/users/1',
            json={
                'name': 'user_2',
                # 'password': '43210',
            }
        )
        print(response.status)
        print(await response.json())
        response = await session.get(
            'http://localhost:8080/users/1',
        )
        print(response.status)
        print(await response.json())
        response = await session.delete(
            'http://localhost:8080/users/1',
        )
        print(response.status)
        print(await response.json())
        response = await session.get(
            'http://localhost:8080/users/1',
        )
        print(response.status)
        print(await response.json())


if __name__ == '__main__':
    asyncio.run(main())
