import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import user_handlers, admin_handlers
from database import DatabaseHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import ADMIN_IDS, API_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
scheduler = AsyncIOScheduler()
db = DatabaseHandler('database.db')

@dp.update.outer_middleware()
async def inject_dependencies(handler, event, data):
    data["db"] = db
    return await handler(event, data)

async def on_startup():
    await db.create_tables()
    await db.add_initial_lessons()
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)

dp.include_router(user_handlers.router)
dp.include_router(admin_handlers.router)
dp.startup.register(on_startup)

if __name__ == '__main__':
    dp.run_polling(bot)