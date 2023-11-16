from typing import List
from telegram import BotCommand, Bot
from telegram.ext import (
    CommandHandler,
    Application,
    PreCheckoutQueryHandler,

)

from src.handlers.handlers import *
from src.handlers.add_deadline_handler import *
from src.handlers.delete_subject_handler import *
from src.handlers.delete_activity_handler import *
from src.handlers.list_deadline_handler import *
from src.handlers.notifier import deadline_notifier
from src.handlers.notifier import google_sheets_notifier
from src.handlers.subscribe_deadline_handler import *
from src.handlers.subscribe_table_handler import *
from src.handlers.unsubscribe_table import *
from src.handlers.subscription_list_handler import *
from src.handlers.authorize_handler import *

from src.data_init import TOKEN
from src.models import *

import asyncio



def bot_start() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_callback))
    application.add_handler(add_deadline_builder())
    application.add_handler(list_deadline_builder())
    application.add_handler(subscribe_table_builder())
    application.add_handler(subscription_list_builder())
    application.add_handler(unsubscribe_table_builder())
    application.add_handler(authorize_builder())
    application.add_handler(subscribe_deadline_builder())
    application.add_handler(unsubscribe_deadline_builder())
    application.add_handler(delete_subject_builder())
    application.add_handler(delete_activity_builder())

    __init_commands(
        application,
        [
            BotCommand("start", "login user"),
            BotCommand("add_deadline", "add deadline"),
            BotCommand("delete_subject", "delete subject"),
            BotCommand("delete_activity", "delete activity"),
            BotCommand("list_deadline", "list deadlines"),
            BotCommand("subscription_list", "subscription list"),
            BotCommand("subscribe_changes", "subscribe changes"),
            BotCommand("unsubscribe_table", "unsubscribe table"),
            BotCommand("subscribe_deadline", "subscribe deadline"),
            BotCommand("unsubscribe_deadline", "unsubscribe deadline"),
            BotCommand("authorize", "google authorization"),
            BotCommand("cancel", "return back"),
        ]
    )

    job_queue = application.job_queue

    job_queue.run_repeating(deadline_notifier, interval=10, first=0, job_kwargs={'misfire_grace_time': 15*60})
    job_queue.run_repeating(google_sheets_notifier, interval=10, first=0, job_kwargs={'misfire_grace_time': 15*60})

    application.run_polling(allowed_updates=Update.ALL_TYPES)

def __init_commands(application, commands: List[BotCommand]):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.bot.set_my_commands(commands))