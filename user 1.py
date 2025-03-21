# from aiogram import F, Router
# from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
# from aiogram.filters import Command
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from database import DatabaseHandler
# import logging
# import asyncio

# logger = logging.getLogger(__name__)
# router = Router()

# WELCOME_PHOTO_ID = "AgACAgIAAxkBAAMeZ9CrWTU8KLnt4cq6c48bj13N1NYAAkz1MRuVfIBKTuWj6376xvwBAAMCAAN4AAM2BA"
# VIDEO_NOTE_ID = "DQACAgIAAxkBAANMZ9CvF5am7ZO6wcVEwy60ljp-39AAAklrAALdA3hKNnlCz5zdYBw2BA"

# # ====================== ОБРАБОТКА СТАРТА ======================
# async def send_igor_message(chat_id: int, bot):
#     await asyncio.sleep(5)
#     try:
#         text = (
#             "Игорь меньше чем за 2 недели успел изучить всю информацию в моем курсе, "
#             "заказать товар и полностью окупить обучение. Круто?\n\n"
#             "А что, если я скажу, что уже через 2 месяца он заработал 750,000 рублей?\n\n"
#             "Нажимай на кнопку и начинай изучать материал, который стабильно приносит результат моим ученикам"
#         )
#         builder = InlineKeyboardBuilder()
#         builder.button(text="Получить подарок", callback_data="start_lesson")
#         await bot.send_message(chat_id, text, reply_markup=builder.as_markup())
#     except Exception as e:
#         logger.error(f"Ошибка отправки сообщения об Игоре: {e}")

# async def send_delayed_content(chat_id: int, bot):
#     try:
#         await asyncio.sleep(10)
#         await bot.send_video_note(chat_id, video_note=VIDEO_NOTE_ID)
#         await send_igor_message(chat_id, bot)
#     except Exception as e:
#         logger.error(f"Ошибка цепочки отправки: {e}")

# @router.message(Command("start"))
# async def cmd_start(message: Message, db: DatabaseHandler):
#     user_id = message.from_user.id
#     username = message.from_user.first_name
    
#     welcome_text = (
#         f"Рад приветствовать тебя, {username}!\n"
#         "Здесь ты узнаешь:\n"
#         "— Структура продающего объявления: Теория и мои примеры\n"
#         "— Как я пишу оффер (уникальное предложение) и описание,\n"
#         "которые не оставляют у клиента вопросов\n" 
#         "— Как делать фото, которое выделяется среди тысяч\n"
#         "— Мои фишки, благодаря которым я стабильно зарабатываю\n"
#         "больше 700,000р ежемесячно\n"
#         "А так же сможешь ознакомиться с моим пошаговым планом запуска прибыльного магазина.\n"
#         "Досматривай до конца, впитывай информацию и узнай, какой подарок ждет тебя после прохождения.\n\n"
#         "Ну что, готов?"
#     )

#     try:
#         if not await db.user_exists(user_id):
#             await db.add_user(user_id, message.from_user.username)

#         await message.answer_photo(WELCOME_PHOTO_ID, caption=welcome_text)
#         asyncio.create_task(send_delayed_content(message.chat.id, message.bot))

#     except Exception as e:
#         logger.error(f"Ошибка при старте: {e}")
#         await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")

# # ====================== ОБРАБОТКА УРОКОВ ======================
# async def send_congrats_message(chat_id: int, bot):
#     await asyncio.sleep(15)#120sec
#     try:
#         text = (
#             "🎉 Поздравляю! Ты получил 1 из 27 уроков из моего\nпошагового плана\n\n"
#             "Досматривай до конца и жми на кнопку, подарок уже близко\n\n"
#         )
#         builder = InlineKeyboardBuilder()
#         builder.button(text="Хочу изучать дальше и забрать подарок!", callback_data="get_gift")
#         await bot.send_message(chat_id, text, reply_markup=builder.as_markup())
#     except Exception as e:
#         logger.error(f"Ошибка отправки поздравления: {e}")

# async def send_second_lesson_gift(chat_id: int, bot):
#     try:
#         await asyncio.sleep(1)#120sec
#         text1 = (
#             "Изучил? Красавчик! Ты узнал, как зарабатывать на товарке много, прибыльно и постоянно!\n\n"
#             "В следующем уроке ты поймешь, какую цену ставить на свои товары чтобы клиенты выбирали тебя, а ты зарабатывал еще больше!"
#         )
#         await bot.send_message(chat_id, text1)

