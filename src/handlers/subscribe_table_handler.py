from telegram import (
    Update
)

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

from src.handlers.handlers import cancel_callback

ADD_TABLE_URL, ADD_CELLS_RANGE, SUBSCRIBE_TABLE = range(3)


async def start_subscribe_table_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите ссылку на таблицу:")
    return ADD_TABLE_URL


async def add_cells_range_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    table_id = update.message.text.split('/')[-2] #TODO нормальный парсинг table_id
    context.user_data["table_id"] = table_id
    await update.message.reply_text("Введите ячейки:")
    return ADD_CELLS_RANGE


async def subscribe_table_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    cells_range = update.message.text
    chat_id = str(update.message.chat.id)
    table_id = context.user_data["table_id"]

    # sql = f"INSERT INTO google_sheets_follows(id, field, description) VALUES ({chat_id},{cells_range},{table_id} );"

    await update.message.reply_text("Подписка добавлена")
    return ConversationHandler.END


def subscribe_table_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("subscribe_changes", start_subscribe_table_callback)],
        states={
            ADD_TABLE_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_cells_range_callback)
            ],
            ADD_CELLS_RANGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, subscribe_table_callback)
            ],

        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
