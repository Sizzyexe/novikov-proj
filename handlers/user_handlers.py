

#region 2 вариант




from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import DatabaseHandler
import logging
import asyncio

logger = logging.getLogger(__name__)
router = Router()

# Константы
WELCOME_PHOTO_ID = "AgACAgIAAxkBAAMeZ9CrWTU8KLnt4cq6c48bj13N1NYAAkz1MRuVfIBKTuWj6376xvwBAAMCAAN4AAM2BA"
FIRST_VIDEO_NOTE_ID = "DQACAgIAAxkBAAICAAFn1AJLZq0I7zukdcmvonQ-TmSupwAC6mUAAvrVoEqV3jOoHxt1OTYE"
SECOND_VIDEO_NOTE_ID = "DQACAgIAAxkBAANMZ9CvF5am7ZO6wcVEwy60ljp-39AAAklrAALdA3hKNnlCz5zdYBw2BA"

# Состояния
class LessonStates(StatesGroup):
    waiting_for_lesson = State()

# ====================== ОБРАБОТКА СТАРТА ======================
@router.message(Command("start"))
async def cmd_start(message: Message, db: DatabaseHandler):
    user_id = message.from_user.id
    username = message.from_user.first_name
    
    welcome_text = (
        f"Рад приветствовать тебя, {username}!\n\n"
        "Меня зовут Павел Новиков, и благодаря товарному бизнесу в 19 лет я успел:\n\n"
        "• Купить Mercedes C180 и Toyota Mark 2\n"
        "• Запустить ооочень много ниш и поднять их с нуля до больших оборотов в дедлайне 2-х недель\n"
        "• Выйти на доход в 1млн руб. +++ и стабильно держать его\n"
        "• Заработать 2.5млн за 2 месяца в нише айфонов после кризиса\n"
        "• Открыть магазин с кроссовками в торговом центре (оффлайн) и продать его больше, чем за 1кк\n"
        "• Переехать в Питер и уехать\n"
        "• Съехать от родителей еще в 17\n"
        "• И много всего другого\n\n"
        "Здесь я делюсь знаниями, которые позволили мне это сделать.\n\n"
        "Ну что, готов?"
    )

    try:
        if not await db.user_exists(user_id):
            await db.add_user(user_id, message.from_user.username)

        builder = InlineKeyboardBuilder()
        builder.button(text="Готов! 🚀", callback_data="ready")
        await message.answer_photo(
            WELCOME_PHOTO_ID, 
            caption=welcome_text,
            reply_markup=builder.as_markup()
        )

    except Exception as e:
        logger.error(f"Ошибка при старте: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")

# ====================== ОБРАБОТКА КНОПКИ "ГОТОВ" ======================
@router.callback_query(F.data == "ready")
async def handle_ready(callback: CallbackQuery, state: FSMContext):
    try:
        builder = InlineKeyboardBuilder()
        builder.button(text="Получить урок 📚", callback_data="get_first_lesson")
        
        await callback.message.answer_video_note(
            video_note=FIRST_VIDEO_NOTE_ID,
            reply_markup=builder.as_markup()
        )
        
        await state.set_state(LessonStates.waiting_for_lesson)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await callback.message.answer("⚠️ Ошибка. Попробуйте снова.")
    finally:
        await callback.answer()

