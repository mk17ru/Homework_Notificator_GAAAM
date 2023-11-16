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
from src.db.helpers import run_sql


ADD_TABLE_URL, ADD_CELLS_RANGE = range(2)


def get_table_id(update: Update):
    url_split = update.message.text.split('/')
    if len(url_split) < 6:
        return None
    url_parts = ['https:', '', 'docs.google.com', 'spreadsheets', 'd']
    for i in range(0, 5):
        if url_parts[i] != url_split[i]:
            return None

    return url_split[5]


async def start_subscribe_table_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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


async def subscribe_table_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    cells_range = update.message.text
    nums = "".join([c for c in cells_range if c.isdigit() or c == ":"]).split(':')
    if len(nums) != 2 or nums[0] != nums[1]:
        await update.message.reply_text("Некорректный формат ячеек! Диапазон должен быть строкой")
        return ConversationHandler.END
    chat_id = str(update.message.chat.id)
    table_id = context.user_data["table_id"]

    sql = f"INSERT INTO google_sheets_follows(following_chat_id, cells_range, table_id) VALUES (%s, %s, %s);"
    run_sql(sql, [chat_id, cells_range, table_id])

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
