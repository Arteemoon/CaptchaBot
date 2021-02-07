import os
import asyncio
import asyncio_redis
import datetime
import json
from templates import Template


class RedisDispatcher:

    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
    
    async def connect(self):
        self.connection = await asyncio_redis.Connection.create(host='redis', port=6379, db=0)

    async def append_quque_user(self, key, value):
        await self.connection.set(key, value)

    async def get_user(self, key):
        return await self.connection.get(key)

    async def get_users(self):
        return await self.connection.keys('*')
    
    async def delete_quque_user(self, key):
        await self.connection.delete(key)

    async def expire_redis_users(self, bot):
        from main import FORMAT_TIME
        user_keys = await self.get_users()
        for user_key in await user_keys.aslist():
            chat_id, user_id = user_key.split('_')
            user_data = json.loads(await self.get_user(user_key))
            if datetime.datetime.utcnow()  >= datetime.datetime.strptime(user_data['kick_time'], FORMAT_TIME):
                await bot.kick_chat_member(chat_id, user_id)
                await self.delete_quque_user([user_key])
                await bot.send_message(chat_id, Template.KICK_USER.format(user_data["username"]))