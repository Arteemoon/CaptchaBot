import logging
import os
from captcha import Captcha
import uuid
import random
from templates import Template
import datetime
from redis import RedisDispatcher
import json
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.getenv('TOKEN_BOT')
KICK_TIME_MINUTE = 1
INTERVAL_TIME = 10
FORMAT_TIME = '%Y-%m-%d %H:%M'

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
redis_dispatcher = RedisDispatcher('redis', 6379, 0)
scheduler = AsyncIOScheduler()

@dp.message_handler(content_types=["new_chat_members"])
async def new_member_handler(message: types.Message):
    num = str(random.choices(range(1000, 9999))[0])
    filename = f'{uuid.uuid4()}.png'
    Captcha(filename, num).create()
    with open(filename, 'rb') as captcha:
        await bot.send_photo(message.chat.id, captcha, caption=Template.CAPTCHA.format(f'@{message["from"].username}'))
    os.remove(filename)
    redis_key = f'{message.chat.id}_{message["from"].id}'
    redis_data = json.dumps({
        "answer": num,
        "kick_time": (datetime.datetime.utcnow() + datetime.timedelta(minutes=KICK_TIME_MINUTE)).strftime(FORMAT_TIME),
        "username": message['from'].username
    })
    await redis_dispatcher.append_quque_user(redis_key, redis_data)

@dp.message_handler()
async def message_handler(message: types.Message):
    user = await redis_dispatcher.get_user(f'{message.chat.id}_{message["from"].id}')
    if user:
        if message.text == json.loads(user)["answer"]:
            await redis_dispatcher.delete_quque_user([f'{message.chat.id}_{message["from"].id}'])
            await bot.send_message(message.chat.id, Template.SUCCESS_CAPTCHA.format(message["from"].username))
        else:
            await bot.delete_message(message.chat.id, message.message_id)
       

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(redis_dispatcher.connect())
    scheduler.add_job(redis_dispatcher.expire_redis_users, 'interval', seconds=INTERVAL_TIME, args=(bot, ))
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)