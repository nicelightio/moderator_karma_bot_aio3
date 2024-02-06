# виртуально окружение
# python -m venv venv
# venv\Scripts\activate
# deactivate


# Хауди Хо примитивный бот на аиограм
# https://www.youtube.com/watch?v=bXxa9IkAPew&t=98s


# pip install aiogram
# pip install sqlight
# скачаем sqliteStudio https://sqlitestudio.pl/
# запускаем
# Database - add database - db.db
#  connect to database
# Таблицы - crearte a table
# в поле "Имя таблицы" Subscriptions пишем и не жмем никуда
# Сверху зелено-синяя кнопочка "Добавить столбец"
# имя_столбца "id", галочка первичный ключ, справа Настроить - галочка автоинкремент - ОК - ОК
# "добвить столбец":
# имя_столбца: user_id Data_type: NUMERIC, галочка Not NULL - OK
# "добвить столбец":
# имя_столбца: status, Data_type: NUMERIC, галочка Not NULL, галочка Default -- Настроить: вписать TRUE - OK
# поставить квадратную зеленую галочку

import logging


import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command, CommandObject
from aiogram.types import FSInputFile, Message, ChatPermissions
from aiogram.types.chat_member_administrator import ChatMemberAdministrator
from aiogram.types.chat_member_owner import ChatMemberOwner

from random import randint

from time import sleep
import sqlite3
from datetime import datetime, timedelta


TELEGRAM_TOKEN = "6390700887:AAHoGnCMsJ9AkK51rmJrxsOalBl-LHiZtCY"
# группа с учениками
# GROUP_ID = '-1001674247269' # message.chat.id
# группа только для учителя, для тестов
# https://t.me/+zF_bqNvChnI5M2Ni
# GROUP_ID = "-4071547289"


# создаем фалйик sqlighter.py ложим туда этот класс
# создаем файлик db.db
# from sqlighter import SQLighter
class SQLighter:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        con = sqlite3.connect("db.db")
        cur = con.cursor()

    def add_subscriber(self, user_id, status=True):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO `subscriptions` (`user_id`, `status`) VALUES(?,?)",
                (user_id, status),
            )

    def get_subscriptions(self, status=True):
        """Получаем всех со статусом подписки"""
        with self.connection:
            return self.cursor.execute(
                "SELECT * FROM `subscriptions` WHERE `status` = ?", (status,)
            ).fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute(
                "SELECT * FROM `subscriptions` WHERE `user_id` = ?", (user_id,)
            ).fetchall()
            return bool(len(result))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            return self.cursor.execute(
                "UPDATE `subscriptions` SET `status` = ? WHERE `user_id` = ?",
                (status, user_id),
            )

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()


# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
# bot = Bot(token=config.API_TOKEN)
bot = Bot(token=TELEGRAM_TOKEN)
# диспатчер
dp = Dispatcher()

# инициализируем соединение с БД
db = SQLighter("db.db")


# @dp.message_handler(commands=['unsubscribe'])  # в старой версии так
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # #самостоятельная работа добавить картинку, паузу 1 секунду и фразу привет
    # sleep(1)
    await message.answer("Hello!")
    await asyncio.sleep(1.5)
    # await message.reply("это ответочка")
    await message.answer(
        "Привет, {0.first_name}.".format(message.from_user.first_name),
        parse_mode="html",
    )


@dp.message(Command("image"))
async def upload_photo(message: types.Message):
    image_from_pc = FSInputFile("hello.webp")
    result = await message.answer_photo(image_from_pc, caption="Пообщаемся")


# рандомное число из команды с диапазоном
#        /rn 1-6
# @dp.message(Command('random'))
@dp.message(Command(commands=["random", "rn", "rand"]))
async def get_random(message: types.Message, command: CommandObject):
    a, b = [int(n) for n in command.args.split("-")]
    rnum = randint(a, b)
    # await  message.reply(f'Случайное число: {rnum}')
    await message.reply(f"Случайное число от {a} до {b} пполучилось: \t {rnum} ")


# отправить сообщение в группу с id -1001674247269
@dp.message(Command("mychanel"))
# отправить в группу или в канал	-1001674247269
async def cmd_start(message: types.Message, bot: Bot):
    await bot.send_message(-1001674247269, "hello from aiogram")


# бан пользователя
@dp.message(Command("ban"))
# @dp.message(is_admin=True, commands=['ban'], comands_prefix=['!/'])
async def cmd_ban(message: types.Message):

    ### проверка кем является пользователь, который отправил команду, админом
    # получаем статус
    user_status = await bot.get_chat_member(
        chat_id=message.chat.id, user_id=message.from_user.id
    )
    if isinstance(
        user_status, types.chat_member_administrator.ChatMemberAdministrator
    ) or isinstance(user_status, types.chat_member_owner.ChatMemberOwner):
        print(f"\nadmin use /ban")
    else:
        await message.reply("не стоит писать то, о чем тебя не просили")
        return
    # если команда применена без цитаты
    if not message.reply_to_message:
        await message.reply("Эта комада должна быть ответом на сообщение!")
        return

    # запоминаем кого банить будем
    who_banned = message.reply_to_message.from_user.first_name
    # удаляем мсдж который мы цитировали командой /ban
    await bot.delete_message(
        chat_id=message.chat.id, message_id=message.reply_to_message.message_id
    )
    # БАНИМ пользователя
    await bot.ban_chat_member(
        chat_id=message.chat.id,
        user_id=message.reply_to_message.from_user.id,
        revoke_messages=True,
    )

    # репортим в чат что юзер забанен
    await message.answer(
        f"Пользователь <b>{who_banned} </b> забанен", parse_mode="html"
    )


