from cryptography.fernet import Fernet
def get_key():
    key_path = 'secret.key'
    try:
        with open(key_path, 'rb') as key_file:
            key = key_file.read()
    except FileNotFoundError:
        # If the file does not exist, create it
        key = Fernet.generate_key()
        with open(key_path, 'wb') as key_file:
            key_file.write(key)
    return key


def encrypt_password(password, key):
    f = Fernet(key)
    return f.encrypt(password.encode())

def decrypt_password(encrypted_password, key):
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_password).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

