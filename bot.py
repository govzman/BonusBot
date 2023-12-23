import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import sqlite3
import time

create1 = """
CREATE TABLE Person (
    UserID INT PRIMARY KEY,
    Nickname VARCHAR(255),
    Level INT,
    HP INT,
    CurHP INT,
    Money INT,
    Attack INT,
    MagicAttack INT,
    XP INT,
    Armour INT,
    MagicArmour INT,
    LocationID INT,
    Start_move_time INT,
    Move_distance INT,
    Player_state INT
);
"""

create2 = """
CREATE TABLE Mobs (
    MobID INT PRIMARY KEY,
    HP INT,
    XP INT,
    ReqLevel INT,
    AttackType VARCHAR(255),
    Attack INT,
    Armour INT,
    MagicArmour INT
);"""

create3 = """
CREATE TABLE Locations (
    LocationID INT PRIMARY KEY,
    XCoord INT,
    YCoord INT,
    LocationType VARCHAR(255)
);
"""

create4 = """
CREATE TABLE Items (
    ItemID INT PRIMARY KEY,
    Cost INT,
    CostToSale INT,
    ItemType VARCHAR(255),
    HP INT,
    Mana INT,
    Attack INT,
    MagicAttack INT,
    Armour INT,
    MagicArmour INT,
    ReqLevel INT
);

"""

HELP_MSG = """
<b>Hi! In this game you can upgrade your character, buy weapons and explore world!</b>

<b>Some commands to help you:</b>

<em>/get_stats</em> - check your stats
<em>/get_paths</em> - check available locations
<em>/set_xp *number*</em> - set your XP
<em>/move *location*</em> - move to available location
"""

LOCATIONS = {0: {'name': "Start_location", 'coords': (
    0, 0)}, 1: {'name': "Moscow_City", 'coords': (0, 3)}}

LOCATIONS_ID = {'Start_location': 0, 'Moscow_City': 1}

PATHS = {0: [1], 1: [0]}

# Bot token can be obtained via https://t.me/BotFather
TOKEN = "6726992834:AAGDQBLGSVaIxpLFErLSnE6qzNpIZ_7IceQ"

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


def check_player(connection, user_id):
    cur = connection.cursor()
    find_login = cur.execute(
        "SELECT Nickname FROM Person WHERE UserID = ?", (user_id, ))
    return (find_login.fetchone() != None)


def search_tele_id(user_id, nickname):
    connection = sqlite3.connect('test.db')
    cur = connection.cursor()
    ans = check_player(connection, user_id)
    if not ans:
        cur.execute("""INSERT INTO Person VALUES
                    (?, ?, 0, 100, 100, 50, 10, 30, 0, 1, 0, 0, 0, 0, 0)
                    """, (user_id, nickname, ))
    connection.close()
    return ans

    #     Level INT,
    # HP INT,
    # CurHP INT,
    # Money INT,
    # Attack INT,
    # MagicAttack INT,
    # XP INT,
    # Armour INT,
    # MagicArmour INT,
    # LocationID INT


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    nickname = message.from_user.username
    if (search_tele_id(user_id, nickname)):
        await message.answer(f"Hello, {nickname}! Text /help to play")
    else:
        await message.answer(f"Oh! You are newbie, hi, {nickname}! Text /help to play. Good luck!")


