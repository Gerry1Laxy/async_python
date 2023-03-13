import json

from aiohttp import web
from sqlalchemy import select
from bcrypt import hashpw, gensalt, checkpw

from models import User


def raise_http_error(error_class, message: str):
    raise error_class(
        text=json.dumps({"status": "error", "description": message}),
        content_type="application/json",
    )


class BaseView(web.View):

    def __init__(self, request: web.Request) -> None:
        super().__init__(request)
        self.item_id = int(self.request.match_info.get('item_id', 0))
        self.user_id = int(self.request.match_info.get('user_id', 0))
        if not self.item_id:
            self.item_id = self.user_id
        self.model = None
    
    async def get(self):
        item = await self.get_item()
    
    async def get_item(self):
        item = await self.request.session.get(self.model, self.item_id)
        if item is None:
            raise_http_error(
                web.HTTPNotFound,
                f'{self.model.__name__} not found'
            )



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
        if not self.request['token'] or (
            self.request['token'].user_id != self.user_id
        ):
            raise_http_error(web.HTTPForbidden, 'only owner has access')
    
    async def hash_password(self, json_data):
        password = json_data['password']
        password = password.encode()
        password = hashpw(password, salt=gensalt())
        password = password.decode()
        json_data['password'] = password

