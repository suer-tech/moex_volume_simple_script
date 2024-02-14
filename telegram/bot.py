import asyncio
import os

import aiohttp
from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiohttp import ClientSession

from keyboard import greet_kb1
from tg_config import users_id, token, fdv_crypto_dir_path, parser_dir_path, moex_dir_path, vol_dir_path

from aiogram import Dispatcher
bot = Bot(token)


async def send_message(full_path):
    file = full_path
    if os.stat(file).st_size > 0:
        with open(file, 'r', encoding='utf-8') as fr:
            mess = fr.read()
        for user in users_id:
            try:
                await bot.send_message(user, mess)
            except Exception as e:
                print(f"Error sending message to user {user}: {str(e)}")

        await remove_message_file(full_path)


async def remove_message_file(full_path):
    os.remove(full_path)


async def polling_thread(fdv_crypto_dir_path):
    while True:
        await asyncio.sleep(1)
        files = [f for f in os.listdir(fdv_crypto_dir_path) if f.endswith('_signal.txt')]
        if files:
            for file_name in files:
                full_path = os.path.join(fdv_crypto_dir_path, file_name)
                await send_message(full_path)


async def process_start_command(message: types.Message):
    await bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIDZ2JEZuGR8N1D5s__y0O8cIUGMk9OAAIiEwACXWxwS64th70744A-IwQ')
    mess = f'Привет, <b>{message.from_user.first_name}</b>! Здесь будут уведомления об изменении цены по основным биржевым активам.'
    await bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=greet_kb1)


async def with_puree(message: types.Message, file_name):
    try:
        with open(file_name, "r") as file:
            data = file.read()
            mess = data if data else f"Нет данных"
        await bot.send_message(message.chat.id, mess, reply_markup=greet_kb1)
    except FileNotFoundError:
        await bot.send_message(message.chat.id, f"Файл не найден")
    except Exception as e:
        await bot.send_message(message.chat.id, f"Произошла ошибка при чтении файла: {str(e)}")


async def send_messages_from_directory(message: types.Message, directory_path: str):
    try:
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        if not files:
            await bot.send_message(message.chat.id, "No files found in the directory.")
            return

        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
            try:
                with open(file_path, "r") as file:
                    data = file.read()
                    message_text = data if data else "No data found in the file."
                await bot.send_message(message.chat.id, message_text, reply_markup=greet_kb1)
            except Exception as e:
                await bot.send_message(message.chat.id, f"Error reading file {file_name}: {str(e)}")

    except Exception as e:
        await bot.send_message(message.chat.id, f"An error occurred: {str(e)}")


async def main():
    dp = Dispatcher(bot)
    # Обработчики сообщений
    dp.register_message_handler(process_start_command, commands=['start'])
    index_file_full_path = os.path.join(parser_dir_path, 'output.txt')
    dp.register_message_handler(lambda message: with_puree(message, index_file_full_path), Text(equals="Индексы"))
    crypto_file_full_path = os.path.join(parser_dir_path, 'crypto.txt')
    dp.register_message_handler(lambda message: with_puree(message, crypto_file_full_path), Text(equals="Крипто"))
    moex_file_full_path = os.path.join(moex_dir_path, 'all_spread.txt')
    dp.register_message_handler(lambda message: with_puree(message, moex_file_full_path), Text(equals="Спреды"))
    dp.register_message_handler(lambda message: send_messages_from_directory(message, vol_dir_path), Text(equals="Обьёмы"))

    try:
        await asyncio.create_task(dp.start_polling())
        await polling_thread(fdv_crypto_dir_path)

    except aiohttp.client_exceptions.ClientOSError as e:
        print(f"ClientOSError error: {e}")

        await bot.session.close()
        bot.session = ClientSession()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()