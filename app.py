from aiogram import executor

from loader import dp, db, TORTOISE_ORM
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)
    await db.init(config=TORTOISE_ORM)
    await db.generate_schemas()


async  def on_shutdown(dispatcher):
    await db.close_connections()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
