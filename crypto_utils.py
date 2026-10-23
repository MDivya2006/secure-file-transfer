from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


def save_key(key, key_file="../database/secret.key"):
    with open(key_file, "wb") as file:
        file.write(key)


def load_key(key_file="../database/secret.key"):
    with open(key_file, "rb") as file:
        return file.read()


def encrypt_file(input_file, output_file, key):
    cipher = Fernet(key)

    with open(input_file, "rb") as file:
        data = file.read()

    encrypted_data = cipher.encrypt(data)

    with open(output_file, "wb") as file:
        file.write(encrypted_data)


def decrypt_file(input_file, output_file, key):
    cipher = Fernet(key)

    with open(input_file, "rb") as file:
        encrypted_data = file.read()

    data = cipher.decrypt(encrypted_data)

    with open(output_file, "wb") as file:
        file.write(data)