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


ADD_SUBJECT, ADD_DEADLINE_NAME  = range(2)

async def start_add_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите предмет:")

    return ADD_SUBJECT

async def add_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["SUBJECT"] = update.message.text

    await update.message.reply_text("Ввведите название дедлайна:")

    return ADD_DEADLINE_NAME


async def add_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["DEADLINE"] = update.message.text
    print(context.user_data["SUBJECT"]) # сохранилось!
    print(context.user_data["DEADLINE"]) # сохранилось!

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
            ADD_DEADLINE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_deadline_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
