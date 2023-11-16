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

DELETE_ACTIVITY, CHOOSE_SUBJECT = range(2)

async def start_delete_activity_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_admin(update.message.chat.username):
        await update.message.reply_text("Извините, вам не разрешено удалять активности.")
        return ConversationHandler.END

    subjects = get_full_relation("SUBJECTS")
    context.user_data["SUBJECTS"] = subjects

    buttons = [KeyboardButton(subject[1]) for subject in subjects]
    reply_markup = ReplyKeyboardMarkup([buttons], one_time_keyboard=True)
    await update.message.reply_text("Выберите предмет", reply_markup=reply_markup)

    return CHOOSE_SUBJECT

async def choose_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    subject = update.message.text
    context.user_data["SUBJECT"] = subject

    subjects = context.user_data["SUBJECTS"]
    subject_id = next(filter(lambda record: record[1] == subject, subjects), None)[0]
    context.user_data["SUBJECT_ID"] = subject_id

    sql = "SELECT * FROM ACTIVITIES WHERE SUBJECT_ID=%s;"
    
    activities = run_sql(sql, (subject_id,))

    buttons = [KeyboardButton(activity[2]) for activity in activities]
    reply_markup = ReplyKeyboardMarkup([buttons], one_time_keyboard=True)
    await update.message.reply_text("Выберите активность", reply_markup=reply_markup)

    return DELETE_ACTIVITY

async def delete_activity_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    activity = update.message.text
    subject_id = context.user_data["SUBJECT_ID"]
    subject = context.user_data["SUBJECT"]
    sql = 'DELETE FROM ACTIVITIES WHERE NAME=%s and SUBJECT_ID=%s;'

    run_sql(sql, (activity, subject_id))

    await update.message.reply_text(f"Активность {activity} для предмета {subject} удалена.")

    return ConversationHandler.END


def delete_activity_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("delete_activity", start_delete_activity_callback)],
        states={
            DELETE_ACTIVITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_activity_callback)
            ],
            CHOOSE_SUBJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_subject_callback)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )