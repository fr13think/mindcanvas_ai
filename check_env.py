import os
from dotenv import load_dotenv

load_dotenv() # Memuat variabel dari file .env

token = os.environ.get("HUGGINGFACE_TOKEN")

print("--- Memeriksa Environment Variable ---")
if token:
    # Hanya cetak sebagian kecil dari token untuk keamanan
    print(f"Token ditemukan: {token[:4]}...{token[-4:]}")
else:
    print("Token TIDAK ditemukan.")
print("------------------------------------")