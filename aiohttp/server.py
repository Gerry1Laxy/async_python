from aiohttp import web
from sqlalchemy import select
from bcrypt import checkpw

from models import orm_context, session_middleware, User, Token
from views import raise_http_error, UserView


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
