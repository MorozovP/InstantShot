import logging
import os
import re
import sys
from time import strftime, time

import requests
from dotenv import load_dotenv
from telegram import (InlineQueryResultPhoto, InputMediaPhoto,
                      ReplyKeyboardMarkup, Update)
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          InlineQueryHandler, MessageHandler, Updater)

load_dotenv()

MEDIA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app/media/'
)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
THUMBNAIL_TOKEN = os.getenv('THUMBNAIL_TOKEN')
THUMBNAIL_URL = os.getenv('THUMBNAIL_URL')
DB_API_URL = os.getenv('DB_API_URL')

logging_status = {
    'error': 'При получении скриншота возникла ошибка.',
    'save_error': 'При сохранении данных возникла ошибка.',
    'save_success': 'Данные сохранены успешно.',
    'success': 'Скриншот получен.'
}


def save_data(data) -> None:
    """Сохраняет данные запроса в БД."""
    try:
        requests.post(url=f'{DB_API_URL}request/', json=data)
    except Exception as error:
        err_message = logging_status['save_error'], error
        raise Exception(err_message)
    else:
        logging.info(logging_status['save_success'])


def save_bot_user(data) -> None:
    """Сохраняет данные пользователя в БД."""
    try:
        requests.post(url=f'{DB_API_URL}user/', json=data)
    except Exception as error:
        err_message = logging_status['save_error'], error
        raise Exception(err_message)
    else:
        logging.info(logging_status['save_success'])


def get_url(requested_website) -> str:
    """Возвращает URL запрашиваемого скриншота."""
    return (f'{THUMBNAIL_URL}{THUMBNAIL_TOKEN}/thumbnail/get?'
            f'url=https://{requested_website}&width=640')


def get_screenshot(update) -> tuple:
    """
    Сохраняет скриншот на сервере и возвращает кортеж, содержащий следующие
    данные: время, затраченное на выполнение запроса, URL сайта из запроса
    пользователя, URL запрашиваемого скриншота.
    """
    request_time = time()
    current_date = strftime("%m%d%y")
    if update.message:
        user_id = str(update.message.from_user.id)
        requested_website = update.message.text
    else:
        user_id = str(update.inline_query.from_user.id)
        requested_website = update.inline_query.query
    url = get_url(requested_website)
    with requests.get(url, stream=True) as r:
        filename = '.'.join([current_date, user_id, requested_website, 'jpg'])
        open(f'{MEDIA}{filename}', 'wb').write(r.content)
        time_used = str("%.2f" % (time() - request_time)) + ' секунд.'
        return time_used, requested_website, url


def get_title(update) -> str:
    """Делает запрос к сайту и извлекает из ответа title."""
    headers = {
        "authority": "api.blocket.se",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98"',
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "sec-ch-ua-platform": "'Linux'",
        "accept": "*/*",
        "origin": "https://www.blocket.se",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.blocket.se/",
        "accept-language": "en-US,en;q=0.9"
    }
    requested_website = update.message.text
    try:
        n = requests.get(f'https://{requested_website}', headers=headers)
    except Exception as error:
        logging.info(logging_status['error'], error)
        return requested_website
    else:
        logging.info(logging_status['success'])
        return re.search('.*>(.*)</title', n.text, re.IGNORECASE).group(1)


def answer(update: Update, context: CallbackContext) -> None:
    """
    В ответ на запрос пользователя присылает сообщение-заглушку, которую
    редактирует после получения скриншота.
    """
    with requests.get(url=f'{DB_API_URL}message/wait') as r:
        msg = context.bot.send_photo(
            chat_id=update.effective_chat.id,
            caption=r.json().get('text'),
            photo=open(f'{MEDIA}waiting.jpg', 'rb')
        )
    try:
        time_used, requested_website, url = get_screenshot(update)
    except Exception as error:
        err_message = logging_status['error'], error
        raise Exception(err_message)
    else:
        logging.info(logging_status['success'])
    data = {'bot_user_id': update.message.from_user.id,
            'requested_url': update.message.text}
    save_data(data)
    title = get_title(update)
    with requests.get(url=f'{DB_API_URL}message/update') as r:
        context.bot.edit_message_media(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            media=InputMediaPhoto(media=url,
                                  caption=f'{title}, \n'
                                          f'{r.json().get("text")} '
                                          f'{time_used}')
        )


def inline_answer(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    if not query:
        return
    results = []
    time_used, requested_website, url = get_screenshot(update)
    results.append(
        InlineQueryResultPhoto(
            id=query,
            title=query,
            thumb_url=url,
            photo_url=url
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


def start(update: Update, context: CallbackContext) -> None:
    """
    По команде /start присылает сообщение с описанием функционала бота.
    """
    bot_user = update.message.from_user.to_dict()
    save_bot_user(bot_user)
    with requests.get(url=f'{DB_API_URL}message/start') as r:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=r.json().get('text'))


def unknown(update: Update, context: CallbackContext) -> None:
    """
    В ответ на запрос, не проходящий валидацию, высылает сообщение об ошибке.
    """
    with requests.get(url=f'{DB_API_URL}message/unknown') as r:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=r.json().get('text'))


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

    updater = Updater(TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.entity('url'), answer)
    )
    updater.dispatcher.add_handler(InlineQueryHandler(inline_answer))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text & (~Filters.command), unknown)
    )

    updater.start_polling()

    updater.idle()
