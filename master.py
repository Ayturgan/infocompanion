from aiogram import types, executor, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.types.web_app_info import WebAppInfo

from googletrans import Translator
from json.decoder import JSONDecodeError

import textwrap
import requests
import sqlite3
import wikipedia

import config as cfg
from keyboards import markup_of_main, main_menu_button, menu_trans, keyb

transl = Translator()

bot = Bot(cfg.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


con = sqlite3.connect("example.db")
print("Бот запущен...")


class MainReadyArticles(StatesGroup):
    WAITING_FOR_TOPIC = State()
    WAITING_FOR_LANGUAGE = State()


class TranslatorStates(StatesGroup):
    WAITING_FOR_TEXT = State()
    WAITING_FOR_NEXT_TEXT = State()

    WAITING_FOR_LANGUAGE = State()


class GetImagesStates(StatesGroup):
    WAITING_FOR_IMAGE = State()


class UserInput(StatesGroup):
    TOPIC = State()
    LANGUAGE = State()


# ОБРАБОТЧИК КОМАНДЫ START
@dp.message_handler(commands=["start"], state="*")
async def begin(message: Message, state: FSMContext):
    print(
        f"Пользователь {message.from_user.first_name}:{message.from_user.id} зашел в чат бота"
    )

    mycursor = con.cursor()
    sql = "SELECT * FROM users WHERE id = ?"
    adr = str(message.from_user.id)
    mycursor.execute(sql, (adr,))
    myresult = mycursor.fetchall()

    markup = markup_of_main
    first_name = message.from_user.first_name
    if myresult is None or myresult == [] or myresult == ():
        mycursor = con.cursor()
        sql = "INSERT INTO users (id, lang) VALUES (?, ?)"
        val = (str(message.from_user.id), "ru")
        mycursor.execute(sql, val)
        con.commit()
        await message.reply(
            f"Добро пожаловать {first_name}! Я к вашим услугам.\nЕсли вы хотите воспользоваться готовой статьей, вы можете просто ввести тему здесь)",
            reply_markup=markup,
        )
        with open("stickers/sticker1.webp", "rb") as sticker_file1:
            await message.answer_sticker(sticker_file1)
    else:
        await message.reply("С возвращением мой дорогой друг!", reply_markup=markup)
        with open("stickers/sticker.webp", "rb") as sticker_file:
            await message.answer_sticker(sticker_file)

    await MainReadyArticles.WAITING_FOR_TOPIC.set()


@dp.message_handler(state=MainReadyArticles.WAITING_FOR_TOPIC, content_types=["text"])
async def get_image(message: Message, state: FSMContext):
    if message.text == "Wikipedia":
        await wikidedia(message, state)
        return
    elif message.text == "Переводчик":
        await translator(message, state)
        return
    elif message.text == "Картина":
        await start_image(message)
        return
    elif message.text == "Цитата дня":
        await quote_of_the_day(message)
        return
    else:
        topic = message.text
        await state.update_data(topic=topic)
        keyboard = InlineKeyboardMarkup(row_width=3)
        for language in cfg.LANGUAGES:
            button = InlineKeyboardButton(text=language[0], callback_data=language[1])
            keyboard.insert(button)
        await message.reply("Выберите язык из списка:", reply_markup=keyboard)
        await MainReadyArticles.WAITING_FOR_LANGUAGE.set()


@dp.callback_query_handler(
    lambda c: c.data in [lang[1] for lang in cfg.LANGUAGES],
    state=MainReadyArticles.WAITING_FOR_LANGUAGE,
)
async def process_language_selection(
    callback_query: types.CallbackQuery, state: FSMContext
):
    lang = callback_query.data
    await state.update_data(lang=lang)
    await bot.answer_callback_query(callback_query.id, text="Язык выбран!")
    data = await state.get_data()
    topic = data["topic"]
    lang = data["lang"]
    article = generate_article(topic, lang)
    if article:
        paragraphs = textwrap.wrap(article, width=4096)
        for paragraph in paragraphs:
            await bot.send_message(callback_query.message.chat.id, paragraph)

        quote = get_quotes(lang)
        if quote:
            await callback_query.message.answer(f"Цитата: {quote}")
            response = requests.get(f"https://source.unsplash.com/featured/?{topic}")
            if response.status_code == 200:
                await callback_query.message.answer_photo(photo=response.content)
                print("Пользователь получил свою готовую статью")
            else:
                await callback_query.message.reply("Не удалось получить картинку")
    else:
        await callback_query.message.reply("Такая тема не найдена в Википедии")
    await MainReadyArticles.WAITING_FOR_TOPIC.set()


def get_quotes(lang):
    response = requests.get(
        f"http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang={lang}"
    )
    try:
        if response.status_code == 200:
            data = response.json()
            if "quoteText" in data:
                quote = data["quoteText"]
                return quote
    except JSONDecodeError:
        pass
    return None


# ОБРАБОТЧИК КНОПКИ ГЛАВНОЕ МЕНЮ
@dp.message_handler(text="Главное меню")
async def main_menu(message: Message, state: FSMContext):
    print(f"Пользователь {message.from_user.first_name} перешёл в Главное меню")
    await state.finish()
    markup = markup_of_main
    await message.answer(
        "Вы вернулись в главное меню. Чем еще желаете воспользоваться?",
        reply_markup=markup,
    )
    with open("stickers/sticker2.webp", "rb") as sticker_file:
        await message.answer_sticker(sticker_file)
    await MainReadyArticles.WAITING_FOR_TOPIC.set()


# ОБРАБОТЧИК КНОПКИ ЦИТАТА ДНЯ


def get_quote():
    response = requests.get(
        "http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=ru"
    )
    if response.status_code == 200:
        data = response.json()
        if "quoteText" in data:
            quote = data["quoteText"]
            return quote
    return None


@dp.message_handler(text="Цитата дня")
async def quote_of_the_day(message: Message):
    while True:
        quote = get_quote()
        if quote is None:
            continue
        else:
            response = requests.get(f"https://source.unsplash.com/featured/?natural")
            if response.status_code == 200:
                await message.answer_photo(photo=response.content, caption=quote)
                print("Пользователь получил цитату дня)")

            else:
                await message.answer(quote)
                print("Пользователь получил цитату дня)")

            break


# ОБРАБОТЧИК КНОПКИ КАРТИНА


@dp.message_handler(text="Картина")
async def start_image(message: Message):
    print(f"Пользователь {message.from_user.first_name} перешёл в Картина")

    await message.answer(
        "Приветсвую вас! Здесь вы можете указать название или ключевые слова, чтобы я смог отправить вам подходящую картину. Пожалуйста, используйте английский язык для наилучшего результата)",
        reply_markup=main_menu_button,
    )
    with open("stickers/sticker3.webp", "rb") as sticker_file:
        await message.answer_sticker(sticker_file)
    await GetImagesStates.WAITING_FOR_IMAGE.set()


@dp.message_handler(state=GetImagesStates.WAITING_FOR_IMAGE, content_types=["text"])
async def get_image(message: Message, state: FSMContext):
    if message.text == "Главное меню":
        await main_menu(message, state)
        return
    response = requests.get(f"https://source.unsplash.com/featured/?{message.text}")
    if response.status_code == 200:
        await message.answer_photo(photo=response.content)
        print("Пользователь получил свою картину)")
    else:
        await message.reply("Не удалось получить картинку")
    await GetImagesStates.WAITING_FOR_IMAGE.set()


# ОБРАБОТЧИК КНОПКИ WIKIPEDIA


def generate_article(topic, lang):
    wikipedia.set_lang(lang)
    try:
        page = wikipedia.page(topic)
        summary = wikipedia.summary(topic)
        article = f"Статья: {page.title}\n\n{summary}"
        return article
    except wikipedia.exceptions.DisambiguationError as e:
        options = e.options[:5]
        article = f"Уточните ваш запрос, возможно вы имели в виду одну из следующих тем:\n\n{', '.join(options)}"
        return article
    except wikipedia.exceptions.PageError:
        article = "Такая тема не найдена в Википедии"
        return article


@dp.message_handler(text="Wikipedia")
async def wikidedia(message: Message, state: FSMContext):
    print(f"Пользователь {message.from_user.first_name} перешёл в Wikipedia")
    if message.text == "Главное меню":
        await main_menu(message, state)
        return
    await message.reply(
        "Здесь ты можешь получить мини-статью на любую тему. Попрошу тебя написать тему более точно, чтобы получить желаемый результат. Введите тему:",
        reply_markup=main_menu_button,
    )

    await UserInput.TOPIC.set()


@dp.message_handler(state=UserInput.TOPIC)
async def process_topic(message: types.Message, state: FSMContext):
    if message.text == "Главное меню":
        await main_menu(message, state)
        return
    topic = message.text
    await state.update_data(topic=topic)
    keyboard = InlineKeyboardMarkup(row_width=3)
    for language in cfg.LANGUAGES:
        button = InlineKeyboardButton(text=language[0], callback_data=language[1])
        keyboard.insert(button)
    await message.reply("Выберите язык из списка:", reply_markup=keyboard)
    await UserInput.LANGUAGE.set()


@dp.callback_query_handler(
    lambda c: c.data in [lang[1] for lang in cfg.LANGUAGES], state=UserInput.LANGUAGE
)
async def process_language_selection(
    callback_query: types.CallbackQuery, state: FSMContext
):
    lang = callback_query.data
    await state.update_data(lang=lang)
    await bot.answer_callback_query(callback_query.id, text="Язык выбран!")
    data = await state.get_data()
    topic = data["topic"]
    lang = data["lang"]
    article = generate_article(topic, lang)
    if article:
        url = f"https://{lang}.m.wikipedia.org/w/index.php?go=Перейти&search=" + topic
        paragraphs = textwrap.wrap(article, width=4096)

        for i, paragraph in enumerate(paragraphs):
            if i == len(paragraphs) - 1:
                markup = types.InlineKeyboardMarkup(resize_keyboard=True)
                markup.add(
                    types.InlineKeyboardButton(
                        "Открыть Википедию", web_app=WebAppInfo(url=url)
                    )
                )
            else:
                markup = None

            await bot.send_message(
                callback_query.message.chat.id, paragraph, reply_markup=markup
            )

        with open("stickers/sticker4.webp", "rb") as sticker_file:
            await callback_query.message.answer_sticker(
                sticker_file, reply_markup=main_menu_button
            )
    else:
        await callback_query.message.reply("Такая тема не найдена в Википедии")
        with open("stickers/sticker7.webp", "rb") as sticker_file:
            await callback_query.message.answer_sticker(sticker_file)
    if callback_query.message.text == "Главное меню":
        await main_menu(callback_query.message, state)
        return
    print("Пользователь получил свою статью)")
    await UserInput.TOPIC.set()


# ОБРАБОТЧИК КНОПКИ ПЕРЕВОДЧИК
@dp.message_handler(text="Переводчик")
async def translator(msg: Message, state: FSMContext):
    print(f"Пользователь {msg.from_user.first_name} перешёл в Переводчик")
    if msg.text == "Главное меню":
        await main_menu(msg, state)
        return

    await msg.answer(
        "Добро пожаловать в переводчик😊 Можете ввести текст на любом языке.",
        reply_markup=menu_trans,
    )
    with open("stickers/sticker6.webp", "rb") as sticker_file:
        await msg.answer_sticker(sticker_file)
    await TranslatorStates.WAITING_FOR_NEXT_TEXT.set()


@dp.message_handler(
    state=[TranslatorStates.WAITING_FOR_TEXT, TranslatorStates.WAITING_FOR_NEXT_TEXT],
    content_types=["text"],
)
async def process_question(msg: Message, state: FSMContext):
    if msg.text == "Главное меню":
        await main_menu(msg, state)
        return

    if msg.text == "Выбрать язык":
        await choose_language(msg, state)
        return

    print(f"Пользователь {msg.from_user.first_name} переводит: {msg.text}")
    mycursor = con.cursor()
    sql = "SELECT * FROM users WHERE id = ?"
    adr = msg.from_user.id
    mycursor.execute(sql, (adr,))
    myresult = mycursor.fetchall()
    print(myresult)
    lang = myresult[0][1]

    translation = transl.translate(msg.text, dest=lang)
    if translation is not None and translation.text is not None:
        word = translation.text
        await bot.send_message(msg.from_user.id, word)
    else:
        word = "Ошибка при переводе"
        print(word)


@dp.callback_query_handler(
    lambda c: c.data == "translator", state=TranslatorStates.WAITING_FOR_TEXT
)
async def process_callback_kb1btn1(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await choose_language(callback_query.message, state)


@dp.callback_query_handler(
    lambda c: c.data in cfg.LANGUES, state=TranslatorStates.WAITING_FOR_LANGUAGE
)
async def process_callback_language(callback_query: CallbackQuery, state: FSMContext):
    lang = callback_query.data

    mycursor = con.cursor()
    sql = "UPDATE users SET lang = ? WHERE id = ?"
    val = (lang, str(callback_query.from_user.id))

    mycursor.execute(sql, val)
    print(f"Выбранный язык: {lang}")
    print(f"ID пользователя: {callback_query.from_user.id}")

    await bot.send_message(
        callback_query.from_user.id,
        "Язык изменился на "
        + cfg.LANGDICT[lang]
        + "\nМожете ввести текст с любого языка",
    )
    with open("stickers/sticker3.webp", "rb") as sticker_file:
        await callback_query.message.answer_sticker(sticker_file)
    print("Данные приняты в sql")
    await TranslatorStates.WAITING_FOR_TEXT.set()


@dp.message_handler(text="Выбрать язык", state=TranslatorStates.WAITING_FOR_TEXT)
async def choose_language(message: Message, state: FSMContext):
    print("Выбор языка")
    await message.reply("Выберите язык", reply_markup=keyb)
    await TranslatorStates.WAITING_FOR_LANGUAGE.set()


executor.start_polling(dp, skip_updates=True)
