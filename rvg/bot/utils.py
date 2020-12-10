from functools import lru_cache

from aiogram import Dispatcher

from rvg.bot.instance import get_bot
from rvg.bot.message_handlers import reddit_message_handler, reddit_message_cb_handler
from rvg.constants import REDDIT_URL_PATTERN


@lru_cache()
def get_dispatcher() -> Dispatcher:
    bot = get_bot()
    dispatcher = Dispatcher(bot)
    dispatcher.register_message_handler(reddit_message_handler, regexp=REDDIT_URL_PATTERN)
    dispatcher.register_callback_query_handler(reddit_message_cb_handler)
    return dispatcher
