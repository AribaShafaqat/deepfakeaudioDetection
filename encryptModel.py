from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open("secret.key", "wb") as key_file:
    key_file.write(key)

with open("models/deep_sonar_model2.pth", "rb") as f:
    model_data = f.read()

# Encrypt
fernet = Fernet(key)
encrypted_data = fernet.encrypt(model_data)

# Save encrypted file
with open("deepsonarmodel2_encrypted.pth", "wb") as f:
    f.write(encrypted_data)