""" ### мутируем
# https://qna.habr.com/q/1146740 тут есть отличный код в коментах
@dp.message(Command("mute"))
async def cmd_mute(message: types.Message):
    ### проверка кем является пользователь, который отправил команду
    # получаем статус
    user_status = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if not isinstance(user_status, types.chat_member_administrator.ChatMemberAdministrator ) or not isinstance(user_status, types.chat_member_owner.ChatMemberOwner):
    # if isinstance(user_status, ChatMemberAdministrator) or isinstance(user_status, ChatMemberOwner):
        await message.reply('у вас нет прав на совершение данного действия. \n Рейтинг понижен')
        return
    
    # если команда применена без цитаты
    if not message.reply_to_message:
        await message.reply("Эта комада должна быть ответом на сообщение!")
        return
    # рабочее мутирование юзера
    await message.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=message.reply_to_message.from_user.id,
        permissions=ChatPermissions(can_send_messages=False),
    )

    #### проверка статуса юзера в группе, рабочая
    # if isinstance(user_status, types.chat_member_administrator.ChatMemberAdministrator ) or isinstance(user_status, types.chat_member_owner.ChatMemberOwner):
    # # if isinstance(user_status, ChatMemberAdministrator) or isinstance(user_status, ChatMemberOwner):
    #     print(f'\n Админ или хозяин \n')

    # until_date=datetime.now() + timedelta(hours = 2 * 24))
    # end_restr = message.date + timedelta(seconds = 2 * 24))
    # 2 * 86400

    await message.reply_to_message.reply("Пользователь ззамутирован")
    # await message.reply_to_message.reply('Пользователь {user} ззамутирован на {ковырнадцать} {днейЧасов}')
"""


# https://qna.habr.com/q/1146740
@dp.message(Command(commands=["m", "mute"]))
async def mute(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть ответом на сообщение!")
        return
    try:
        muteint = int(message.text.split()[1])
        mutetype = message.text.split()[2]
        comment = " ".join(message.text.split()[3:])
    except IndexError:
        await message.reply("Не хватает аргументов!\nПример:\n`/m 3 дня причина`")
        return
    if (
        mutetype == "ч"
        or mutetype == "часов"
        or mutetype == "час"
        or mutetype == "часа"
    ):
        dt = datetime.now() + timedelta(hours=muteint)
        timestamp = dt.timestamp()
    elif (
        mutetype == "д" or mutetype == "дней" or mutetype == "день" or mutetype == "дня"
    ):
        dt = datetime.now() + timedelta(days=muteint)
        timestamp = dt.timestamp()
    elif (
        mutetype == "м"
        or mutetype == "мес"
        or mutetype == "месяц"
        or mutetype == "месяца"
        or mutetype == "месяцев"
    ):
        if muteint > 12:
            muteint = 12
        dt = datetime.now() + timedelta(days=muteint*30)
        timestamp = dt.timestamp()
        print('\n\ntimestamp\n')
        print(timestamp)
    else:
        await message.reply("не понял тебя")
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.reply_to_message.message_id - 2
        )
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.reply_to_message.message_id - 1
        )
        return

    await message.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=message.reply_to_message.from_user.id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=timestamp,
    )


    await message.reply(
        f' <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>, для Вас уютное место в партере на {muteint} {mutetype}\n {comment}',
        parse_mode="html",
    )



""" добавление инлайн кнопок c увеличением, уменьшением
 https://mastergroosha.github.io/aiogram-3-guide/buttons/"""
# Словарь хранятся пользовательские данные.
user_data = {}


def get_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
            types.InlineKeyboardButton(text="+1", callback_data="num_incr"),
        ],
        [types.InlineKeyboardButton(text="Подтвердить", callback_data="num_finish")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def update_num_text(message: types.Message, new_value: int):
    await message.edit_text(f"Укажите число: {new_value}", reply_markup=get_keyboard())


@dp.message(Command("numbers"))
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите число: 0", reply_markup=get_keyboard())


@dp.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: types.CallbackQuery):
    user_value = user_data.get(callback.from_user.id, 0)
    action = callback.data.split("_")[1]

    if action == "incr":
        user_data[callback.from_user.id] = user_value + 1
        await update_num_text(callback.message, user_value + 1)
    elif action == "decr":
        user_data[callback.from_user.id] = user_value - 1
        await update_num_text(callback.message, user_value - 1)
    elif action == "finish":
        await callback.message.edit_text(f"Итого: {user_value}")

    await callback.answer()


"""конец добавления кнопок с инлайном на увеличение уменьшение числа """


# ping pong
@dp.message()
async def echo(message: types.Message):
    # await message.answer(message.text)
    # print(f"message.reply_to_message.from_user = {message.reply_to_message.from_user}")
   
   # print(f"message.reply_to_message = {message.reply_to_message}")


# поллинг новых апдейтов
async def main():
    await dp.start_polling(bot)
    # удалить все предыдущие сообщения
    await bot.delete_webhook(drop_pending_updates=True)


# основной цикл
if __name__ == "__main__":
    asyncio.run(main())
