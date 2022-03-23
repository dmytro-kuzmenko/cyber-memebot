import os


class Config:
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    SAVE_CHAT: int = os.getenv("SAVE_CHAT")
    DATABASE_URL: str = os.environ["DATABASE_URL"]


config = Config()
