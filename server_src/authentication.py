from tinydb import TinyDB, Query
import hashlib
from cryptography.fernet import Fernet

secret_key =  b'6SGa2U3RtT_w4JvHYibd9LWF6CLE1K46Ef65XMen72c=' #Fernet.generate_key()
#print("SECRET: ", secret_key.decode())


def encrypt(input_string, key = secret_key):
    sha256 = hashlib.sha256()
    input_string = input_string + secret_key
    sha256.update(input_string)
    return sha256.hexdigest()

def authenticate(token, chat_id):
    db = TinyDB('mqtt_database.json')
    clients_table = db.table('clients')
    all_entries = clients_table.all()
    client_ids = [entry['client_id'] for entry in all_entries]
    token = str(token)
    encrypted_first_10_chars = []
    for client_id in client_ids:
        encrypted = encrypt(client_id.encode())
        encrypted_first_10_chars.append(encrypted[:10])

    idx = -1
    for i, encrypted in enumerate(encrypted_first_10_chars):
        encrypted = str(encrypted)
        encrypted = encrypted.replace("'", "")
        print('encryped', encrypted, 'token', token, i)
        if encrypted == token:
            idx = i

    if idx == -1:
        return False
    client_id = client_ids[idx]
    Client = Query()
    clients_table.update({'chat_id': chat_id}, (Client.client_id == client_id))
    db.close()
    return True
