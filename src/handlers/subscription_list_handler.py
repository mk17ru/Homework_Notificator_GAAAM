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

from src.db.helpers import run_sql


async def subscription_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = ""
    sql = (
        f""" 
               SELECT df.following_chat_id, s.name, a.name, d.deadline, d.activity_id, a.subject_id
                   FROM deadline_follows AS df
                       INNER JOIN activities AS a 
                       ON df.subject_id = a.subject_id
                       INNER JOIN deadlines AS d
                       ON d.activity_id = a.id
                       INNER JOIN subjects AS s 
                       ON s.id = a.subject_id
                   WHERE df.following_chat_id = %s; 
               """
    )
    db_result = run_sql(sql, [update.message.chat.id])
    for val in db_result:
        msg = msg + f"Deadline for homework {val[1]} {val[2]} {str(val[3])} UTC" + '\n'

    sql = (
        f""" 
                       SELECT table_id, cells_range 
                       FROM google_sheets_follows
                       WHERE following_chat_id = %s;
                """
    )
    db_result = run_sql(sql, [update.message.chat.id])
    for val in db_result:
        msg = msg + f"Subscription on table https://docs.google.com/spreadsheets/d/{val[0]} on cells {val[1]} " + '\n'
    await update.message.reply_text(msg)

    return ConversationHandler.END


def subscription_list_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("subscription_list", subscription_list_callback)],
        states={},
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
