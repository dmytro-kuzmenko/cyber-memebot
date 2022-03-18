
import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, InputFile, InputMediaPhoto, ContentTypes  # TODO Realize photo saving in DB
from aiogram.utils import executor

from demo import Demo

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(BOT_TOKEN)

dp = Dispatcher(bot=bot)
runner = Demo()

dp.setup_middleware(LoggingMiddleware())

# region Photo loading
root = "images/"
img_names = [root+path for path in os.listdir(root)]

full_paths = [f"{f}/{i}" for f in img_names for i in os.listdir(f)]


# endregion

# region Start
@dp.message_handler(CommandStart())
async def start(msg: Message):
    return await msg.answer(f'Привіт, {msg.from_user.first_name}.\nНадішли запит')


# endregion

@dp.message_handler(content_types=ContentTypes.TEXT)
async def process(msg: Message):
    results = runner.run_model(msg.text)["indices"]
    to_send = [InputMediaPhoto(InputFile(full_paths[i])) for i in results]
    return await bot.send_media_group(msg.chat.id, to_send, disable_notification=True,
                                      reply_to_message_id=msg.message_id, allow_sending_without_reply=True)


if __name__ == '__main__':

    executor.start_polling(dp)
