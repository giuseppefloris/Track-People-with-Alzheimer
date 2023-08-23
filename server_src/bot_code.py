from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

Token = '6450165920:AAE288hF7Ndjxb9N_priwOn86A8Dt9HjddQ'
BOT_USERNAME = '@TPWA_bot'


# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, thanks for using our service. \n Now we will'
                                    'configure the service for you')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This are all the commands that you can use...')


async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('acc_data.txt', 'rb') as f:
        acc = f.read()
    with open('bpm_data.txt', 'rb') as f:
        bpm = f.read()
    await update.message.reply_text(f'Here your update:...\n'
                                    f'BPM:{bpm}\n'
                                    f'lo zio è caduto?:{acc}')


async def position_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('gps_data.txt', 'rb') as f:
        gps = f.read()
    await update.message.reply_text('Here the position:...\n'
                                    f'lo zio è scappato?:{gps}')


# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'update' in text:
        return 'Use the Update command'

    if 'position' in text:
        return 'Use the postion command'

    return 'I do not understand what you wrote'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    response: str = handle_response(text)
    print('Bot', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(Token).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('update', update_command))
    app.add_handler(CommandHandler('position', position_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)
    print('Polling...')
    app.run_polling(poll_interval=3)