@dp.message(Command("set_xp"))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args
    if (args):
        args = args.split()
        if (len(args) == 1 and args[0].isdigit()):
            connection = sqlite3.connect('test.db')
            cur = connection.cursor()
            if not check_player(connection, message.from_user.id):
                return await message.answer(f"Text /start to play")
            cur.execute("UPDATE Person SET XP = ?, Level = ? WHERE UserID = ?", (int(
                args[0]), int(args[0]) // 100, message.from_user.id, ))
            connection.commit()
            connection.close()
            return await message.answer(f"XP now is {args[0]} and level is {int(args[0]) // 100}")
        await message.answer(f"XP should be positive or zero number")
    await message.answer(f"/set_xp takes one positive or zero number as argument. \n Example: <I>/set_xp 100</I>", parse_mode="HTML")


@dp.message(Command("move"))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args
    if (args):
        args = args.split()

        connection = sqlite3.connect('test.db')
        cur = connection.cursor()
        if not check_player(connection, message.from_user.id):
                return await message.answer(f"Text /start to play")
        location_id = cur.execute(
            "SELECT LocationID FROM Person WHERE UserID = ?", (message.from_user.id, )).fetchone()[0]
        connection.commit()
        connection.close()
        if args[0] not in LOCATIONS_ID:
            return await message.answer(f"Location should be available. Check /get_paths")
        dest_city = LOCATIONS_ID[args[0]]
        if (len(args) == 1 and dest_city in PATHS[location_id]):
            # connection = sqlite3.connect('test.db')
            # cur = connection.cursor()
            # cur.execute("UPDATE Person SET XP = ?, Level = ? WHERE UserID = ?", (int(
            #     args[0]), int(args[0]) // 100, message.from_user.id, ))
            # connection.commit()
            # connection.close()
            global bot
            distance = abs(LOCATIONS[location_id]['coords'][0] - LOCATIONS[dest_city]['coords'][0]) + abs(
                LOCATIONS[location_id]['coords'][1] - LOCATIONS[dest_city]['coords'][1])
            await message.answer(f"You moving to {args[0]}! This will take {distance} seconds")
            await asyncio.sleep(distance)
            await bot.send_message(chat_id=message.from_user.id, text=f"You finally arrived to {args[0]}!")
            connection = sqlite3.connect('test.db')
            cur = connection.cursor()
            cur.execute("UPDATE Person SET LocationID = ? WHERE UserID = ?",
                        (dest_city, message.from_user.id, ))
            connection.commit()
            connection.close()
            return
        await message.answer(f"Location should be available. Check /get_paths")
    await message.answer(f"/move takes one argument with location name. \n Example: <I>/move Start_location</I>", parse_mode="HTML")


@dp.message(Command("get_stats"))
async def command_start_handler(message: Message) -> None:
    connection = sqlite3.connect('test.db')
    cur = connection.cursor()
    if not check_player(connection, message.from_user.id):
                return await message.answer(f"Text /start to play")
    stats = cur.execute(
        "SELECT Level, HP, CurHP, Money, Attack, MagicAttack, XP, Armour, MagicArmour, LocationID FROM Person WHERE UserID = ?", (message.from_user.id, )).fetchone()
    connection.commit()
    connection.close()
    await message.answer(f"<b>Stats</b>:\nLevel: {stats[0]}\nHP: {stats[1]}\nCurHP: {stats[2]}\nMoney: {stats[3]}\nAttack: {stats[4]}\nMagicAttack: {stats[5]}\nXP: {stats[6]}\nArmour: {stats[7]}\nMagicArmour: {stats[8]}\nLocation: {LOCATIONS[stats[9]]['name']}\n")


@dp.message(Command("get_paths"))
async def command_start_handler(message: Message) -> None:
    connection = sqlite3.connect('test.db')
    cur = connection.cursor()
    if not check_player(connection, message.from_user.id):
                return await message.answer(f"Text /start to play")
    location_id = cur.execute(
        "SELECT LocationID FROM Person WHERE UserID = ?", (message.from_user.id, )).fetchone()[0]
    connection.commit()
    connection.close()
    await message.answer(f"<b>Availible paths:</b>\n" + ',\n'.join(list(map(lambda x: f"<b>{LOCATIONS[x]['name']}</b>, distance: {abs(LOCATIONS[location_id]['coords'][0] - LOCATIONS[x]['coords'][0]) + abs(LOCATIONS[location_id]['coords'][1] - LOCATIONS[x]['coords'][1])}", PATHS[location_id]))))


@dp.message(Command("help"))
async def command_start_handler(message: Message) -> None:
    await message.answer(HELP_MSG)


@dp.message()
async def help_handler(message: types.Message) -> None:
    await message.answer("Type /help to get more info how to play!")


async def main() -> None:
    global bot
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # connection = sqlite3.connect('test.db')
    # cur = connection.cursor()
    # find_login = cur.execute(create1)
    # find_login = cur.execute(create2)
    # find_login = cur.execute(create3)
    # find_login = cur.execute(create4)
    # connection.commit()
    # connection.close()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import sqlite3
import time

create1 = """
CREATE TABLE Person (
    UserID INT PRIMARY KEY,
    Nickname VARCHAR(255),
    Level INT,
    HP INT,
    CurHP INT,
    Money INT,
    Attack INT,
    MagicAttack INT,
    XP INT,
    Armour INT,
    MagicArmour INT,
    LocationID INT,
    Start_move_time INT,
    Move_distance INT,
    Player_state INT
);
"""

create2 = """
CREATE TABLE Mobs (
    MobID INT PRIMARY KEY,
    HP INT,
    XP INT,
    ReqLevel INT,
    AttackType VARCHAR(255),
    Attack INT,
    Armour INT,
    MagicArmour INT
);"""

create3 = """
CREATE TABLE Locations (
    LocationID INT PRIMARY KEY,
    XCoord INT,
    YCoord INT,
    LocationType VARCHAR(255)
);
"""

create4 = """
CREATE TABLE Items (
    ItemID INT PRIMARY KEY,
    Cost INT,
    CostToSale INT,
    ItemType VARCHAR(255),
    HP INT,
    Mana INT,
    Attack INT,
    MagicAttack INT,
    Armour INT,
    MagicArmour INT,
    ReqLevel INT
);

"""

HELP_MSG = """
<b>Hi! In this game you can upgrade your character, buy weapons and explore world!</b>

<b>Some commands to help you:</b>

<em>/get_stats</em> - check your stats
<em>/get_paths</em> - check available locations
<em>/set_xp *number*</em> - set your XP
<em>/move *location*</em> - move to available location
"""

LOCATIONS = {0: {'name': "Start_location", 'coords': (
    0, 0)}, 1: {'name': "Moscow_City", 'coords': (0, 3)}}

LOCATIONS_ID = {'Start_location': 0, 'Moscow_City': 1}

PATHS = {0: [1], 1: [0]}

# Bot token can be obtained via https://t.me/BotFather
TOKEN = "6726992834:AAGDQBLGSVaIxpLFErLSnE6qzNpIZ_7IceQ"

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


def check_player(connection, user_id):
    cur = connection.cursor()
    find_login = cur.execute(
        "SELECT Nickname FROM Person WHERE UserID = ?", (user_id, ))
    return (find_login.fetchone() != None)


def search_tele_id(user_id, nickname):
    connection = sqlite3.connect('test.db')
    cur = connection.cursor()
    ans = check_player(connection, user_id)
    if not ans:
        cur.execute("""INSERT INTO Person VALUES
                    (?, ?, 0, 100, 100, 50, 10, 30, 0, 1, 0, 0, 0, 0, 0)
                    """, (user_id, nickname, ))
    connection.close()
    return ans

    #     Level INT,
    # HP INT,
    # CurHP INT,
    # Money INT,
    # Attack INT,
    # MagicAttack INT,
    # XP INT,
    # Armour INT,
    # MagicArmour INT,
    # LocationID INT


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    nickname = message.from_user.username
    if (search_tele_id(user_id, nickname)):
        await message.answer(f"Hello, {nickname}! Text /help to play")
    else:
        await message.answer(f"Oh! You are newbie, hi, {nickname}! Text /help to play. Good luck!")


@dp.message(Command("set_xp"))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args
    if (args):
        args = args.split()
        if (len(args) == 1 and args[0].isdigit()):
            connection = sqlite3.connect('test.db')
            cur = connection.cursor()
            if not check_player(connection, message.from_user.id):
                return await message.answer(f"Text /start to play")
            cur.execute("UPDATE Person SET XP = ?, Level = ? WHERE UserID = ?", (int(
                args[0]), int(args[0]) // 100, message.from_user.id, ))
            connection.commit()
            connection.close()
            return await message.answer(f"XP now is {args[0]} and level is {int(args[0]) // 100}")
        await message.answer(f"XP should be positive or zero number")
    await message.answer(f"/set_xp takes one positive or zero number as argument. \n Example: <I>/set_xp 100</I>", parse_mode="HTML")


@dp.message(Command("move"))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args
    if (args):
        args = args.split()

        connection = sqlite3.connect('test.db')
        cur = connection.cursor()
        if not check_player(connection, message.from_user.id):
                return await message.answer(f"Text /start to play")
        location_id = cur.execute(
            "SELECT LocationID FROM Person WHERE UserID = ?", (message.from_user.id, )).fetchone()[0]
        connection.commit()
        connection.close()
        if args[0] not in LOCATIONS_ID:
            return await message.answer(f"Location should be available. Check /get_paths")
        dest_city = LOCATIONS_ID[args[0]]
        if (len(args) == 1 and dest_city in PATHS[location_id]):
            # connection = sqlite3.connect('test.db')
            # cur = connection.cursor()
            # cur.execute("UPDATE Person SET XP = ?, Level = ? WHERE UserID = ?", (int(
            #     args[0]), int(args[0]) // 100, message.from_user.id, ))
            # connection.commit()
            # connection.close()
            global bot
            distance = abs(LOCATIONS[location_id]['coords'][0] - LOCATIONS[dest_city]['coords'][0]) + abs(
                LOCATIONS[location_id]['coords'][1] - LOCATIONS[dest_city]['coords'][1])
            await message.answer(f"You moving to {args[0]}! This will take {distance} seconds")
            await asyncio.sleep(distance)
            await bot.send_message(chat_id=message.from_user.id, text=f"You finally arrived to {args[0]}!")
            connection = sqlite3.connect('test.db')
            cur = connection.cursor()
            cur.execute("UPDATE Person SET LocationID = ? WHERE UserID = ?",
                        (dest_city, message.from_user.id, ))
            connection.commit()
            connection.close()
            return
        await message.answer(f"Location should be available. Check /get_paths")
    await message.answer(f"/move takes one argument with location name. \n Example: <I>/move Start_location</I>", parse_mode="HTML")


@dp.message(Command("get_stats"))
async def command_start_handler(message: Message) -> None:
    connection = sqlite3.connect('test.db')
    cur = connection.cursor()
    if not check_player(connection, message.from_user.id):
                return await message.answer(f"Text /start to play")
    stats = cur.execute(
        "SELECT Level, HP, CurHP, Money, Attack, MagicAttack, XP, Armour, MagicArmour, LocationID FROM Person WHERE UserID = ?", (message.from_user.id, )).fetchone()
    connection.commit()
    connection.close()
    await message.answer(f"<b>Stats</b>:\nLevel: {stats[0]}\nHP: {stats[1]}\nCurHP: {stats[2]}\nMoney: {stats[3]}\nAttack: {stats[4]}\nMagicAttack: {stats[5]}\nXP: {stats[6]}\nArmour: {stats[7]}\nMagicArmour: {stats[8]}\nLocation: {LOCATIONS[stats[9]]['name']}\n")


@dp.message(Command("get_paths"))
async def command_start_handler(message: Message) -> None:
    connection = sqlite3.connect('test.db')
    cur = connection.cursor()
    if not check_player(connection, message.from_user.id):
                return await message.answer(f"Text /start to play")
    location_id = cur.execute(
        "SELECT LocationID FROM Person WHERE UserID = ?", (message.from_user.id, )).fetchone()[0]
    connection.commit()
    connection.close()
    await message.answer(f"<b>Availible paths:</b>\n" + ',\n'.join(list(map(lambda x: f"<b>{LOCATIONS[x]['name']}</b>, distance: {abs(LOCATIONS[location_id]['coords'][0] - LOCATIONS[x]['coords'][0]) + abs(LOCATIONS[location_id]['coords'][1] - LOCATIONS[x]['coords'][1])}", PATHS[location_id]))))


@dp.message(Command("help"))
async def command_start_handler(message: Message) -> None:
    await message.answer(HELP_MSG)


@dp.message()
async def help_handler(message: types.Message) -> None:
    await message.answer("Type /help to get more info how to play!")


async def main() -> None:
    global bot
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # connection = sqlite3.connect('test.db')
    # cur = connection.cursor()
    # find_login = cur.execute(create1)
    # find_login = cur.execute(create2)
    # find_login = cur.execute(create3)
    # find_login = cur.execute(create4)
    # connection.commit()
    # connection.close()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
