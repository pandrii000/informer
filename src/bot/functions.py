from functools import wraps
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
import logging
import telegram

from src.config.config import CONFIG
from src.bot.utils import get_update_messages
from src.api import database


# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)

HELP = """
Commands available:
    - start - Start bot
    - help - Help
    - update - Update
    - analyse - Analyse
    - queries - Queries
    - clean_db - Clean database (auto-backup)
    - backup_db - Backup database
    - add_query - Add query
    - remove_query - Remove query
    - set_time_interval - Set time interval
    - get_time_interval - Get time interval
"""


def restricted(func):
    """Restrict usage of func to allowed users only and replies if necessary"""

    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != CONFIG["telegram"]["my_chat_id"]:

            update.message.reply_text("User disallowed.")

            message = "WARNING: Unauthorized access denied for {}({}) with request: {}".format(
                update.effective_user.username, user_id, update.effective_message.text
            )

            context.bot.send_message(
                chat_id=CONFIG["telegram"]["my_chat_id"],
                text=message,
            )

            return  # quit function
        return func(update, context, *args, **kwargs)

    return wrapped


@restricted
def command_start(update, context):
    username = update.effective_user.username
    context.bot.send_message(
        update.effective_message.chat_id,
        text=f"Hi, {username}!",
    )


def command_help(update, context):
    context.bot.send_message(
        update.effective_message.chat_id,
        text=HELP,
    )


@restricted
def command_update(update, context):
    messages, num_updates = get_update_messages(max_updates=1)

    if len(messages) == 0:
        messages = ["Nothing new."]
    else:
        messages = [
            "There are <b>{}/{}</b> new repositories!".format(
                len(messages), num_updates
            )
        ] + messages

    for message in messages:
        context.bot.send_message(
            update.effective_message.chat_id,
            text=message,
            parse_mode=telegram.ParseMode.HTML,
        )


@restricted
def command_queries(update, context):
    queries = database.get_all_query()
    message = "<b>Queries list ({}):</b>\n".format(len(queries)) + "\n".join(queries)
    for i in range(0, len(message), 4096):
        context.bot.send_message(
            update.effective_message.chat_id,
            message[i : i + 4096],
            parse_mode=telegram.ParseMode.HTML,
        )


@restricted
def command_add_query(update, context):
    args = update.effective_message.text.split(" ", 1)
    assert len(args) > 1, "You need to specify query"
    query = args[1]
    database.add_query(query)
    context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text="Successfully added {}".format(query),
    )


@restricted
def command_remove_query(update, context):
    args = update.effective_message.text.split(" ", 1)
    assert len(args) > 1, "You need to specify query"
    query = args[1]
    database.delete_query(value=query)
    context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text="Successfully removed {}".format(query),
    )


# @restricted
# def command_get_time_interval(update, context):
#     time_interval = get_time_interval()
#     context.bot.send_message(
#         chat_id=update.effective_message.chat_id,
#         text='Time interval is {}'.format(str(time_interval)),
#     )


@restricted
def forwarded_message(update, context):
    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Avoiding-flood-limits
    # sleep(3.001)
    context.bot.send_message(
        chat_id=FORWARD_CHAT_ID,
        text=update.effective_message.text_html,
        parse_mode=telegram.ParseMode.HTML,
    )
    context.bot.delete_message(
        chat_id=MY_CHAT_ID, message_id=update.effective_message.message_id
    )


@restricted
def error_handler(update, context):
    message = "Error: %s" % context.error
    context.bot.send_message(chat_id=update.effective_message.chat_id, text=message)
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def get_updater():
    updater = Updater(CONFIG["telegram"]["bot"]["token"], use_context=True)
    return updater


def serve_bot():
    """Start the bot."""
    updater = get_updater()
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", command_start))
    dp.add_handler(CommandHandler("help", command_help))
    dp.add_handler(CommandHandler("update", command_update))
    dp.add_handler(CommandHandler("queries", command_queries))
    dp.add_handler(CommandHandler("add_query", command_add_query))
    dp.add_handler(CommandHandler("remove_query", command_remove_query))

    dp.add_handler(MessageHandler(Filters.text, forwarded_message))
    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    serve_bot()
