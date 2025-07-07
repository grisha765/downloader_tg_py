import pyrogram.types
from bot.db.options import get_option, set_option
from bot.core.helpers import safe_call, Common
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


async def options_menu(message):
    user_id = message.from_user.id
    channel_scrap_button = pyrogram.types.InlineKeyboardButton(
        text=f'{"🟢" if user_id in Common.user_tasks else "🔴"} Videos watchdog',
        callback_data='option_watchdog'
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
    
    await safe_call(
        job_text,
        text=msg,
        reply_markup=buttons
    )

async def option_set(callback_query, option, value):
    user_id = callback_query.from_user.id
    await set_option(user_id, option, value)
    await callback_query.answer(f"You selected {value} {option}!")
    logging.debug(f'{user_id}: Selected {option}:{value}')
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
    await safe_call(
        callback_query.message.edit_text,
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
    await safe_call(
        callback_query.message.edit_text,
        text="Choose Refresh Period:",
        reply_markup=reply_markup
    )


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
