from datetime import datetime, timedelta, timezone
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

from src.db.helpers import run_sql


def delete_outdated_deadlines():

    sql = "DELETE FROM deadlines AS d WHERE d.deadline < (now() at time zone 'utc')"
    run_sql(sql)


async def deadline_notifier(context: CallbackContext):
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
           """
    )

    result = run_sql(sql) or []

    print(result)

    for message in result:
        current = datetime.utcnow()
        current_intervals = [timedelta(hours=1), timedelta(days=1), timedelta(weeks=1)]
        for current_interval in current_intervals:
            if current + current_interval - timedelta(seconds=10) <= message[3] <= current + current_interval:
                await context.bot.send_message(
                    message[0],
                    text=f"Deadline for homework {message[1]} {message[2]} {str(message[3])} UTC"
                )
                break
    delete_outdated_deadlines()


