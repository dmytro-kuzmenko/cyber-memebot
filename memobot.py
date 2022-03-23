
import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, InputFile, InputMediaPhoto, ContentTypes  # TODO Realize photo saving in DB
from aiogram.utils import executor

from database import get_index_maps
from demo import Demo
from config import config

bot = Bot(config.BOT_TOKEN)

dp = Dispatcher(bot=bot)
runner = Demo()

dp.setup_middleware(LoggingMiddleware())

# region Photo loading
photos = await get_index_maps()
# endregion

# region Start
@dp.message_handler(CommandStart())
async def start(msg: Message):
    return await msg.answer(f'Привіт, {msg.from_user.first_name}.\nНадішли запит')


# endregion



@dp.message_handler(commands=["id"]) # know id
async def get_chat_id(msg: Message):
    return await msg.answer(msg.chat.id)


@dp.message_handler(content_types=ContentTypes.TEXT)
async def process(msg: Message):
    results = runner.run_model(msg.text)["indices"]
    to_send = [InputMediaPhoto(photos[i]) for i in results]
    return await bot.send_media_group(msg.chat.id, to_send, disable_notification=True,
                                      reply_to_message_id=msg.message_id, allow_sending_without_reply=True)


if __name__ == '__main__':

    executor.start_polling(dp)
