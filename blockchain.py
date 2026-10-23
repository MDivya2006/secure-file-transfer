import json
import time
from pathlib import Path
from web3 import Web3

# File paths
BASE_DIR = Path(__file__).resolve().parent
ADDRESS_FILE = BASE_DIR / "contract_address.txt"
ABI_FILE = BASE_DIR / "FileRegistry_abi.json"

# Ganache connection
GANACHE_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL, request_kwargs={"timeout": 10}))

contract = None
account = None


def connect_blockchain():
    global contract, account

    if not w3.is_connected():
        raise ConnectionError(
            "Ganache connect aagala. Ganache open panni check pannu."
        )

    print("Blockchain connected successfully!")

    if not ADDRESS_FILE.exists():
        raise FileNotFoundError("contract_address.txt file missing.")

    if not ABI_FILE.exists():
        raise FileNotFoundError("FileRegistry_abi.json file missing.")

    address = ADDRESS_FILE.read_text(encoding="utf-8").strip()

    with open(ABI_FILE, "r", encoding="utf-8") as file:
        abi_data = json.load(file)

    # ABI file list-ah irundhaalum dictionary-ah irundhaalum support pannum
    abi = abi_data if isinstance(abi_data, list) else abi_data["abi"]

    code = w3.eth.get_code(address)

    if len(code) == 0:
        raise RuntimeError(
            "Contract found aagala. Ganache-la contract deploy pannu."
        )

    contract = w3.eth.contract(address=address, abi=abi)
    account = w3.eth.accounts[0]

    print("Smart contract loaded successfully!")
    print("Contract address:", address)
    print("Contract code length:", len(code))


def store_file_hash(file_name, file_hash, owner_name="Divya"):
    """Register file details in the blockchain."""

    if contract is None or account is None:
        connect_blockchain()

    timestamp = int(time.time())

    tx_hash = contract.functions.registerFile(
        str(file_name),
        str(file_hash),
        str(owner_name),
        account,
        timestamp
    ).transact({
        "from": account,
        "gas": 500000
    })

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status != 1:
        raise RuntimeError("Blockchain file registration failed.")

    return {
        "success": True,
        "transaction_hash": receipt.transactionHash.hex(),
        "block_number": receipt.blockNumber,
        "file_hash": str(file_hash)
    }


def get_file_record(file_hash):
    """Retrieve a registered file record from the blockchain."""

    if contract is None:
        connect_blockchain()

    record = contract.functions.getFile(str(file_hash)).call()

    if not record or not record[1]:
        return None

    return {
        "file_name": record[0],
        "file_hash": record[1],
        "owner_name": record[2],
        "owner_address": record[3],
        "timestamp": record[4]
    }


def register_file(file_name, file_hash, owner_name="Divya"):
    """Compatibility function for existing code."""
    return store_file_hash(file_name, file_hash, owner_name)


def get_file(file_hash):
    """Compatibility function for existing code."""
    return get_file_record(file_hash)


def verify_file(file_hash):
    """Check whether the file hash exists on the blockchain."""

    record = get_file_record(file_hash)

    if record is None:
        return False

    return record["file_hash"] == str(file_hash)


# Connect when this module is imported by app.py
connect_blockchain()


if __name__ == "__main__":
    print("\nBlockchain test")
    print("Ganache connected:", w3.is_connected())
    print("Available accounts:", len(w3.eth.accounts))
    print("Contract ready!")