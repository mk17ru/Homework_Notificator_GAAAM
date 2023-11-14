from src.db.connection import conn
from datetime import datetime

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


ADD_SUBJECT, ADD_ACTIVITY, ADD_DEADLINE  = range(3)
admin_usernames = ["gkashin"]

async def start_add_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    is_admin = update.message.from_user.username in admin_usernames
    if not is_admin:
        await update.message.reply_text("Sorry, you're not allowed to create a deadline.")
        return ConversationHandler.END

    sql = "SELECT * FROM SUBJECTS;"

    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    conn.commit()

    subjects = [KeyboardButton(row[1]) for row in result]
    reply_markup = ReplyKeyboardMarkup([subjects], one_time_keyboard=True)

    await update.message.reply_text("Выберите предмет", reply_markup=reply_markup)

    return ADD_SUBJECT

async def add_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["SUBJECT"] = update.message.text
    subject = context.user_data["SUBJECT"]

    sql = "SELECT * FROM ACTIVITIES;"

    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    conn.commit()

    activities = [row[2] for row in result]
    reply_markup = ReplyKeyboardMarkup([activities], one_time_keyboard=True)

    await update.message.reply_text("Выберите активность", reply_markup=reply_markup)

    return ADD_ACTIVITY


async def add_activity_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["ACTIVITY"] = update.message.text

    await update.message.reply_text('Введите дату дедлайна в формате yyyy-mm-dd hh:mm')

    return ADD_DEADLINE

async def add_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["DEADLINE"] = update.message.text

    activity_id = context.user_data["ACTIVITY"]
    deadline = context.user_data["DEADLINE"]

    try:
        date = datetime.strptime(deadline, '%Y-%m-%d %H:%M')
    except ValueError:
        await update.message.reply_text('Неверный формат даты.')
        return ConversationHandler.END
            
    sql = "INSERT INTO deadlines(activity_id, deadline) values (1, %s)"

    cur = conn.cursor()
    data = (activity_id, date)
    cur.execute(sql, data)
    conn.commit()

    conn.close()

    await update.message.reply_text('Дедлайн успешно обновлен!')

    return ConversationHandler.END

async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END

def add_deadline_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_deadline", start_add_deadline_callback)],
        states={
            ADD_SUBJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_subject_callback)
            ],
            ADD_ACTIVITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_activity_callback)
            ],
            ADD_DEADLINE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_deadline_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
