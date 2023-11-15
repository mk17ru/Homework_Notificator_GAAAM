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

ADD_TABLE_URL, ADD_CELLS_RANGE = range(2)


async def start_unsubscribe_table_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите ссылку на таблицу:")
    return ADD_TABLE_URL


async def add_cells_range_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    table_id = update.message.text.split('/')[-2]  # нормальный парсинг table_id
    context.user_data["table_id"] = table_id
    await update.message.reply_text("Введите ячейки:")
    return ADD_CELLS_RANGE


async def unsubscribe_table_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # sql = f"DELETE FROM googlesheets_follows where ..." #условия прописать бы
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
