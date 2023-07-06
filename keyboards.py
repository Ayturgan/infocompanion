import config as cfg
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

a = 0
keyss = []
keyb = InlineKeyboardMarkup()
for i, j in cfg.LANGDICT.items():
    key = InlineKeyboardButton(j, callback_data=i)
    keyss.append(key)
    a += 1
    if a == 3:
        a = 0
        keyb.add(keyss[0], keyss[1], keyss[2])
        keyss = []

markup_of_main = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton("Wikipedia")
button2 = KeyboardButton("Переводчик", callback_data="translator")
button3 = KeyboardButton("Картина")
button4 = KeyboardButton("Цитата дня")
markup_of_main.add(button1, button2, button3, button4)

main_menu_button = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_button.add(KeyboardButton("Главное меню"))

menu_trans = ReplyKeyboardMarkup(resize_keyboard=True)
menu_trans.add(KeyboardButton("Главное меню"))
menu_trans.add(KeyboardButton("Выбрать язык"))
