from functools import lru_cache

from aiogram import Dispatcher

from rvg.bot.instance import get_bot
from rvg.bot.message_handlers import reddit_message_handler, reddit_message_cb_handler


@lru_cache()
def get_dispatcher() -> Dispatcher:
    bot = get_bot()
    dispatcher = Dispatcher(bot)
    dispatcher.register_message_handler(reddit_message_handler,
                                        regexp=r'https://www.reddit.com/r?[a-zA-Z0-9_.+-/#~]+')
    dispatcher.register_callback_query_handler(reddit_message_cb_handler)
    return dispatcher
