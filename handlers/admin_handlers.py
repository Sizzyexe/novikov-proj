from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_IDS
from keyboards import admin_keyboard, cancel_keyboard
from database import DatabaseHandler
import logging

logger = logging.getLogger(__name__)
router = Router()

class BroadcastState(StatesGroup):
    message = State()

class BindVideoState(StatesGroup):
    waiting_lesson = State()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Доступ запрещен")
        return
    await message.answer("🔧 Админская панель:", reply_markup=admin_keyboard())

@router.message(Command("upload"))
async def upload_video_handler(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    if not message.video:
        await message.answer("📎 Отправьте видео файл")
        return

    await state.update_data(
        file_id=message.video.file_id,
        file_unique_id=message.video.file_unique_id
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="Урок 1", callback_data="bind_1")
    builder.button(text="Урок 2", callback_data="bind_2")
    builder.adjust(1)
    
    await message.answer(
        "🔗 К какому уроку привязать видео?",
        reply_markup=builder.as_markup()
    )
    await state.set_state(BindVideoState.waiting_lesson)

@router.callback_query(BindVideoState.waiting_lesson, F.data.startswith("bind_"))
async def bind_video_handler(callback: CallbackQuery, db: DatabaseHandler, state: FSMContext):
    try:
        lesson_id = int(callback.data.split("_")[1])
        data = await state.get_data()
        await db.update_lesson_video(lesson_id, data['file_id'])
        await callback.message.edit_text(
            f"✅ Видео привязано к уроку {lesson_id}\n"
            f"File ID: {data['file_id']}\n"
            f"Unique ID: {data['file_unique_id']}"
        )
    except Exception as e:
        logger.error(f"Ошибка привязки видео: {e}")
        await callback.message.edit_text("❌ Ошибка привязки видео")
    finally:
        await state.clear()

@router.message(F.photo)
async def get_file_id(message: Message):
    await message.reply(f"File ID: {message.photo[-1].file_id}")
@router.message(F.video_note)
async def get_video_note_id(message: Message):
    video_note_id = message.video_note.file_id
    await message.reply(f"File ID видеосообщения: `{video_note_id}`")

@router.callback_query(F.data == "broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "📢 Введите сообщение для рассылки:", 
        reply_markup=cancel_keyboard()
    )
    await state.set_state(BroadcastState.message)
    await callback.answer()

@router.message(BroadcastState.message)
async def process_broadcast(message: Message, state: FSMContext, db: DatabaseHandler):
    users = await db.get_all_users()
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await message.send_copy(chat_id=user_id)
            success += 1
        except Exception as e:
            failed += 1
    
    await message.answer(
        f"✅ Рассылка завершена:\nДоставлено: {success}\nНе удалось: {failed}"
    )
    await state.clear()

@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery, db: DatabaseHandler):
    stats = await db.get_stats()
    text = (
        "📊 Статистика бота:\n\n"
        f"👥 Пользователей: {stats['total_users']}\n"
        f"📈 Активных: {stats['active_users']}\n"
        f"🎓 Прогресс: {stats['avg_progress']} уроков\n"
        f"📅 Последняя регистрация: {stats['last_registration']}"
    )
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Действие отменено")
    await callback.answer()

@router.message(F.video)
async def show_file_id_handler(message: Message):
    video = message.video
    await message.reply(
        f"📹 File ID: {video.file_id}\n"
        f"🆔 Unique ID: {video.file_unique_id}"
    )