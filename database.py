import os
import asyncio
import asyncpg
from typing import List
from config import config


async def _collect_info() -> list[int, int, str]:
    from memobot import bot
    from aiogram.types import InputFile
    root = "images/"
    img_folders = [root + path for path in os.listdir(root)]

    full_paths = [f"{f}/{i}" for f in img_folders for i in os.listdir(f)]
    print(full_paths)
    id_map, photos = {}, []
    for net_id, name in enumerate(full_paths):
        msg = await bot.send_photo(config.SAVE_CHAT, InputFile(name))
        await asyncio.sleep(3.5)
        photos.append((net_id, msg.photo[0].file_id, name))
    return photos


async def _initialize_db(photos):
    conn = await asyncpg.connect(config.DATABASE_URL)
    try:
        await conn.execute("DROP TABLE IF EXISTS photos;")
        await conn.execute("""CREATE TABLE IF NOT EXISTS photos(
        net_id SMALLINT NOT NULL PRIMARY KEY ,
        tg_id TEXT NOT NULL,
        name TEXT
        );""")

        await conn.copy_records_to_table('photos', records=photos)
        return True
    finally:
        await conn.close()


async def _initialize():  # initialize db (check collect_info)
    photos = await _collect_info()
    if await _initialize_db(photos):
        print("Completed.")
    else:
        print("Error")


async def get_index_maps():
    conn = await asyncpg.connect(config.DATABASE_URL)
    res = {}
    try:
        records = await conn.fetch("SELECT net_id, tg_id FROM photos")
        for rec in records:
            res[rec[0]] = rec[1]
        return res
    finally:
        await conn.close()

if __name__ == '__main__':
    print("Started")
    print(asyncio.run(get_index_maps()))
    print("Stopped")

