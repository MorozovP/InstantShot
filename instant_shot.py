import os, requests
from time import strftime, time
import logging
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    InputMediaPhoto,
    InlineQueryResultDocument, InlineQueryResultPhoto
)
from dotenv import load_dotenv
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    InlineQueryHandler
)
from PIL import Image
from io import BytesIO

load_dotenv()

MEDIA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'InstantShot/media'
)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
THUMBNAIL_TOKEN = os.getenv('THUMBNAIL_TOKEN')
URL = 'https://api.thecatapi.com/v1/images/search'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def get_screenshot(update, context):
    now = time()
    date = strftime("%m%d%y")
    user_id = str(update.message.from_user.id)
    requested_website = update.message.text
    url = (f'https://api.thumbnail.ws/api/{THUMBNAIL_TOKEN}/thumbnail/get?url'
           f'=https://{requested_website}&width=640')
    with requests.get(url, stream=True) as r:
        filename = '.'.join([date, user_id, requested_website, 'jpg'])
        file_path = f'{MEDIA}/{filename}'
        open(file_path, 'wb').write(r.content)
        time_used = time() - now
        return file_path, time_used, requested_website


async def shot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await context.bot.send_photo(chat_id=update.effective_chat.id,
                                       caption='Это будет непросто, но '
                                               'я постараюсь. Наберись '
                                               'терпения...',
                                       photo=open('waiting.jpg', 'rb'))
    file_path, time_used, requested_website = await get_screenshot(update,
                                                                   context)

    await context.bot.edit_message_media(
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        media=InputMediaPhoto(
            media=open(file_path, 'rb'),
            caption=f'https://{requested_website} \n'
                    f'запрос выполнен за {"%.2f" % time_used} секунд'
        ))

a = 'https://api.thumbnail.ws/api/YOUR-FREE-API-KEY/thumbnail/get?url=https://www.google.com/&width=640'
async def inline_shot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    print(query)
    results.append(
        InlineQueryResultPhoto(
            id=query,
            title=query,
            thumb_url=f'https://api.thumbnail.ws/api/abfbe1c38573e86ce4544bd3e3e79da9f1bf7d354ea3/thumbnail/get?url=https://{query}/&width=640',
            photo_url=f'https://api.thumbnail.ws/api/abfbe1c38573e86ce4544bd3e3e79da9f1bf7d354ea3/thumbnail/get?url=https://{query}/&width=640'
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Привет! Для получения скриншота '
                                        'пришли мне адрес сайта, например, '
                                        'mail.ru')


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Не похоже на адрес сайта, '
                                        'попробуй еще раз.')


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    start_handler = CommandHandler('start', start)
    shot_handler = MessageHandler(filters.Entity('url'), shot)
    inline_shot_handler = InlineQueryHandler(inline_shot)
    unknown_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), unknown)

    application.add_handler(start_handler)
    application.add_handler(shot_handler)
    application.add_handler(inline_shot_handler)
    application.add_handler(unknown_handler)

    application.run_polling()
