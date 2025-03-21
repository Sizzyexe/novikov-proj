from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import DatabaseHandler

scheduler = AsyncIOScheduler()

async def setup_scheduler(bot, db):
    @scheduler.scheduled_job('cron', hour=12, timezone='Europe/Moscow')
    async def daily_reminder():
        users = await db.get_inactive_users()
        for user_id in users:
            await bot.send_message(user_id, "Не забудьте продолжить обучение! 🚀")

    @scheduler.scheduled_job('interval', hours=1)
    async def check_inactivity():
        users = await db.get_inactive_users()
        for user_id in users:
            await bot.send_message(user_id, "Мы скучаем! Вернитесь к обучению 😊")