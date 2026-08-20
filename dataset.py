from encryption_utils import decrypt_data
import json

DATA_FILE = "face_data.enc"

def load_dataset():
    with open(DATA_FILE, "rb") as f:
        encrypted = f.read()

    decrypted = decrypt_data(encrypted.decode())
    return json.loads(decrypted)