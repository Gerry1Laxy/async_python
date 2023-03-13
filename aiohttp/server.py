import json

from aiohttp import web
from sqlalchemy import select
from bcrypt import hashpw, gensalt, checkpw

from models import orm_context, session_middleware, User, Token


# async def test(request: web.Request):

#     json_data = await request.json()
#     headers = request.headers
#     qs = request.query
#     print(json_data)
#     if json_data:
#         print(f'{json_data=}')
#     print(f'{headers=}')
#     print(f'{qs=}')
#     return web.json_response(
#         {
#             'hello': 'world'
#         }
#     )

def raise_http_error(error_class, message: str):
    raise error_class(
        text=json.dumps({"status": "error", "description": message}),
        content_type="application/json",
    )

def check_password(password: str, hashed_password: str):
    return checkpw(password.encode(), hashed_password.encode())


@web.middleware
async def auth_middleware(request: web.Request, handler):
    token_id = request.headers.get('token')
    if not token_id:
        raise_http_error(web.HTTPUnauthorized, 'token required')
    token = await request.session.get(Token, token_id)
    if token is None:
        raise_http_error(web.HTTPForbidden, 'incorrect token')
    request['token'] = token
    return await handler(request)


async def login(request: web.Request):
    login_data = await request.json()
    user = await request.session.execute(
        select(User).where(User.name == login_data['name'])
    )
    user = user.scalar()
    if not user or not check_password(login_data['password'], user.password):
        raise_http_error(web.HTTPUnauthorized, 'incorrect login or password')
    
    token = Token(user=user)
    request.session.add(token)
    await request.session.commit()

    return web.json_response({
        'token': str(token.id)
    })

class UserView(web.View):

    def __init__(self, request: web.Request) -> None:
        super().__init__(request)
        self.user_id = int(self.request.match_info.get('user_id', 0))

    async def get(self):
        session = self.request.session
        # user_id = int(self.request.match_info['user_id'])
        user = await self.get_user()
        return web.json_response({
            'id': user.id,
            'name': user.name,
            'creation_time': user.creation_time.isoformat()
        })

    async def post(self):
        session = self.request.session
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
        self.check_owner()
        user = await self.get_user()
        json_data = await self.request.json()
        if 'password' in json_data:
            await self.hash_password(json_data)
        for field, value in json_data.items():
            setattr(user, field, value)
        self.request.session.add(user)
        await self.request.session.commit()
        return web.json_response({
            'status': 'success'
        })

    async def delete(self):
        self.check_owner()
        await self.request.session.delete(await self.get_user())
        await self.request.session.commit()
        return web.json_response({
            'status': 'success'
        })

    async def get_user(self):
        user = await self.request.session.get(User, self.user_id)

        if user is None:
            raise web.HTTPNotFound(
                text=json.dumps({
                    'status': 'error',
                    'massege': 'user not found'
                }),
                content_type='application/json'
            )
        return user
    
    def check_owner(self):
        if not self.request['token'] or self.request['token'].user_id != self.user_id:
            raise_http_error(web.HTTPForbidden, 'only owner has access')
    
    async def hash_password(self, json_data):
        password = json_data['password']
        password = password.encode()
        password = hashpw(password, salt=gensalt())
        password = password.decode()
        json_data['password'] = password



if __name__ == '__main__':

    app = web.Application()
    app_auth_required = web.Application(
        middlewares=[session_middleware, auth_middleware]
    )

    app.cleanup_ctx.append(orm_context)
    app.middlewares.append(session_middleware)
    app.add_routes([
        web.post('/users/', UserView),
        web.post('/login', login)
    ])
    app_auth_required.add_routes([
        web.get('/{user_id:\d+}', UserView),
        web.patch('/{user_id:\d+}', UserView),
        web.delete('/{user_id:\d+}', UserView),
    ])
    app.add_subapp('/users', app_auth_required)

    web.run_app(app, host='localhost')
