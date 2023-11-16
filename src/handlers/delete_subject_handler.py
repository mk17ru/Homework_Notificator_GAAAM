from datetime import datetime, timedelta
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
    filters, CallbackContext,
)

from src.handlers.handlers import cancel_callback
from src.db.helpers import get_full_relation, run_sql, is_admin

DELETE_SUBJECT = range(1)

async def start_delete_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_admin(update.message.chat.username):
        await update.message.reply_text("Извините, вам не разрешено удалять предметы.")
        return ConversationHandler.END

    subjects = get_full_relation("SUBJECTS")
    buttons = [KeyboardButton(subject[1]) for subject in subjects]
    reply_markup = ReplyKeyboardMarkup([buttons], one_time_keyboard=True)
    await update.message.reply_text("Выберите предмет", reply_markup=reply_markup)

    return DELETE_SUBJECT

async def delete_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    subject = update.message.text
    sql = 'DELETE FROM SUBJECTS WHERE NAME=%s;'

    run_sql(sql, (subject,))

    await update.message.reply_text(f"Предмет {subject} удален.")

    return ConversationHandler.END


def delete_subject_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("delete_subject", start_delete_subject_callback)],
        states={
            DELETE_SUBJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_subject_callback)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )