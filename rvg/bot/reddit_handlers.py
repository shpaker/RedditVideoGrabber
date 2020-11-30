import json
from logging import getLogger

from aiogram import types

from rvg.bot.instance import get_bot
from rvg.entries import RedditAudio, RedditVideo
from rvg.page import RedditPage
from rvg.utils import prettify_size

logger = getLogger(__name__)
# dp = get_dispatcher()


# regexp='https://www\.reddit\.com/r?[a-zA-Z0-9_.+-/#~]+'
# @dp.message_handler()
async def reddit_message_handler(message: types.Message):
    bot = get_bot()
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    logger.info(f'Receive {message.text} from {message.from_user.username}')
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')
    try:
        reddit_page = RedditPage(message.text)
        entries = await reddit_page.videos_entries()
    except Exception as err:
        logger.warning(err)
        await message.reply(f'Error processing {err.__class__.__name__}')
        raise

    if not entries:
        await message.reply(f'Video not found')

    row_btns = (
        types.InlineKeyboardButton(f'{entry.name} ({prettify_size(entry.entry_size)})',
                                   callback_data=json.dumps(
                                       entry.dict,
                                       separators=(',', ':'),
                                   )) for entry in entries)

    # for entry in entries:
    keyboard_markup.row(*row_btns)

    await message.reply('Choose resolution', reply_markup=keyboard_markup)


# @dp.callback_query_handler()
async def reddit_message_cb_handler(query: types.CallbackQuery):
    bot = get_bot()
    try:
        data = json.loads(query.data)
    except Exception as err:  # noqa
        return

    dash_id: str = data['d']
    audio_id: str = data.get('a')
    video_id: str = data['v']

    keyboard_markup = types.InlineKeyboardMarkup()
    await bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_markup,
    )
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text=f'Resolution: {video_id}'
    )
    video = RedditVideo(
        dash_id=dash_id,
        entry_id=video_id,
        audio=RedditAudio(dash_id=dash_id, entry_id=audio_id) if audio_id else None,
    )
    await bot.send_chat_action(chat_id=query.message.chat.id, action='record_video')
    data = await video.download()
    await bot.send_chat_action(chat_id=query.message.chat.id, action='upload_video')
    await query.message.reply_video(video=data)

    logger.info(f'Send video {dash_id}/{video_id} to {query.message.chat.username}')
