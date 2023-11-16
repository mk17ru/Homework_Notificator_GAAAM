import hashlib
import ast
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


def ind_to_cell(start, diff):
    rev = start[::-1]
    ind = 0
    is_first = True
    mult = 1
    for c in rev:
        if is_first:
            ind += ord(c) - ord('A')
            is_first = False
            continue
        mult *= 26
        ind += (ord(c) - ord('A') + 1) * mult

    ind += diff
    res = ''
    is_first = 0
    while ind > 0:
        res += chr(ind % 26 + ord('A') - is_first)
        is_first = 1
        ind //= 26

    return res[::-1]

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
            print("problems with extracting from table!")
            continue
        cur_hash = hashlib.sha256(str(cur_value).encode('utf-8')).hexdigest()
        if message[3] is None or message[4] is None:
            run_sql(update_sql, [cur_hash, cur_value, message[0], message[1], message[2]])
            continue
        if str(cur_hash) != message[3]:
            prev_list = ast.literal_eval(message[4])
            cur_list = ast.literal_eval(cur_value)
            new_vals_added = {}
            for i in range(0, len(cur_list)):
                if i >= len(prev_list):
                    new_vals_added[i] = cur_list[i]
                    continue
                if cur_list[i] != prev_list[i]:
                    new_vals_added[i] = cur_list[i]
            msg = f"ADDED in table https://docs.google.com/spreadsheets/d/{message[1]}:\n"
            start = "".join([c for c in message[2] if not c.isdigit()]).split(':')[0]
            nums = "".join([c for c in message[2] if c.isdigit() or c == ":"]).split(':')
            for val in new_vals_added:
                msg += f"{new_vals_added[val]} in cell {ind_to_cell(start, val)}{nums[0]}\n"

            await context.bot.send_message(
                message[0],
                msg
            )
            run_sql(update_sql, [cur_hash, cur_value, message[0], message[1], message[2]])