#         await asyncio.sleep(1)#60sec
#         text2 = (
#             "Подарок уже рядом! Ты узнал, как правильно ставить цены, чтобы ты выделялся среди конкурентов, при этом сохраняя высокую маржу\n\n"
#             "Как только изучишь урок до конца, нажимай на кнопку 👇"
#         )
#         builder = InlineKeyboardBuilder()
#         builder.button(text="Я все изучил, забрать подарок! 🎁", callback_data="get_gift")
#         await bot.send_message(chat_id, text2, reply_markup=builder.as_markup())
#     except Exception as e:
#         logger.error(f"Ошибка отправки подарка: {e}")

# async def send_gift_message(chat_id: int, bot):
#     try:
#         text = (
#             "🎁 Поздравляю! Ты увидел малую часть из моего пошагового плана по созданию прибыльного магазина на авито, "
#             "которая уже приносит моим ученикам больше 150 тысяч ежемесячно!\n\n"
#             "Я люблю людей, которые идут к своим целям, поэтому дарю тебе эту информацию.\n"
#             "Но, помимо этого, если ты действительно готов херачить, а не просто посмотреть уроки и забыть, "
#             "я дарю тебе консультацию от меня, где я по полочкам разберу твою ситуацию и подскажу, "
#             "как именно тебе забрать свои 150-200к с товарки!\n\n"
#             "Скорее жми на кнопку и мы свяжемся с тобой в ближайшее время!"
#         )
#         gift_photo_id = "AgACAgIAAxkBAAIBI2fS_nRKZeYyaV0nDVyEQVEO91B5AAKp8jEbEVCZSkZsYHZML8jgAQADAgADeQADNgQ"  # Замените на ваш FileID
        
#         builder = InlineKeyboardBuilder()
#         builder.row(InlineKeyboardButton(text="📩 Написать мне", url="https://t.me/Hogops"))
#         builder.row(InlineKeyboardButton(text="Смотреть полный курс 📚", callback_data="view_full_course"))
#         builder.row(InlineKeyboardButton(text="📢 Смотреть кейсы", callback_data="view_cases"))
        
#         await bot.send_photo(
#             chat_id=chat_id,
#             photo=gift_photo_id,
#             caption=text,
#             reply_markup=builder.as_markup()
#         )
#     except Exception as e:
#         logger.error(f"Ошибка отправки финального сообщения: {e}")

# async def send_lesson(message: Message, lesson_id: int, db: DatabaseHandler):
#     try:
#         lesson = await db.get_lesson_content(lesson_id)
#         if not lesson:
#             await message.answer("🎉 Поздравляем! Вы завершили курс!")
#             return

#         reply_markup = None if lesson_id in [1, 2] else get_lesson_keyboard(lesson_id, await db.get_total_lessons())

#         if lesson.get('video_file_id'):
#             await message.answer_video(
#                 video=lesson['video_file_id'],
#                 caption=lesson['content'],
#                 reply_markup=reply_markup
#             )
#         else:
#             await message.answer(
#                 text=lesson['content'],
#                 reply_markup=reply_markup
#             )

#         if lesson_id == 1:
#             asyncio.create_task(send_congrats_message(message.chat.id, message.bot))
#         elif lesson_id == 2:
#             asyncio.create_task(send_second_lesson_gift(message.chat.id, message.bot))
#     except Exception as e:
#         logger.error(f"Ошибка отправки урока: {e}")
#         await message.answer("⚠️ Ошибка при отправке урока. Попробуйте позже.")

# def get_lesson_keyboard(current_lesson: int, total_lessons: int):
#     builder = InlineKeyboardBuilder()
#     builder.button(text="Следующий урок ➡️", callback_data="next_lesson")
#     builder.button(text="Меню 🏠", callback_data="menu")
#     return builder.adjust(1).as_markup()

# # ====================== ОБРАБОТЧИКИ КНОПОК ======================
# @router.callback_query(F.data == "start_lesson")
# async def start_lesson(callback: CallbackQuery, db: DatabaseHandler):
#     user_id = callback.from_user.id
#     await db.update_lesson(user_id, 1)
    
#     # Новый текст перед уроком
#     intro_text = (
#         "Вот урок из моего курса \"Сотка на товарке\", где я даю методологию по выходу "
#         "на заветные 100,000р по шагам на товарном бизнесе. Благодаря этим знаниям мои ученики "
#         "уже в первый месяц преодолевают планку 150,000 тысяч, а я дарю тебе это абсолютно бесплатно.\n\n"
#         "Бери и применяй👇"
#     )
#     await callback.message.answer(intro_text)
    
