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

from src.db.helpers import run_sql


def check_already_taken_deadlines(activity, subject, period):
    sql = (
        f""" 
           SELECT count(*) FROM deadlines_sent
           where activity_id = %s and subject_id = %s and period = %s
           """
    )

    result = run_sql(sql, [activity, subject, period])

    return result[0][0] == 0


def add_already_taken_deadlines(activity, subject, period):

    sql = "INSERT INTO deadlines_sent(subject_id, activity_id, period) values (%s, %s, %s)"
    run_sql(sql, [subject, activity, period])



async def notifier(context: CallbackContext):
    sql = (
        f""" 
           SELECT df.following_user_id, s.name, a.name, d.deadline, d.activity_id, a.subject_id
               FROM deadline_follows AS df
                   INNER JOIN activities AS a 
                   ON df.subject_id = a.subject_id
                   INNER JOIN deadlines AS d
                   ON d.activity_id = a.id
                   INNER JOIN subjects AS s 
                   ON s.id = a.subject_id
           """
    )

    result = run_sql(sql, [])

    print(result)

    for message in result:
        current = datetime.now()
        current_intervals = [timedelta(hours=1), timedelta(days=1), timedelta(weeks=1)]
        for current_interval in current_intervals:
            if current <= message[3] < current + current_interval and check_already_taken_deadlines(message[4], message[5], current_interval.total_seconds()):
                add_already_taken_deadlines(message[4], message[5], current_interval.total_seconds())
                await context.bot.send_message(message[0],
                           text="Deadline for homework " + message[1] + " " + message[2] + " " + str(message[3]))

                break


