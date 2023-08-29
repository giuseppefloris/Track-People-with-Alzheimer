from tinydb import TinyDB, Query
from cryptography.fernet import Fernet

secret_key =  b'6SGa2U3RtT_w4JvHYibd9LWF6CLE1K46Ef65XMen72c=' #Fernet.generate_key()
#print("SECRET: ", secret_key.decode())
cipher = Fernet(secret_key)


def authenticate(token, chat_id):
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    all_entries = clients_table.all()
    client_ids = [entry['client_id'] for entry in all_entries]
    token = str(token)
    encrypted_first_10_chars = []
    for client_id in client_ids:
        encrypted = cipher.encrypt(client_id.encode())
        encrypted_first_10_chars.append(encrypted[:10])

    idx = -1

    for i, encrypted in enumerate(encrypted_first_10_chars):
        encrypted = str(encrypted)
        encrypted = encrypted.replace('b', '')
        encrypted = encrypted.replace("'", "")

        if encrypted == token:
            idx = i
    if idx == -1:
        return None # da mandare messaggio ogni volta che auth andata male
    client_id = client_ids[i]
    Client = Query()
    clients_table.update({'chat_id': chat_id},
                         (Client.client_id == client_id))
    db.close()
    return True
