import os.path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from wifi import in_out_position
from wifi import learn_inside_locations, train_model, predict
from authentication import authenticate
from gps import retrieve_position
from tinydb import TinyDB, Query
import requests

Token = '6450165920:AAF0pJ0I4vhDFMMe8yJ4PwcN0G4XlkVC5Kc'
BOT_USERNAME = '@TPWA_bot'


# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, thanks for using our service. '
                                    '\n Now we will configure the service for you\n '
                                    r'First, authenticate your device by using the command /authenticate')


async def authenticate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    Client = Query()
    results = clients_table.search(Client.chat_id == update.effective_user.id)
    db.close()

    if len(results) != 0:
        await update.message.reply_text('Device already authenticated')
    else:
        await update.message.reply_text('Write the authentication token provided with the device')


async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    Client = Query()
    result = clients_table.search(Client.chat_id == update.effective_user.id)
    if len(result) == 0:
        await update.message.reply_text(f'You have first to authenticate your device')
        db.close()
    else:
        clients_table.update({"setup": True}, (Client.chat_id == update.effective_user.id))
        db.close()
        await update.message.reply_text('This is the setup of the device. \n First select a geofence in meters. '
                                        'Insert only numbers')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This are all the commands that you can use...\n'
                                    r'/start to initiate the service '
                                    '\n'
                                    r'/authenticate to match you smartphone with your device'
                                    '\n'
                                    r'/setup to let the device learn your inside positions'
                                    '\n'
                                    r'/position to check the current position'
                                    '\n'
                                    r'/delete to delete the current device configuration')
async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    gps_house_coord = db.table('gps_house_coord')
    inside_locations = db.table('inside_locations')
    Client = Query()
    client_id = clients_table.search(Client.chat_id == update.effective_user.id)
    client = client_id[0]['client_id']

    clients_table.remove(Client.client_id.all(client))
    gps_house_coord.remove(Client.client_id.all(client))
    inside_locations.remove(Client.client_id.all(client))
    db.close()
    await update.message.reply_text('Configuration Deleted\n')

async def position_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    inside_locations = db.table('inside_locations')
    Client = Query()
    result = clients_table.search(Client.chat_id == update.effective_user.id)

    if len(result) == 0:
        await update.message.reply_text(f'You have first to authenticate and setup your device')
        db.close()
    else:
        client_id = result[0]['client_id']
        result_inside = inside_locations.search(Client.client_id == client_id)

        if len(result_inside) == 0:
            await update.message.reply_text(f'You have first to setup your device')
            db.close()
        else:
            clients_table.update({'setup': False}, (Client.chat_id == update.effective_user.id))
            client_id = clients_table.search(Client.chat_id == update.effective_user.id)
            client_id = client_id[0]

            if not client_id['train']:
                train_model(update.effective_user.id)
                clients_table.update({'train': True}, (Client.chat_id == update.effective_user.id))

            db.close()

            position = in_out_position(client_id['client_id'])
            if position == 'inside':
                pred_position, occupancy = predict(update.effective_user.id)
                await update.message.reply_text('Here the inside position:...\n'
                                                f'{pred_position} \n'
                                                f'Occupancy: {occupancy}')

            if position == 'outside':
                file = retrieve_position(client_id['client_id'])
                await update.message.reply_document(document=file, caption='here the outside position')


# Responses

def send(chat, msg):
    url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={chat}&text={msg}"
    print(requests.get(url).json())


def handle_setup(text: str, chat_id):
    processed: str = text.lower()
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    Client = Query()
    clients_table.update({'train': False}, (Client.chat_id == chat_id))
    results = clients_table.search(Client.chat_id == chat_id)

    if not results[0]['geofence']:
        clients_table.update({'geofence': int(processed)}, (Client.chat_id == chat_id))
        db.close()
        return 'Now insert how frequently you want to update the data of the inside position. Insert only numbers'
    if not results[0]['count_max']:
        clients_table.update({'count_max': int(processed)}, (Client.chat_id == chat_id))
        return 'Now move inside a room of the house and insert the name of it. Insert at least two rooms.'
    message = learn_inside_locations(processed, chat_id)
    db.close()
    return message


def handle_authentication(text: str, chat_id):
    process = authenticate(text, chat_id)
    if not process:
        return 'Failed! Restart the authentication process'
    else:

        db = TinyDB('mqtt_database.json')
        clients_table = db.table('clients')
        Client = Query()
        clients_table.update({'auth': False}, Client.chat_id == chat_id)
        db.close()
        return r'Correctly Authenticated. Use command /setup to initialize the device'


def handle_response(text: str) -> str:
    return 'I do not understand what you wrote'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    Client = Query()
    results = clients_table.search(Client.chat_id == update.effective_user.id)
    db.close()

    if len(results) == 0:
        auth = True
        setup = False

    else:
        results = results[0]
        auth = results['auth']
        setup = results['setup']

    text: str = update.message.text

    if auth is True:
        message = handle_authentication(text, chat_id=update.effective_user.id)
        await update.message.reply_text(message)

    elif setup is True:
        print('SETUP')
        message = handle_setup(text, chat_id=update.effective_user.id)
        await update.message.reply_text(message)

    else:
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
    app.add_handler(CommandHandler('authenticate', authenticate_command))
    app.add_handler(CommandHandler('setup', setup_command))
    app.add_handler(CommandHandler('position', position_command))
    app.add_handler(CommandHandler('delete', delete_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)
    print('Polling...')
    app.run_polling(poll_interval=3)
