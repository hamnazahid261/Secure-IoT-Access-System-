from cryptography.fernet import Fernet

KEY_FILE = "secret.key"


def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)


def load_key():
    return open(KEY_FILE, "rb").read()


def encrypt_data(text):
    f = Fernet(load_key())
    return f.encrypt(text.encode())


def decrypt_data(text):
    f = Fernet(load_key())
    return f.decrypt(text).decode()