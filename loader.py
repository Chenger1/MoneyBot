from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage

from data import config

from tortoise import Tortoise

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage(config.REDIS_HOST, 6379, db=5)
dp = Dispatcher(bot, storage=storage)
db = Tortoise()


TORTOISE_ORM = {
    "connections": {"default": {
        'engine': 'tortoise.backends.asyncpg',
        'credentials': {
            'database': config.DB_NAME,
            'host': '127.0.0.1',
            'password': config.DB_PASSWORD,
            'port': '5432',
            'user': config.DB_USER
        }}},
    "apps": {
        "models": {
            "models": ["db.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
