from cryptography.fernet import Fernet

# 🔑 KEY GENERATE (ONLY ONCE)
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as f:
        f.write(key)

# 🔑 KEY LOAD
def load_key():
    return open("secret.key", "rb").read()

# 🔒 ENCRYPT DATA
def encrypt_data(data: bytes):
    key = load_key()
    f = Fernet(key)
    return f.encrypt(data)