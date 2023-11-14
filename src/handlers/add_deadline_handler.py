from src.db.connection import conn

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


ADD_SUBJECT, ADD_ACTIVITY, ADD_DEADLINE  = range(3)
admin_usernames = ["gkashin"]

async def start_add_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    is_admin = update.message.from_user.username in admin_usernames
    if not is_admin:
        await update.message.reply_text("Sorry, you're not allowed to create a deadline.")
        return ConversationHandler.END

    await update.message.reply_text("Введите предмет:")

    return ADD_SUBJECT

async def add_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["SUBJECT"] = update.message.text

    await update.message.reply_text("Ввведите название активности:")

    return ADD_ACTIVITY


async def add_activity_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["ACTIVITY"] = update.message.text

    await update.message.reply_text("Ввведите дедлайн:")

    return ADD_DEADLINE

async def add_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["DEADLINE"] = update.message.text

    activity_id = context.user_data["ACTIVITY"]
    deadline = context.user_data["DEADLINE"]
    
    sql = "INSERT INTO deadlines(activity_id, deadline) values (%s, %s)"

    cur = conn.cursor()
    data = (activity_id, deadline)
    cur.execute(sql, data)
    conn.commit()
    conn.close()

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
