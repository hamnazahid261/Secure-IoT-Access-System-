from cryptography.fernet import Fernet

# 🔑 KEY LOAD
def load_key():
    return open("secret.key", "rb").read()

# 🔓 DECRYPT DATA
def decrypt_data(data: bytes):
    key = load_key()
    f = Fernet(key)
    return f.decrypt(data)