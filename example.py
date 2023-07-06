# import telebot
# from telebot import types

# bot = telebot.TeleBot("6240843240:AAEWbR_a_AFnnkjTk1uF93IjTcvSTlUQg3s")


# @bot.message_handler(commands=["start"])
# def start(message):
#     markup = types.ReplyKeyboardMarkup()
#     btn1 = types.KeyboardButton("Hey")
#     btn2 = types.KeyboardButton("Halo")
#     btn3 = types.KeyboardButton("maro")
#     markup.row(btn1)
#     markup.row(btn2, btn3)
#     file = open("img.jpg", "rb")
#     bot.send_photo(message.chat.id, file, reply_markup=markup)
#     # bot.send_message(message.chat.id, "Hello", reply_markup=markup)
#     bot.register_next_step_handler(message, on_click)


# def on_click(message):
#     if message.text == "Hey":
#         bot.send_message(message.chat.id, "heyy")
#     elif message.text == "Halo":
#         bot.send_message(message.chat.id, "Huuu")
#     bot.register_next_step_handler(message, on_click)


# @bot.message_handler(content_types=["photo"])
# def get_photo(message):
#     markup = types.InlineKeyboardMarkup()
#     btn1 = types.InlineKeyboardButton("Перейти на сайт", url="https://remanga.org/")
#     btn2 = types.InlineKeyboardButton("Удалить фото", callback_data="delete")
#     btn3 = types.InlineKeyboardButton("Изменить фото", callback_data="edit")
#     markup.row(btn1)
#     markup.row(btn2, btn3)
#     bot.reply_to(message, "Какое красивое фото!", reply_markup=markup)


# @bot.callback_query_handler(func=lambda callback: True)
# def callback_message(callback):
#     if callback.data == "delete":
#         bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
#     elif callback.data == "edit":
#         bot.edit_message_text(
#             "edit text", callback.message.chat.id, callback.message.message_id
#         )


# bot.polling(non_stop=True)


# import telebot
# import sqlite3


# bot = telebot.TeleBot("6240843240:AAEWbR_a_AFnnkjTk1uF93IjTcvSTlUQg3s")
# name = None


# @bot.message_handler(commands=["start"])
# def start(message):
#     conn = sqlite3.connect("data.sql")
#     cur = conn.cursor()

#     cur.execute(
#         "CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))"
#     )
#     conn.commit()
#     cur.close()
#     conn.close()

#     bot.send_message(
#         message.chat.id, "Hello, i will registered you now, enter your name"
#     )
#     bot.register_next_step_handler(message, user_name)


# def user_name(message):
#     global name
#     name = message.text.strip()
#     bot.send_message(message.chat.id, "enter password")
#     bot.register_next_step_handler(message, user_name)


# def user_pass(message):
#     password = message.text.strip()
#     conn = sqlite3.connect("data.sql")
#     cur = conn.cursor()

#     cur.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (name, password))
#     conn.commit()
#     cur.close()
#     conn.close()
#     markup = telebot.types.InlineKeyboardMarkup()
#     markup.add(
#         telebot.types.InlineKeyboardButton("list of users", callback_data="users")
#     )
#     bot.send_message(message.chat.id, "done!", reply_markup=markup)


# bot.polling(non_stop=True)


# import telebot
# import requests
# import json

# bot = telebot.TeleBot("6240843240:AAEWbR_a_AFnnkjTk1uF93IjTcvSTlUQg3s")
# API = "2eba9e0aa9263c905d0f5749db949ff6"


# @bot.message_handler(commands=["start"])
# def start(message):
#     bot.send_message(message.chat.id, "Привет рад тебя видеть! Напиши название города.")


# @bot.message_handler(content_types=["text"])
# def get_weather(message):
#     city = message.text.strip().lower()
#     res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric")
#     data = json.loads(res.text)
#     bot.reply_to(message, f'Сейчас погода: {data["main"]["temp"]}')

# bot.polling(non_stop=True)


# import telebot
# from currency_converter import CurrencyConverter
# from telebot import types


# bot = telebot.TeleBot("6240843240:AAEWbR_a_AFnnkjTk1uF93IjTcvSTlUQg3s")
# API = "2eba9e0aa9263c905d0f5749db949ff6"
# currency = CurrencyConverter()
# amount = 0


