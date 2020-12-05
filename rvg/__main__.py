import logging
from os import environ

import sentry_sdk
from aiogram.utils import executor

from rvg.bot import dispatcher

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    sentry_url = environ.get('RVG_SENTRY_URL')
    sentry_env = environ.get('RVG_SENTRY_ENV')
    if sentry_url:
        sentry_sdk.init(
            sentry_url,
            environment=sentry_env,
            traces_sample_rate=1.0,
        )
    executor.start_polling(dispatcher, skip_updates=True)
