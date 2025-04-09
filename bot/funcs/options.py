import pyrogram.types, asyncio
from bot.db.options import get_option, set_option
from bot.funcs.video_auto import auto_video_msg
from bot.core.classes import Common
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


async def options_menu(message):
    user_id = message.from_user.id
    channel_scrap_button = pyrogram.types.InlineKeyboardButton(
        text=f'{"🟢" if user_id in Common.user_tasks else "🔴"} Channels Scrap',
        callback_data='option_channelscrap'
    )

    buttons = pyrogram.types.InlineKeyboardMarkup(
        [
            [pyrogram.types.InlineKeyboardButton(
                text='Quality',
                callback_data='option_quality')],
            [pyrogram.types.InlineKeyboardButton(
                text='Refresh Period',
                callback_data='option_refresh')],
            [channel_scrap_button]
        ]
    )
    msg = 'Options:'

    if getattr(message, 'data', None) is not None:
        job_text = message.message.edit_text
    else:
        job_text = message.reply_text
    
    await job_text(
        text=msg,
        reply_markup=buttons
    )

async def option_set(callback_query, option, value):
    user_id = callback_query.from_user.id
    await set_option(user_id, option, value)
    await callback_query.answer(f"You selected {value} {option}!")
    logging.debug(f'{user_id}: Selected {value}:{option}')
    await options_menu(callback_query)


async def quality_menu(callback_query):
    user_id = callback_query.from_user.id
    current_value = await get_option(user_id, "quality") or "Medium"
    possible_values = ["Low", "Medium", "High"]

    buttons = []
    for val in possible_values:
        check_mark = "✅" if val == current_value else ""
        buttons.append(
            [
                pyrogram.types.InlineKeyboardButton(
                    text=f"{check_mark}{val}",
                    callback_data=f"set_option_quality_{val}"
                )
            ]
        )

    buttons.append(
        [
            pyrogram.types.InlineKeyboardButton(
                text="Back",
                callback_data="option_back"
            )
        ]
    )

    reply_markup = pyrogram.types.InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(
        text="Choose Quality:",
        reply_markup=reply_markup
    )


async def refresh_menu(callback_query):
    user_id = callback_query.from_user.id
    current_value = await get_option(user_id, "refresh") or "15min"
    possible_values = ["15min", "30min", "1h", "6h", "12h", "1d"]

    buttons = []
    for val in possible_values:
        check_mark = "✅" if val == current_value else ""
        buttons.append(
            [
                pyrogram.types.InlineKeyboardButton(
                    text=f"{check_mark}{val}",
                    callback_data=f"set_option_refresh_{val}"
                )
            ]
        )

    buttons.append(
        [
            pyrogram.types.InlineKeyboardButton(
                text="Back",
                callback_data="option_back"
            )
        ]
    )

    reply_markup = pyrogram.types.InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_text(
        text="Choose Refresh Period:",
        reply_markup=reply_markup
    )


async def channel_scrap_switch(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in Common.user_tasks:
        Common.user_tasks[user_id].cancel()
        Common.user_tasks.pop(user_id, None)
        await callback_query.answer("Channels auto scrap stop.")
        logging.debug(f'{user_id}: Channels scrap task stop')
        await options_menu(callback_query)
    else:
        Common.user_tasks[user_id] = asyncio.create_task(auto_video_msg(client, user_id))
        await callback_query.answer("Channels auto scrap start.")
        logging.debug(f'{user_id}: Channels scrap task start')
        await options_menu(callback_query)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
