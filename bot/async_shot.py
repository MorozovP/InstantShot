import logging
import os
import re
import sys
from time import strftime, time

import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType, InputMediaPhoto
from dotenv import load_dotenv

load_dotenv()

MEDIA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app/media/'
)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
THUMBNAIL_TOKEN = os.getenv('THUMBNAIL_TOKEN')
THUMBNAIL_URL = os.getenv('THUMBNAIL_URL')
DB_API_URL = os.getenv('DB_API_URL')

bot = Bot(token=TELEGRAM_TOKEN)

dp = Dispatcher(bot)

logging_status = {
    'error': 'При получении скриншота возникла ошибка',
    'success': 'Скриншот получен',
    'save_error': 'При сохранении данных возникла ошибка',
    'save_success': 'Данные сохранены успешно',
    'get_msg_error': 'Ошибка при получении сообщения из БД',
    'get_msg_success': 'Сообщение из базы получено',
    'get_title_error': 'При запросе к сайту возникла ошибка',
    'get_title_success': 'Title получен'
}


async def get_db_message(session, message_name):
    """Запрашивает ответное сообщение бота из БД."""
    try:
        async with session.get(url=f'{DB_API_URL}{message_name}') as resp:
            r = await resp.json()
            logging.info(logging_status['get_msg_success'])
            return r['text']
    except Exception as error:
        err_message = logging_status['get_msg_error'], error
        raise Exception(err_message)


async def save_bot_user(session, data) -> None:
    """Сохраняет данные пользователя в БД."""
    try:
        await session.post(url=f'{DB_API_URL}user/', data=data)
        logging.info(logging_status['save_success'])
    except Exception as error:
        err_message = logging_status['save_error'], error
        raise Exception(err_message)


async def save_data(session, data) -> None:
    """Сохраняет данные запроса в БД."""
    try:
        await session.post(url=f'{DB_API_URL}request/', json=data)
        logging.info(logging_status['save_success'])
    except Exception as error:
        err_message = logging_status['save_error'], error
        raise Exception(err_message)


async def get_title(requested_website) -> str:
    """Делает запрос к сайту и извлекает из ответа title."""
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(f'https://{requested_website}')
            logging.info(logging_status['get_title_success'])
            return re.search('.*>(.*)</title',
                             await response.text(), re.IGNORECASE).group(1)
    except Exception as error:
        err_message = logging_status['get_title_error'], error
        raise Exception(err_message)


async def fetch_screenshot(requested_website, filename):
    """Делает запрос к API, сохраняет скриншот."""
    url = (f'{THUMBNAIL_URL}{THUMBNAIL_TOKEN}/thumbnail/'
           f'get?url=https://{requested_website}&width=640')
    try:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            data = response.content
            with open(f'media/{filename}', 'wb') as file:
                file.write(await data.read())
            logging.info(logging_status['success'])
    except Exception as error:
        err_message = logging_status['error'], error
        raise Exception(err_message)


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """
    По команде /start присылает сообщение с описанием функционала бота.
    """
    async with aiohttp.ClientSession() as session:
        await save_bot_user(session, dict(message.from_user))
        reply_message = await get_db_message(session, 'message/start')
        await message.reply(reply_message)


@dp.message_handler(content_types=ContentType.TEXT)
async def answer(message: types.Message) -> None:
    """
    В ответ на запрос пользователя присылает сообщение-заглушку, которую
    редактирует после получения скриншота.
    """
    request_time = time()
    async with aiohttp.ClientSession() as session:
        msg_text = await get_db_message(session, 'message/wait')
        reply_msg = await message.reply_photo(
            photo=(open('media/waiting.jpg', 'rb')),
            caption=msg_text
        )
        await save_data(session, {'bot_user_id': message.from_user.id,
                                  'requested_url': message.text})
    filename = '.'.join([strftime("%m%d%y"), str(message.from_user.id),
                         message.text, 'jpg'])
    await fetch_screenshot(message.text, filename)
    await reply_msg.edit_media(
        media=InputMediaPhoto(open(f'media/{filename}', 'rb'))
    )
    title = await get_title(message.text)
    time_used = str("%.2f" % (time() - request_time))
    await reply_msg.edit_caption(f'{title}\n Запрос выполнен '
                                 f'за {time_used} сек.')


@dp.message_handler()
async def unknown(message: types.Message) -> None:
    """
    В ответ на запрос, не проходящий валидацию, высылает сообщение об ошибке.
    """
    async with aiohttp.ClientSession() as session:
        reply_message = await get_db_message(session, 'message/unknown')
        await message.reply(reply_message)


def check_tokens() -> bool:
    """Проверка доступности переменных окружения."""
    return all([THUMBNAIL_TOKEN, THUMBNAIL_URL, TELEGRAM_TOKEN, DB_API_URL])


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s, '
               '%(lineno)s '
    )
    if not check_tokens():
        logging.critical('Отсутствует обязательная переменная окружения')
        sys.exit(0)

    executor.start_polling(dp, skip_updates=True)
