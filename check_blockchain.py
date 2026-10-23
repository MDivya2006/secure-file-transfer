from blockchain import contract

file_id = "test.txt"

file_data = contract.functions.getFile(file_id).call()

print("📄 File Name :", file_data[0])
print("🔑 File Hash :", file_data[1])
print("👤 Sender    :", file_data[2])
print("👤 Receiver  :", file_data[3])
print("⏰ Expiry    :", file_data[4])