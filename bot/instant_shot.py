import logging
import os
from time import strftime, time

import requests
from dotenv import load_dotenv
from telegram import InlineQueryResultPhoto, InputMediaPhoto, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          InlineQueryHandler, MessageHandler, Updater)

load_dotenv()

MEDIA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app/media/'
)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
THUMBNAIL_TOKEN = os.getenv('THUMBNAIL_TOKEN')
THUMBNAIL_URL = 'https://api.thumbnail.ws/api/'
DB_API_URL = 'http://db-api:8000/api/'


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def get_url(requested_website):
    return (f'{THUMBNAIL_URL}{THUMBNAIL_TOKEN}/thumbnail/get?'
            f'url=https://{requested_website}&width=640')


def get_screenshot(update):
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


def shot(update: Update, context: CallbackContext):
    with requests.get(url=f'{DB_API_URL}message/wait') as r:
        msg = context.bot.send_photo(
            chat_id=update.effective_chat.id,
            caption=r.json().get('text'),
            photo=open(f'{MEDIA}waiting.jpg', 'rb')
        )
    time_used, requested_website, url = get_screenshot(update)
    bot_user_id = update.message.from_user.id
    requested_url = update.message.text
    data = {'bot_user_id': bot_user_id, 'requested_url': requested_url}
    requests.post(
        url=f'{DB_API_URL}request/',
        json=data
    )
    with requests.get(url=f'{DB_API_URL}message/update') as r:
        context.bot.edit_message_media(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            media=InputMediaPhoto(media=url,
                                  caption=f'{requested_website}, \n'
                                          f'{r.json().get("text")} '
                                          f'{time_used}')
        )


def inline_shot(update: Update, context: CallbackContext):
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


def start(update: Update, context: CallbackContext):
    bot_user = update.message.from_user.to_dict()
    requests.post(url=f'{DB_API_URL}user/', json=bot_user)
    with requests.get(url=f'{DB_API_URL}message/start') as r:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=r.json().get('text'))


def unknown(update: Update, context: CallbackContext):
    with requests.get(url=f'{DB_API_URL}message/unknown') as r:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=r.json().get('text'))


if __name__ == '__main__':
    updater = Updater(TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.entity('url'), shot))
    updater.dispatcher.add_handler(InlineQueryHandler(inline_shot))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text & (~Filters.command), unknown)
    )

    updater.start_polling()

    updater.idle()
