from datetime import datetime
import asyncio
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
from src.db.connection import conn
from src.db.helpers import get_full_relation, run_sql

CHOOSE_SUBJECT, ADD_SUBJECT, CHOOSE_ACTIVITY, ADD_ACTIVITY, ADD_DEADLINE, START = range(6)
admin_usernames = ["gkashin", "imashevchenko", "chichaaaps"]

async def start_add_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    is_admin = update.message.from_user.username in admin_usernames
    if not is_admin:
        await update.message.reply_text("Sorry, you're not allowed to create a deadline.")
        return ConversationHandler.END

    subjects = get_full_relation("SUBJECTS")
    context.user_data["SUBJECTS"] = subjects
    buttons = [KeyboardButton(subject[1]) for subject in subjects]
    reply_markup = ReplyKeyboardMarkup([buttons, ['Создать новый']], one_time_keyboard=True)
    await update.message.reply_text("Выберите предмет", reply_markup=reply_markup)

    return CHOOSE_SUBJECT

async def add_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["SUBJECT"] = update.message.text
    subject = context.user_data["SUBJECT"]

    sql = 'INSERT INTO SUBJECTS(name) VALUES(%s) RETURNING id;'

    result = run_sql(sql, (subject,))
    if not result:
        await update.message.reply_text(f"Предмет с именем {subject} уже существует.\nВведите любое значение для продолжения.")
        context.user_data.clear()
        return START

    subject_id = result[0][0]
    context.user_data["SUBJECT_ID"] = subject_id

    await update.message.reply_text("Введите название активности:")

    return ADD_ACTIVITY

async def choose_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if "SUBJECT" not in context.user_data:
        context.user_data["SUBJECT"] = update.message.text

    subject = context.user_data["SUBJECT"]
    if subject == 'Создать новый':
        await update.message.reply_text("Введите название предмета:")
        return ADD_SUBJECT

    subjects = context.user_data["SUBJECTS"]
    
    subject_id = next(filter(lambda record: record[1] == subject, subjects), None)[0]
    context.user_data["SUBJECT_ID"] = subject_id

    sql = 'SELECT * FROM ACTIVITIES WHERE SUBJECT_ID=%s;'
    activities = run_sql(sql, (subject_id,))
    context.user_data["ACTIVITIES"] = activities

    buttons = [activity[2] for activity in activities]
    reply_markup = ReplyKeyboardMarkup([buttons, ['Создать новую']], one_time_keyboard=True)
    await update.message.reply_text("Выберите активность", reply_markup=reply_markup)

    return CHOOSE_ACTIVITY

async def choose_activity_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if "ACTIVITY" not in context.user_data:
        context.user_data["ACTIVITY"] = update.message.text
        activity = context.user_data["ACTIVITY"]
        if activity == 'Создать новую':
            await update.message.reply_text("Введите название активности:")
            return ADD_ACTIVITY

        activities = context.user_data["ACTIVITIES"]
        activity_id = next(filter(lambda record: record[2] == activity, activities), None)[0]
        context.user_data["ACTIVITY_ID"] = activity_id

    await update.message.reply_text('Введите дату дедлайна в формате dd-mm-yyyy hh:mm')

    return ADD_DEADLINE

async def add_activity_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    activity = update.message.text

    subject = context.user_data["SUBJECT"]
    subject_id = context.user_data["SUBJECT_ID"]
    sql = 'INSERT INTO ACTIVITIES(subject_id, name) VALUES(%s, %s) RETURNING id;'
    result = run_sql(sql, (subject_id, activity))
    if not result:
        await update.message.reply_text(f"Активность с именем {activity} для предмета {subject} уже существует.\nВведите любое значение для продолжения.")
        del context.user_data["ACTIVITY"]
        return CHOOSE_SUBJECT
    
    context.user_data["ACTIVITY"] = update.message.text

    activity_id = result[0][0]
    context.user_data["ACTIVITY_ID"] = activity_id

    await update.message.reply_text('Введите дату дедлайна в формате dd-mm-yyyy hh:mm UTC')

    return ADD_DEADLINE

async def add_deadline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["DEADLINE"] = update.message.text

    activity_id = context.user_data["ACTIVITY_ID"]

    deadline = context.user_data["DEADLINE"]

    try:
        date = datetime.strptime(deadline, '%d-%m-%Y %H:%M')
        context.user_data.clear()
    except ValueError:
        await update.message.reply_text('Неверный формат даты.\nВведите любое значение для продолжения.')
        return CHOOSE_ACTIVITY
    
    sql = "INSERT INTO deadlines(activity_id, deadline) values (%s, %s) ON CONFLICT (activity_id) DO UPDATE SET deadline = excluded.deadline;"
    run_sql(sql, (activity_id, date))

    await update.message.reply_text('Дедлайн успешно обновлен!')

    return ConversationHandler.END


def add_deadline_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_deadline", start_add_deadline_callback)],
        states={
            CHOOSE_SUBJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_subject_callback)
            ],
            ADD_SUBJECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_subject_callback)
            ],
            CHOOSE_ACTIVITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_activity_callback)
            ],
            ADD_ACTIVITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_activity_callback)
            ],
            ADD_DEADLINE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_deadline_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_deadline_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )