import json

from aiohttp import web
from sqlalchemy import select
from bcrypt import hashpw, gensalt, checkpw

from models import orm_context, session_middleware, User


app = web.Application()

app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)

async def test(request: web.Request):

    json_data = await request.json()
    headers = request.headers
    qs = request.query
    print(json_data)
    if json_data:
        print(f'{json_data=}')
    print(f'{headers=}')
    print(f'{qs=}')
    return web.json_response(
        {
            'hello': 'world'
        }
    )

class UserView(web.View):

    def __init__(self, request: web.Request) -> None:
        super().__init__(request)
        self.user_id = int(self.request.match_info.get('user_id', 0))

    async def get(self):
        session = self.request['session']
        # user_id = int(self.request.match_info['user_id'])
        user = await self.get_user()
        return web.json_response({
            'id': user.id,
            'name': user.name,
            'creation_time': user.creation_time.isoformat()
        })

    async def post(self):
        session = self.request['session']
        json_data = await self.request.json()
        name = await session.execute(
            select(User).where(User.name == json_data['name'])
        )
        if name.scalars().first() is None:
            await self.hash_password(json_data)
            user = User(**json_data)
            session.add(user)
            await session.commit()
        else:
            raise web.HTTPConflict(
                text=json.dumps({
                    'status': 'error',
                    'massege': 'user already exists'
                }),
                content_type='application/json'
            )

        return web.json_response({
            'id': user.id
        })

    async def patch(self):
        user = await self.get_user()
        json_data = await self.request.json()
        if 'password' in json_data:
            await self.hash_password(json_data)
        for field, value in json_data.items():
            setattr(user, field, value)
        self.request['session'].add(user)
        await self.request['session'].commit()
        return web.json_response({
            'status': 'success'
        })

    async def delete(self):
        await self.request['session'].delete(await self.get_user())
        await self.request['session'].commit()
        return web.json_response({
            'status': 'success'
        })

    async def get_user(self):
        user = await self.request['session'].get(User, self.user_id)

        if user is None:
            raise web.HTTPNotFound(
                text=json.dumps({
                    'status': 'error',
                    'massege': 'user not found'
                }),
                content_type='application/json'
            )
        return user
    
    async def hash_password(self, json_data):
        password = json_data['password']
        password = password.encode()
        password = hashpw(password, salt=gensalt())
        password = password.decode()
        json_data['password'] = password

app.add_routes([
    web.get('/test', test),
    web.get('/users/{user_id:\d+}', UserView),
    web.post('/users/', UserView),
    web.patch('/users/{user_id:\d+}', UserView),
    web.delete('/users/{user_id:\d+}', UserView)
])

if __name__ == '__main__':
    web.run_app(app, host='localhost')
