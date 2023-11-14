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

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ADD_TABLE_URL, ADD_CELLS_RANGE, SUBSCRIBE_TABLE = range(3)
SCOPES = "https://www.googleapis.com/auth/spreadsheets.readonly"


async def start_subscribe_table_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите ссылку на таблицу:")
    return ADD_TABLE_URL


async def add_cells_range_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = update.message.text.split('/')[-2]
    context.user_data["URL"] = url
    await update.message.reply_text(url)
    await update.message.reply_text("Введите ячейки:")
    return ADD_CELLS_RANGE


async def subscribe_table_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["CELLS_RANGE"] = update.message.text

    if not os.path.exists("token.json"):
        await update.message.reply_text("Token does not exists")
        return ConversationHandler.END

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        result = (
            sheet.values()
                .get(spreadsheetId=context.user_data["URL"], range=context.user_data["CELLS_RANGE"])
                .execute()
        )
        values = result.get("values", [])

        if not values:
            await update.message.reply_text("Values is null")
            return ConversationHandler.END
        msg = ""
        for row in values:
            msg = msg + str(row) + "\n"
    except HttpError as err:
        await update.message.reply_text("Error occured: " + str(err))
        return ConversationHandler.END
    await update.message.reply_text(msg)
    return ConversationHandler.END


def subscribe_table_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("subscribe_changes", start_subscribe_table_callback)],
        states={
            ADD_TABLE_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_cells_range_callback)
            ],
            ADD_CELLS_RANGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, subscribe_table_callback)
            ],

        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
