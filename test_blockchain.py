from blockchain import w3, contract

account = w3.eth.accounts[0]

tx = contract.functions.registerFile(
    "test123",
    "test.txt",
    "abc123hash",
    w3.eth.accounts[1],
    9999999999
).transact({
    "from": account
})

receipt = w3.eth.wait_for_transaction_receipt(tx)

print("✅ File registered on blockchain!")
print("Transaction Hash:", receipt.transactionHash.hex())