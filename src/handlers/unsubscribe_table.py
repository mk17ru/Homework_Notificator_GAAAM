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
from src.handlers.subscribe_table_handler import get_table_id  # перенести бы функцию
from src.db.helpers import run_sql

ADD_TABLE_URL, ADD_CELLS_RANGE = range(2)


async def start_unsubscribe_table_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите ссылку на таблицу:")
    return ADD_TABLE_URL


async def add_cells_range_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    table_id = get_table_id(update)
    if table_id is None:
        await update.message.reply_text("Неверная ссылка")
        return ConversationHandler.END
    context.user_data["table_id"] = table_id
    await update.message.reply_text("Введите ячейки:")
    return ADD_CELLS_RANGE


async def unsubscribe_table_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    cells_range = update.message.text
    table_id = context.user_data["table_id"]

    sql = f"DELETE FROM google_sheets_follows WHERE table_id = %s AND cells_range = %s"
    run_sql(sql, [table_id, cells_range])
    await update.message.reply_text("Подписка удалена")

    return ConversationHandler.END


def unsubscribe_table_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("unsubscribe_table", start_unsubscribe_table_callback)],
        states={
            ADD_TABLE_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_cells_range_callback)
            ],
            ADD_CELLS_RANGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, unsubscribe_table_callback)
            ],

        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
