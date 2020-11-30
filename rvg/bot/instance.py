from functools import lru_cache
from os import environ

from aiogram import Bot


@lru_cache()
def get_bot():
    token = environ.get('RVG_BOT_TOKEN')
    if not token:
        raise ConnectionError
    return Bot(token=token)
