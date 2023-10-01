import requests
from urllib.parse import urlencode

import zipfile
import io
from datetime import datetime
import os

import logging

from telegram import ForceReply, Update

from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import data_utils


logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Send a message when the command /start is issued."""

    user = update.effective_user

    await update.message.reply_html(

        rf"Здравствуйте, {user.mention_html()}! Этот бот поможет Вам обработать массив данных с фотоловушек. Просто отправьте мне ссылку на архив с изображениями (.zip) на Яндекс.Диск. Убедитесь, что архив содержит фото в корне без иных вложений.",

        reply_markup=ForceReply(selective=True),

    )



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Send a message when the command /help is issued."""

    await update.message.reply_text("Этот бот поможет Вам обработать массив данных с фотоловушек. Просто отправьте мне ссылку на архив с изображениями (.zip) на Яндекс.Диск. Убедитесь, что архив содержит фото в корне без иных вложений.")


# handlers 

async def linkHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = f'{update.message.text}'

    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']

    download_response = requests.get(download_url)
    timestamp = datetime.timestamp(datetime.now())
    dirpath = f'./data_{timestamp}'

    os.mkdir(dirpath)

    with zipfile.ZipFile(io.BytesIO(download_response.content), 'r') as zip_ref:
        zip_ref.extractall(dirpath)
    await update.message.reply_text("Архив распакован. Выполняем классификацию...")
    res = data_utils.Data(dirpath)
    res.get_result().to_csv(dirpath+'result.csv',index=False)
    await update.message.reply_text("Готово! Файл разметки:")
    await update.message.reply_document(open(os.path.join(dirpath+'result.csv')))


def main() -> None:


    application = Application.builder().token("6043998295:AAFhjT2MgadRLGTk81VuTvNL5heuMBACvkY").build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("help", help_command))


    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Entity("url"), linkHandler))
    #application.add_handler(MessageHandler(filters.Document.FileExtension("zip"), arcHandler))


    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":

    main()