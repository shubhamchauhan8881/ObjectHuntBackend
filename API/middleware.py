from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs
from channels.db import database_sync_to_async

from django.contrib.auth.models import User


@database_sync_to_async
def returnUser(uid):
    return User.objects.get(pk=uid)


class JWTAuthMiddleWare:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"]
        query_params = query_string.decode()
        query_dict = parse_qs(query_params)

        user_id = query_dict["user"][0]

        user = await returnUser(user_id)
        scope["user"] = user
        return await self.app(scope, receive, send)