# ====================== ОТПРАВКА ПЕРВОГО УРОКА ======================
@router.callback_query(LessonStates.waiting_for_lesson, F.data == "get_first_lesson")
async def send_first_lesson(callback: CallbackQuery, db: DatabaseHandler, state: FSMContext):
    try:
        intro_text = (
            "Здесь ты узнаешь:\n\n"
            "— Структура продающего объявления: Теория и мои примеры\n"
            "— Как я пишу оффер (уникальное предложение) и описание,\n"
            "которые не оставляют у клиента вопросов\n"
            "— Как делать фото, которое выделяется среди тысяч\n"
            "— Мои фишки, благодаря которым я стабильно зарабатываю\n"
            "больше 700,000р ежемесячно\n\n"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Я изучил урок", callback_data="lesson_completed")
        
        lesson = await db.get_lesson_content(1)
        if lesson and lesson.get('video_file_id'):
            msg = await callback.message.answer_video(
                video=lesson['video_file_id'],
                caption=intro_text,
                reply_markup=builder.as_markup()
            )
            await state.update_data(lesson_message_id=msg.message_id)
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await callback.message.answer("⚠️ Не удалось загрузить урок")
    finally:
        await callback.answer()

# ====================== ОБРАБОТКА КНОПКИ "ИЗУЧИЛ" ======================
@router.callback_query(F.data == "lesson_completed")
async def handle_lesson_completion(callback: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        data = await state.get_data()
        if lesson_message_id := data.get('lesson_message_id'):
            await bot.edit_message_reply_markup(
                chat_id=callback.message.chat.id,
                message_id=lesson_message_id,
                reply_markup=None
            )
        
        # Мгновенная отправка второго видео
        await callback.message.answer_video_note(video_note=SECOND_VIDEO_NOTE_ID)
        
        # Запуск отложенной логики
        asyncio.create_task(continue_after_lesson(callback.message, bot))
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await callback.message.answer("⚠️ Произошла ошибка")
    finally:
        await state.clear()
        await callback.answer()

async def continue_after_lesson(message: Message, bot: Bot):
    # Поздравление через 15 секунд
    await asyncio.sleep(15)
    await send_congrats_message(message.chat.id, bot)


# ====================== ОСНОВНАЯ ЛОГИКА УРОКОВ ======================
async def send_lesson(message: Message, lesson_id: int, db: DatabaseHandler):
    try:
        lesson = await db.get_lesson_content(lesson_id)
        if not lesson:
            await message.answer("🎉 Поздравляем! Вы завершили курс!")
            return

        if lesson.get('video_file_id'):
            await message.answer_video(
                video=lesson['video_file_id'],
                caption=None,
                reply_markup=None
            )
        else:
            await message.answer(
                text=lesson['content'],
                reply_markup=None
            )

        if lesson_id == 1:
            asyncio.create_task(send_congrats_message(message.chat.id, message.bot))
        elif lesson_id == 2:
            asyncio.create_task(send_second_lesson_gift(message.chat.id, message.bot))
            
    except Exception as e:
        logger.error(f"Ошибка отправки урока: {e}")
        await message.answer("⚠️ Ошибка при отправке урока. Попробуйте позже.")

# ====================== ПОСЛЕДУЮЩИЕ СООБЩЕНИЯ ======================
async def send_congrats_message(chat_id: int, bot):
    await asyncio.sleep(15)#120sec
    try:
        text = (
    "Игорь попал на мою бесплатную консультацию, не имея никаких знаний о товарке. "
    "Начал с моих записанных уроков и меньше чем за 2 недели успел изучить всю информацию, "
    "заказать товар и полностью окупить обучение. Круто?\n\n"
    "А что, если я скажу, что уже через 2 месяца он заработал 750,000 рублей?\n\n"
    "Теперь такая возможность есть и у тебя! Жми на кнопку и забирай подарок 🎁"
)
        builder = InlineKeyboardBuilder()
        builder.button(text="Хочу изучать дальше и забрать подарок!", callback_data="get_gift")
        await bot.send_message(chat_id, text, reply_markup=builder.as_markup())
    except Exception as e:
        logger.error(f"Ошибка отправки поздравления: {e}")

async def send_second_lesson_gift(chat_id: int, bot):
    try:
        await asyncio.sleep(120)
        text1 = (
            "Изучил? Красавчик! Ты узнал, как зарабатывать на товарке много, прибыльно и постоянно!\n\n"
            "В следующем уроке ты поймешь, какую цену ставить на свои товары чтобы клиенты выбирали тебя, а ты зарабатывал еще больше!"
        )
        await bot.send_message(chat_id, text1)

        await asyncio.sleep(60)
        text2 = (
            "Подарок уже рядом! Ты узнал, как правильно ставить цены, чтобы ты выделялся среди конкурентов, при этом сохраняя высокую маржу\n\n"
            "Как только изучишь урок до конца, нажимай на кнопку 👇"
        )
        builder = InlineKeyboardBuilder()
        builder.button(text="Я все изучил, забрать подарок! 🎁", callback_data="get_gift")
        await bot.send_message(chat_id, text2, reply_markup=builder.as_markup())
    except Exception as e:
        logger.error(f"Ошибка отправки подарка: {e}")

# ====================== ОБРАБОТЧИКИ ДЛЯ ДРУГИХ КНОПОК ======================
@router.callback_query(F.data == "get_gift")
async def get_gift_handler(callback: CallbackQuery):
    try:
        await send_gift_message(callback.message.chat.id, callback.bot)
    except Exception as e:
        logger.error(f"Ошибка отправки финального сообщения: {e}")
    await callback.answer()

async def send_gift_message(chat_id: int, bot):
    try:
        text = (
    "Поздравляю! Я дарю тебе бесплатную карьерную консультацию, где я расскажу, как именно тебе:\n\n"
    "— Выбрать товар с высокой маржинальностью и протестировать его с минимальными вложениями\n"
    "— Дам контакты поставщиков, с которыми работаю уже несколько лет\n"
    "— Расскажу и покажу, как продвигать свои объявления (бесплатные и платные способы)\n"
    "— Как окупить все вложения меньше чем за месяц\n"
    "— Ну и самое главное — как выйти на доход 150,000 и больше!\n\n"
    "Скорее жми на кнопку, заполняй анкету, и я свяжусь с тобой в ближайшее время!"
)
        gift_photo_id = "AgACAgIAAxkBAAIBI2fS_nRKZeYyaV0nDVyEQVEO91B5AAKp8jEbEVCZSkZsYHZML8jgAQADAgADeQADNgQ"
        
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="📩 Заполнить анкету", url="https://forms.gle/LMYPtVTsmjfg5aQ38"))
        builder.row(InlineKeyboardButton(text="Смотреть полный курс 📚", callback_data="view_full_course"))
        builder.row(InlineKeyboardButton(text="📢 Смотреть кейсы", callback_data="view_cases"))
        
        await bot.send_photo(
            chat_id=chat_id,
            photo=gift_photo_id,
            caption=text,
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка отправки финального сообщения: {e}")

# ====================== ОБРАБОТЧИКИ КЕЙСОВ И КУРСА ======================
@router.callback_query(F.data == "view_cases")
async def show_first_case(callback: CallbackQuery):
    await show_case(callback, case_index=0)

@router.callback_query(F.data.startswith("next_case_"))
async def show_next_case(callback: CallbackQuery):
    case_index = int(callback.data.split("_")[-1])
    await show_case(callback, case_index)

async def show_case(callback: CallbackQuery, case_index: int):
    if case_index >= len(CASES):
        case_index = 0
        
    case = CASES[case_index]
    builder = InlineKeyboardBuilder()
    
    for btn in case['buttons']:
        if 'url' in btn:
            builder.row(InlineKeyboardButton(text=btn['text'], url=btn['url']))
        else:
            builder.row(InlineKeyboardButton(text=btn['text'], callback_data=btn['callback_data']))
    
    if case_index == 1:
        await callback.message.answer_photo(
            photo=case['photo_id'],
            caption=case['text'],
            reply_markup=builder.as_markup()
        )
        asyncio.create_task(send_delayed_video(callback.message.chat.id, callback.bot, case['video_id']))
    else:
        await callback.message.answer_photo(
            photo=case['photo_id'],
            caption=case['text'],
            reply_markup=builder.as_markup()
        )
    
    await callback.answer()

async def send_delayed_video(chat_id: int, bot, video_id: str):
    await asyncio.sleep(5)
    try:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Смотреть ещё', callback_data='next_case_2'))
        builder.row(InlineKeyboardButton(text='Стать следующим', url='https://t.me/Hogops'))
        await bot.send_video(
            chat_id=chat_id,
            video=video_id,
            caption="📹 Видео-доказательство результатов:",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка отправки видео: {e}")

@router.callback_query(F.data == "view_full_course")
async def show_full_course(callback: CallbackQuery):
    course_photo_id = "AgACAgIAAxkBAAIDbWfdMwTQ3mFtMcK0UvPY8oda2w-wAAKa7zEbSjboSgvdHfjhej6WAQADAgADeQADNgQ"
    text = (
    "🎓 <b>Обучение идеально подходит для тех, кто хочет изучить все самостоятельно!</b>\n\n"
    "Бери пошаговый план, в котором я подробно разобрал каждый шаг, задавай вопросы лично мне в чате "
    "и двигайся в комфортном темпе, приближаясь к заветным целям! — <a href='https://clck.ru/3J56Zj'>узнать, что в программе</a>\n\n"
    
    "<b>Кому подойдет записанный курс:</b>\n\n"
    "— Новичок в онлайн заработке, студент без постоянного заработка\n"
    "<i>Результат:</i> Делаешь стабильные 100 тысяч и больше на товарке\n\n"
    "— Работаешь в найме и мечтаешь работать на себя\n"
    "<i>Результат:</i> Увольняешься с нелюбимой работы, посвящаешь себя доходному делу\n\n"
    "— Уже имеешь заработок в интернете, уперся в потолок\n"
    "<i>Результат:</i> За первые 2 месяца выйдешь на регулярные продажи\n\n"
    
    "💸 <b>Цена:</b>\n"
    "<s>20.000₽</s> <b>9.990₽</b>\n\n"
    
    "👉<b><a href='https://clck.ru/3J56Zj'>ОЗНАКОМИТЬСЯ С ПОЛНОЙ ПРОГРАММОЙ ОБУЧЕНИЯ</a></b>\n\n"
    
    "С помощью моей программы свыше 70 человек смогли создать прибыльные магазины — <a href='https://clck.ru/3J56bU'>отзывы учеников</a>\n\n"
    
    "🛒 <b>Приобрести:</b> https://t.me/Hogops"
)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Забрать полный курс! 🚀", url="https://t.me/Hogops"))
    
    await callback.message.answer_photo(
        photo=course_photo_id,
        caption=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

# ====================== ДАННЫЕ КЕЙСОВ ======================
CASES = [
    {
        'photo_id': 'AgACAgIAAxkBAAIBL2fTAm2eVTWvO2A8p97uATsJ7VexAALB8jEbEVCZSjzl_kgPbcHNAQADAgADeAADNgQ',
        'text': (
            "Кейс Игоря\n\n"
            "Точка А: 0 рублей\n"
            "Точка Б: 750,000 рублей\n\n"
            "Игорь — теперь для меня близкий человек, с которым я провожу почти свой каждый день, "
            "ранее был у меня на потоке.\n\n"
            "В первые 2 недели он окупил личную работу, а за 2 месяца заработал 750,000р.\n\n"
            "Чтоб вы понимали, когда Игорь заходил ко мне на личную работу — он даже не знал как "
            "опубликовать объявление на авито."
        ),
        'buttons': [
            {'text': 'Смотреть ещё', 'callback_data': 'next_case_1'},
            {'text': 'Стать следующим', 'url': 'https://t.me/Hogops'}
        ]
    },
    {
        'photo_id': 'AgACAgIAAxkBAAIBMWfTAnZsw7Z1rPax1harGHFKQw0DAALD8jEbEVCZSjVZmW3bdpq_AQADAgADeQADNgQ',
        'text': (
            "Кейс Феди\n\n"
            "Точка А: 60,000 рублей\n"
            "Точка Б: 300,000 рублей\n\n"
            "ОДИН ИЗ ЛУЧШИХ УЧЕНИКОВ\n\n"
            "Спрошу лишь: Как вам результат в 300,000р в месяц на товарном бизнесе из которых "
            "120,000-150,000р в месяц идут с Авито?\n\n"
            "Работаешь и вкладываешься во время моего наставничества — получаешь только такой результат."
        ),
        'video_id': 'BAACAgIAAxkBAAIBNWfTAzl87u8eawLzVmdDWTcB88NrAAKOcwACEVCZSu4bVwLtzwABaTYE',
        'buttons': [
            {'text': 'Смотреть ещё', 'callback_data': 'next_case_2'},
            {'text': 'Стать следующим', 'url': 'https://t.me/Hogops'}
        ]
    },
    {
        'photo_id': 'AgACAgIAAxkBAAIBM2fTAnrcKrJ9jwKGRQVmMkeXsMckAALE8jEbEVCZSrd29h501v3gAQADAgADeAADNgQ',
        'text': (
            "Кейс Саши\n\n"
            "Точка А: 55,000 рублей\n"
            "Точка Б: 120,000 рублей\n\n"
            "Пришел с доходом 50-60к\n"
            "Сейчас делает 120,000р+\n\n"
            "Цель на наставнительство выполнил за месяц)"
        ),
        'buttons': [
            {'text': 'Я готов, погнали!', 'callback_data': 'view_full_course'}
        ]
    }
]

@router.callback_query(F.data == "menu")
async def menu_handler(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="Начать заново 🔄", callback_data="restart_course")
    builder.button(text="Выбрать урок 📚", callback_data="select_lesson")
    await callback.message.answer("🏠 Главное меню", reply_markup=builder.as_markup())

@router.callback_query(F.data == "restart_course")
async def restart_course(callback: CallbackQuery, db: DatabaseHandler):
    user_id = callback.from_user.id
    await db.update_lesson(user_id, 1)
    await send_lesson(callback.message, 1, db)
    await callback.answer()
#region 2 вариант




