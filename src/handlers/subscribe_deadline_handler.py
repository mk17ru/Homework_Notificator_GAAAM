from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup
)

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

from src.db.helpers import get_full_relation, run_sql
from src.handlers.handlers import cancel_callback

SUBSCRIBE_SUBJECT = range(1)


async def start_subscribe_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    result = get_full_relation("subjects")
    subjects = [KeyboardButton(row[1]) for row in result]
    reply_markup = ReplyKeyboardMarkup([subjects], one_time_keyboard=True)

    await update.message.reply_text("Выберите предмет", reply_markup=reply_markup)

    return SUBSCRIBE_SUBJECT


async def subscribe_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["SUBJECT"] = update.message.text
    chat_id = str(update.message.chat.id)
    subject = context.user_data["SUBJECT"]

    subject_id = run_sql(f"SELECT id FROM subjects AS s WHERE s.name = '{subject}'")[0][0]
    sql = f"INSERT INTO deadline_follows(following_user_id, subject_id) VALUES ({chat_id}, {subject_id});"
    run_sql(sql)
    await update.message.reply_text("Подписка добавлена")
    return ConversationHandler.END


def subscribe_deadline_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("subscribe_deadline", start_subscribe_deadline_callback)],
        states={
            SUBSCRIBE_SUBJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, subscribe_deadline_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
