import hashlib
from blockchain import contract

# File ID will be entered here after upload
file_id = input("Enter File ID: ").strip()

try:
    # Get file information from blockchain
    file_data = contract.functions.getFile(file_id).call()

    file_name = file_data[0]
    blockchain_hash = file_data[1]
    receiver = file_data[3]
    expiry = file_data[4]

    print("\n📄 File Name :", file_name)
    print("🔑 Blockchain Hash :", blockchain_hash)
    print("👤 Receiver :", receiver)
    print("⏰ Expiry :", expiry)

    # Check whether file exists
    original_file = "../uploads/" + file_name

    try:
        with open(original_file, "rb") as f:

            sha256_hash = hashlib.sha256()

            for chunk in iter(
                lambda: f.read(4096),
                b""
            ):
                sha256_hash.update(chunk)

        current_hash = sha256_hash.hexdigest()

        print("🔑 Current File Hash :", current_hash)

        # Verify integrity
        if blockchain_hash == current_hash:

            print("\n✅ FILE INTEGRITY VERIFIED!")
            print("🛡️ File is authentic and unchanged.")

        else:

            print("\n🚨 TAMPERING DETECTED!")
            print("❌ File hash does not match blockchain.")

    except FileNotFoundError:

        print("\n❌ File not found in uploads folder.")

except Exception as e:

    print("\n❌ File verification failed.")
    print("Error:", e)