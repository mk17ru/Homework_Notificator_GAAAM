from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

from src.handlers.handlers import cancel_callback

from src.db.helpers import get_full_relation


async def subscription_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = ""
    db_result = get_full_relation("deadline_follows")
    for val in db_result:
        msg = msg + str(val) + '\n' #форматирование добавить нужно
    db_result = get_full_relation("google_sheets_follows")
    for val in db_result:
        msg = msg + str(val) + '\n'
    return ConversationHandler.END


def subscription_list_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("subscription_list", subscription_list_callback)],
        states={},
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