# @bot.message_handler(commands=["start"])
# def start(message):
#     bot.send_message(message.chat.id, "Введите сумму")

#     bot.register_next_step_handler(message, summa)


# def summa(message):
#     global amount
#     try:
#         amount = int(message.text.strip())
#     except ValueError:
#         bot.send_message(message.chat.id, "Неверный формат.")
#         bot.register_next_step_handler(message, summa)
#         return
#     if amount > 0:
#         markup = types.InlineKeyboardMarkup(row_width=2)
#         btn1 = types.InlineKeyboardButton("USD/EUR", callback_data="usd/eur")
#         btn2 = types.InlineKeyboardButton("EUR/USD", callback_data="eur/usd")
#         btn3 = types.InlineKeyboardButton("USD/GBR", callback_data="usd/GBR")
#         btn4 = types.InlineKeyboardButton("Другое значение", callback_data="else")
#         markup.add(btn1, btn2, btn3, btn4)
#         bot.send_message(message.chat.id, "Выберите пару валют", reply_markup=markup)
#     else:
#         bot.send_message(message.chat.id, "Неверный формат.")
#         bot.register_next_step_handler(message, summa)


# @bot.callback_query_handler(func=lambda call: True)
# def callback(call):
#     if call.data != "else":
#         values = call.data.upper().split("/")
#         res = currency.convert(amount, values[0], values[1])
#         bot.send_message(
#             call.message.chat.id,
#             f"Получается: {round(res, 2)}. Можете заново вписать сумму",
#         )
#         bot.register_next_step_handler(call.message, summa)
#     else:
#         bot.send_message(call.message.chat.id, "Введите пару значений через слэш")
#         bot.register_next_step_handler(call.message, my_currency)


# def my_currency(message):
#     try:
#         values = message.text.upper().split("/")
#         res = currency.convert(amount, values[0], values[1])
#         bot.send_message(
#             message.chat.id,
#             f"Получается: {round(res, 2)}. Можете заново вписать сумму",
#         )
#         bot.register_next_step_handler(message, summa)
#     except Exception:
#         bot.send_message(message.chat.id, "Что то не так. Впишите значение правильно.")
#         bot.register_next_step_handler(message, my_currency)


# bot.polling(non_stop=True)


######################  AIOGRAM


# from aiogram import Bot, Dispatcher, executor, types

# bot = Bot("6240843240:AAEWbR_a_AFnnkjTk1uF93IjTcvSTlUQg3s")
# dp = Dispatcher(bot)


# @dp.message_handler(commands=["start"])
# async def start(message: types.Message):
#     await message.answer("Hello")


# @dp.message_handler(commands=["inline"])
# async def info(message: types.Message):
#     markup = types.InlineKeyboardMarkup()
#     markup.add(types.InlineKeyboardButton("Site", url="https://cristalix.gg/"))
#     markup.add(types.InlineKeyboardButton("Hello", callback_data="hello"))
#     await message.reply("Hello", reply_markup=markup)


# @dp.callback_query_handler()
# async def callback(call):
#     await call.message.answer(call.data)


# @dp.message_handler(commands=["reply"])
# async def reply(message: types.Message):
#     markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
#     markup.add(types.InlineKeyboardButton("Site"))
#     markup.add(types.InlineKeyboardButton("Website"))
#     await message.answer("Hello", reply_markup=markup)


# executor.start_polling(dp)


# from aiogram import Bot, Dispatcher, executor, types
# from aiogram.types.web_app_info import WebAppInfo
# import json

# bot = Bot("1636320570:AAFHK2w0D8oQgkRc5isAsaC_QEuHYzu16D8")
# dp = Dispatcher(bot)


# @dp.message_handler(commands=["start"])
# async def start(message: types.Message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.add(
#         types.KeyboardButton(
#             "Open website",
#             web_app=WebAppInfo(url="https://ayturgan.github.io/website-telegram-bot/"),
#         )
#     )
#     await message.answer("Hello friend", reply_markup=markup)


# @dp.message_handler(content_types=["web_app_data"])
# async def web_app(message: types.Message):
#     res = json.loads(message.web_app_data.data)
#     await message.answer(
#         f'Name: {res["name"]}. Email: {res["email"]}. Phone: {res["phone"]}'
#     )


# executor.start_polling(dp)
