import hashlib
from crypto_utils import load_key, decrypt_file

key = load_key()

decrypt_file(
    "../encrypted/test.txt.encrypted",
    "../uploads/decrypted_test.txt",
    key
)

def get_hash(filename):
    sha256 = hashlib.sha256()

    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


original_hash = get_hash("../uploads/test.txt")
decrypted_hash = get_hash("../uploads/decrypted_test.txt")

print("Original Hash :", original_hash)
print("Decrypted Hash:", decrypted_hash)

if original_hash == decrypted_hash:
    print("✅ FILE INTEGRITY VERIFIED!")
else:
    print("❌ FILE TAMPERED!")