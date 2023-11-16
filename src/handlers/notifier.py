import hashlib
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
from src.utils import get_values


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


async def google_sheets_notifier(context: CallbackContext):
    select_sql = (
        f""" 
               SELECT following_chat_id, table_id, cells_range, range_hash, prev_value 
               FROM google_sheets_follows;
        """
    )

    update_sql = f"""
                        UPDATE google_sheets_follows 
                        SET range_hash = %s, prev_value = %s 
                        WHERE following_chat_id = %s AND table_id = %s AND cells_range = %s;
                         """

    db_result = run_sql(select_sql, [])

    print(db_result)

    for message in db_result:
        cur_value = get_values(message[1], message[2])
        print(cur_value)
        if not cur_value:
            continue
        cur_hash = hashlib.sha256(str(cur_value).encode('utf-8')).hexdigest()
        if not message[3] or not message[4]:
            run_sql(update_sql, [cur_hash, cur_value, message[0], message[1], message[2]])
            continue
        if str(cur_hash) != message[3]:
            await context.bot.send_message(
                message[0],
                text="New values in cells " + message[2]
            )
            run_sql(update_sql, [cur_hash, cur_value, message[0], message[1], message[2]])



