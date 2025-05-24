



import os
import getpass
import subprocess
import hashlib
import logging

# Folder paths
FOLDERS = {
    "training_real": r"E:\IS\data\for-norm\training\real",
    "training_fake": r"E:\IS\data\for-norm\training\fake",
    "testing_real": r"E:\IS\data\for-norm\testing\real",
    "testing_fake": r"E:\IS\data\for-norm\testing\fake",
    "validation_real": r"E:\IS\data\for-norm\validation\real",
    "validation_fake": r"E:\IS\data\for-norm\validation\fake"
}

# Stored folder-level SHA256 hashes
EXPECTED_HASHES = {
    "training_real": "ba78d4f5abd3b32564530e56e2dee9011eedb831ee4883ba19116d76a844ac58",
    "training_fake": "f5cfcb1ba23dfd3bce222cc72f254f23b3484e68334918b81cba65ca259f1475",
    "testing_real": "034d36121b48e064a2345973850de7f919f7a8338e7180f90917e9c2eb1ab727",
    "testing_fake": "d539862d054071367fba392e7ab22af708972cfba359785890d9d9b92cc07fe8",
    "validation_real": "f4ca840e26baa6aef66ff8755a0540021bdb91eb49fddf7a58adbd124274091d",
    "validation_fake": "049ab3dfe647f5654fcb8073fab636ca66c37860312d7b8dd3a29be55c37aa8c"
}

# Allow both ariba and admin to run
AUTHORIZED_USERS = ['ariba', 'admin']

def verify_user():
    user = getpass.getuser()
    if user.lower() not in AUTHORIZED_USERS:
        raise PermissionError(f"Access denied for user: {user}")
    print(f"User verified: {user}")

def hash_folder(folder_path):
    sha = hashlib.sha256()
    for root, _, files in os.walk(folder_path):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                sha.update(f.read())
    return sha.hexdigest()

def verify_dataset():
    for label, folder in FOLDERS.items():
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Folder not found: {folder}")
        actual_hash = hash_folder(folder)
        if actual_hash != EXPECTED_HASHES[label]:
            raise ValueError(f" Folder tampering detected in: {label}")
        print(f"Folder verified: {label}")

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/training_access.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def log_access():
    user = getpass.getuser()
    logging.info(f"{user} started training.")

def run_training():
    print("Starting training...")
    subprocess.run(["python", "train.py"], check=True)
    print(" Training finished.")

if __name__ == "__main__":
    setup_logger()
    try:
        verify_user()
        verify_dataset()
        log_access()
        run_training()
    except Exception as e:
        logging.error(str(e))
        print(f" Security check failed: {e}")

    # 👉 Uncomment the block below only if you need to regenerate hashes
    # for label, folder in FOLDERS.items():
    #     print(f"{label}: {hash_folder(folder)}")