#     # Задержка 5 секунд перед отправкой урока
#     await asyncio.sleep(5)
#     await send_lesson(callback.message, 1, db)
#     await callback.answer()

# @router.callback_query(F.data == "next_lesson")
# async def next_lesson(callback: CallbackQuery, db: DatabaseHandler):
#     user_id = callback.from_user.id
#     try:
#         current_lesson = await db.get_current_lesson(user_id)
#         total_lessons = await db.get_total_lessons()
        
#         new_lesson = current_lesson + 1
#         if new_lesson > total_lessons:
#             new_lesson = 1

#         await db.update_lesson(user_id, new_lesson)
#         await send_lesson(callback.message, new_lesson, db)
#         await callback.answer()
#     except Exception as e:
#         logger.error(f"Ошибка перехода к уроку: {e}")
#         await callback.answer("⚠️ Произошла ошибка. Попробуйте позже.")

# @router.callback_query(F.data == "get_gift")
# async def get_gift_handler(callback: CallbackQuery):
#     await send_gift_message(callback.message.chat.id, callback.bot)
#     await callback.answer()

# # ====================== ОБРАБОТЧИКИ КЕЙСОВ ======================
# async def send_delayed_video(chat_id: int, bot, video_id: str):
#     await asyncio.sleep(5)
#     try:
#         builder = InlineKeyboardBuilder()
#         builder.row(InlineKeyboardButton(text='Смотреть ещё', callback_data='next_case_2'))
#         builder.row(InlineKeyboardButton(text='Стать следующим', url='https://t.me/Hogops'))
#         await bot.send_video(
#             chat_id=chat_id,
#             video=video_id,
#             caption="📹 Видео-доказательство результатов:",
#             reply_markup=builder.as_markup()
#         )
#     except Exception as e:
#         logger.error(f"Ошибка отправки видео: {e}")

# @router.callback_query(F.data == "view_cases")
# async def show_first_case(callback: CallbackQuery):
#     await show_case(callback, case_index=0)

# @router.callback_query(F.data.startswith("next_case_"))
# async def show_next_case(callback: CallbackQuery):
#     case_index = int(callback.data.split("_")[-1])
#     await show_case(callback, case_index)

# async def show_case(callback: CallbackQuery, case_index: int):
#     if case_index >= len(CASES):
#         case_index = 0
        
#     case = CASES[case_index]
#     builder = InlineKeyboardBuilder()
    
#     for btn in case['buttons']:
#         if 'url' in btn:
#             builder.row(InlineKeyboardButton(text=btn['text'], url=btn['url']))
#         else:
#             builder.row(InlineKeyboardButton(text=btn['text'], callback_data=btn['callback_data']))
    
#     if case_index == 1:
#         await callback.message.answer_photo(
#             photo=case['photo_id'],
#             caption=case['text'],
#             reply_markup=builder.as_markup()
#         )
#         asyncio.create_task(send_delayed_video(callback.message.chat.id, callback.bot, case['video_id']))
#     else:
#         await callback.message.answer_photo(
#             photo=case['photo_id'],
#             caption=case['text'],
#             reply_markup=builder.as_markup()
#         )
    
#     await callback.answer()

# @router.callback_query(F.data == "view_full_course")
# async def show_full_course(callback: CallbackQuery):
#     course_photo_id = "AgACAgIAAxkBAAIBLWfS__9-8lt1OVIBS3RqUerTrML3AAKx8jEbEVCZSq88JW8AAeiKIQEAAwIAA3kAAzYE"  # Ваш FileID
#     text = (
#         "🎓 <b>Идеально подходит для тех, кто хочет изучить все самостоятельно!</b>\n\n"
#         "Бери пошаговый план, применяй действия и двигайся в комфортном темпе, приближаясь к заветной сотке! "
#         "А затем больше и больше, курс рассчитан именно на это!\n\n"
#         "🔥 <b>Модули курса:</b>\n"
#         "— Вводный\n"
#         "— Введение в товарный бизнес\n"
#         "— Мышление и психология\n"
#         "— Выбор товара\n"
#         "— Поставщики\n"
#         "— Дропшиппинг\n"
#         "— Создание Авито-магазина\n"
#         "— Продвижение товара без вложений\n"
#         "— Продвижение товара с вложениями\n"
#         "— Продажи\n"
#         "— Логистика\n"
#         "— Юридические нюансы\n"
#         "— Масштабирование\n"
#         "— Бонус: Оптовые продажи в Telegram\n\n"
#         "💎 <b>Дополнительно:</b>\n"
#         "— Доступ в закрытый чат с учениками\n"
#         "— Моя личная поддержка в чате\n\n"
#         "💸 <b>Цена:</b>\n"
#         "<s>25.000₽</s> <b>9.900₽</b>"
#     )
#     builder = InlineKeyboardBuilder()
#     builder.row(InlineKeyboardButton(text="Забрать полный курс! 🚀", url="https://t.me/Hogops"))
    
