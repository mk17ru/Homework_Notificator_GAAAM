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

from src.handlers.handlers import cancel_callback

LIST_DEADLINE  = range(1)

async def start_list_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите предмет:")

    return LIST_DEADLINE

async def list_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["SUBJECT"] = update.message.text

    sql = (
        f""" 
        SELECT a.name, d.deadline 
            FROM deadlines AS d
                INNER JOIN activities AS a 
                ON d.activity_id = a.id
                INNER JOIN subjects AS s 
                ON s.id = a.subject_id
        WHERE s.name = '{context.user_data["SUBJECT"]}'
        """
    )

    cur = conn.cursor()
    cur.execute(sql, (context.user_data["SUBJECT"]))
    await update.message.reply_text('\n'.join([f'{message[0]}: expires {message[1]}' for message in cur.fetchall()]))
    conn.commit()
    conn.close()

    return ConversationHandler.END

def list_deadline_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("list_deadline", start_list_deadline_callback)],
        states={
            LIST_DEADLINE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, list_deadline_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
