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
        response = await session.post(
            'http://localhost:8080/users/',
            json={
                'name': 'user_3',
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
        # response = await session.delete(
        #     'http://localhost:8080/users/1',
        # )
        # print(response.status)
        # print(await response.json())
        # response = await session.get(
        #     'http://localhost:8080/users/1',
        # )
        # print(response.status)
        # print(await response.json())
        print('login\n' + '-' * 20)
        response = await session.post(
            'http://localhost:8080/login',
            json={
                'name': 'user_2',
                'password': '4321'
            }
        )
        print(response.status)
        print(await response.json())
        print('login\n' + '-' * 20)
        response = await session.post(
            'http://localhost:8080/login',
            json={
                'name': 'user_3',
                'password': '4321'
            }
        )
        print(response.status)
        user_response = await response.json()
        print(user_response)
        
        response = await session.patch(
            'http://localhost:8080/users/2',
            json={
                'name': 'user_2',
                # 'password': '43210',
            },
            headers={'token': user_response['token']}
        )
        print(response.status)
        print(await response.json())
        response = await session.get(
            'http://localhost:8080/users/2',
        )
        print(response.status)
        print(await response.json())
        # response = await session.delete(
        #     'http://localhost:8080/users/2',
        #     headers={'token': user_response['token']}
        # )
        # print(response.status)
        # print(await response.json())
        # response = await session.get(
        #     'http://localhost:8080/users/2',
        # )
        # print(response.status)
        # print(await response.json())
        response = await session.post(
            'http://localhost:8080/users/2/adv/',
            json={
                'title': 'adv_1',
                'description': 'some description'
            },
            headers={
                'token': user_response['token']
            }
        )
        print(response.status)
        print(await response.json())
        response = await session.get(
            'http://localhost:8080/users/2/adv/1',
        )
        print(response.status)
        print(await response.json())

        response = await session.patch(
            'http://localhost:8080/users/2/adv/1',
            json={
                'title': 'adv_6',
                'description': 'description'
            },
            headers={
                'token': user_response['token']
            }
        )
        print(response.status)
        print(await response.json())
        response = await session.get(
            'http://localhost:8080/users/2/adv/1',
        )
        print(response.status)
        print(await response.json())

        response = await session.delete(
            'http://localhost:8080/users/2/adv/1',
            headers={
                'token': user_response['token']
            }
        )
        print(response.status)
        print(await response.json())
        response = await session.get(
            'http://localhost:8080/users/2/adv/1',
        )
        print(response.status)
        print(await response.json())


if __name__ == '__main__':
    asyncio.run(main())
