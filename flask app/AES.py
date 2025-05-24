import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Folder to store the AES key
KEYS_FOLDER = "KEYS"
KEY_FILE_PATH = os.path.join(KEYS_FOLDER, "aes_key.key")

os.makedirs(KEYS_FOLDER, exist_ok=True)

# AES-256 key generation
def generate_aes_key():
    return get_random_bytes(32)  

def store_aes_key(key, path):
    try:
        with open(path, 'wb') as f:
            f.write(key)
            print(f"AES key saved to {path}")
    except Exception as e:
        print(f"Error saving AES key: {e}")

def load_aes_key(path):
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return f.read()
        else:
            print(f"Key file not found: {path}")
            return None
    except Exception as e:
        print(f"Error loading AES key: {e}")
        return None

# Encrypt binary data
def aes_encrypt(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return iv, encrypted  # Return raw bytes

# Decrypt binary data
def aes_decrypt(encrypted_data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return decrypted

# Optional: Encrypt a file directly
def encrypt_file(input_path, output_path, key):
    with open(input_path, 'rb') as f:
        data = f.read()
    iv, encrypted = aes_encrypt(data, key)
    with open(output_path, 'wb') as f:
        f.write(iv + encrypted)  # Save iv + encrypted together

# Optional: Decrypt a file directly
def decrypt_file(input_path, output_path, key):
    with open(input_path, 'rb') as f:
        content = f.read()
    iv = content[:16]
    encrypted = content[16:]
    decrypted = aes_decrypt(encrypted, key, iv)
    with open(output_path, 'wb') as f:
        f.write(decrypted)



# Directly store the key if needed:
aes_key = generate_aes_key()  
store_aes_key(aes_key, KEY_FILE_PATH)  # Store the key in the KEYS folder

# Load the key whenever you need it
loaded_key = load_aes_key(KEY_FILE_PATH)