#     await callback.message.answer_photo(
#         photo=course_photo_id,
#         caption=text,
#         reply_markup=builder.as_markup(),
#         parse_mode="HTML"
#     )
#     await callback.answer()

# # ====================== ДАННЫЕ КЕЙСОВ ======================
# CASES = [
#     {
#         'photo_id': 'AgACAgIAAxkBAAIBL2fTAm2eVTWvO2A8p97uATsJ7VexAALB8jEbEVCZSjzl_kgPbcHNAQADAgADeAADNgQ',
#         'text': (
#             "Кейс Игоря\n\n"
#             "Точка А: 0 рублей\n"
#             "Точка Б: 750,000 рублей\n\n"
#             "Игорь — теперь для меня близкий человек, с которым я провожу почти свой каждый день, "
#             "ранее был у меня на потоке.\n\n"
#             "В первые 2 недели он окупил личную работу, а за 2 месяца заработал 750,000р.\n\n"
#             "Чтоб вы понимали, когда Игорь заходил ко мне на личную работу — он даже не знал как "
#             "опубликовать объявление на авито."
#         ),
#         'buttons': [
#             {'text': 'Смотреть ещё', 'callback_data': 'next_case_1'},
#             {'text': 'Стать следующим', 'url': 'https://t.me/Hogops'}
#         ]
#     },
#     {
#         'photo_id': 'AgACAgIAAxkBAAIBMWfTAnZsw7Z1rPax1harGHFKQw0DAALD8jEbEVCZSjVZmW3bdpq_AQADAgADeQADNgQ',
#         'text': (
#             "Кейс Феди\n\n"
#             "Точка А: 60,000 рублей\n"
#             "Точка Б: 300,000 рублей\n\n"
#             "ОДИН ИЗ ЛУЧШИХ УЧЕНИКОВ\n\n"
#             "Спрошу лишь: Как вам результат в 300,000р в месяц на товарном бизнесе из которых "
#             "120,000-150,000р в месяц идут с Авито?\n\n"
#             "Работаешь и вкладываешься во время моего наставничества — получаешь только такой результат."
#         ),
#         'video_id': 'BAACAgIAAxkBAAIBNWfTAzl87u8eawLzVmdDWTcB88NrAAKOcwACEVCZSu4bVwLtzwABaTYE',
#         'buttons': [
#             {'text': 'Смотреть ещё', 'callback_data': 'next_case_2'},
#             {'text': 'Стать следующим', 'url': 'https://t.me/Hogops'}
#         ]
#     },
#     {
#         'photo_id': 'AgACAgIAAxkBAAIBM2fTAnrcKrJ9jwKGRQVmMkeXsMckAALE8jEbEVCZSrd29h501v3gAQADAgADeAADNgQ',
#         'text': (
#             "Кейс Саши\n\n"
#             "Точка А: 55,000 рублей\n"
#             "Точка Б: 120,000 рублей\n\n"
#             "Пришел с доходом 50-60к\n"
#             "Сейчас делает 120,000р+\n\n"
#             "Цель на наставнительство выполнил за месяц)"
#         ),
#         'buttons': [
#             {'text': 'Я готов, погнали!', 'callback_data': 'view_full_course'}
#         ]
#     }
# ]


# @router.callback_query(F.data == "menu")
# async def menu_handler(callback: CallbackQuery):
#     builder = InlineKeyboardBuilder()
#     builder.button(text="Начать заново 🔄", callback_data="restart_course")
#     builder.button(text="Выбрать урок 📚", callback_data="select_lesson")
#     await callback.message.answer("🏠 Главное меню", reply_markup=builder.as_markup())

# @router.callback_query(F.data == "restart_course")
# async def restart_course(callback: CallbackQuery, db: DatabaseHandler):
#     user_id = callback.from_user.id
#     await db.update_lesson(user_id, 1)
#     await send_lesson(callback.message, 1, db)
#     await callback.answer()