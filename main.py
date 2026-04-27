from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8604959641:AAFLVWtV9BdB4Qhreu5pqEOMgaWvyV41T2E"
SOURCE_CHAT_ID = -1003983646730
TARGET_CHAT_ID = -1001174798090

async def forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.chat.id == SOURCE_CHAT_ID:
        await context.bot.copy_message(
            chat_id=TARGET_CHAT_ID,
            from_chat_id=SOURCE_CHAT_ID,
            message_id=update.channel_post.message_id
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, forward))

app.run_polling()
