import json
import os

from web3 import Web3
from solcx import compile_source, install_solc, set_solc_version

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONTRACT_PATHS = [
    os.path.join(BASE_DIR, "..", "contracts", "fileregistry.sol"),
    os.path.join(BASE_DIR, "..", "contracts", "FileRegistry.sol"),
    os.path.join(BASE_DIR, "blockend", "fileregistry.sol"),
]

CONTRACT_PATH = next(
    (os.path.abspath(path) for path in CONTRACT_PATHS
     if os.path.isfile(path)),
    None
)

if CONTRACT_PATH is None:
    raise FileNotFoundError(
        "fileregistry.sol not found. Check the contracts folder."
    )

# Connect to Ganache
GANACHE_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    raise ConnectionError(
        "Ganache connection failed. Open Ganache and try again."
    )

account = w3.eth.accounts[0]

print("Connected to Ganache!")
print("Account:", account)

# Use Solidity compiler 0.8.19
SOLC_VERSION = "0.8.19"
install_solc(SOLC_VERSION)
set_solc_version(SOLC_VERSION)

# Read contract
with open(CONTRACT_PATH, "r", encoding="utf-8") as file:
    source = file.read()

# Compile contract for an older, compatible EVM target
compiled = compile_source(
    source,
    output_values=["abi", "bin"],
    solc_version=SOLC_VERSION,
    evm_version="london",
)

contract_key = next(
    (key for key in compiled if key.endswith(":FileRegistry")),
    None,
)

if contract_key is None:
    raise ValueError(
        "FileRegistry contract not found. Check the contract name."
    )

contract_interface = compiled[contract_key]

if not contract_interface["bin"]:
    raise RuntimeError("Contract bytecode is empty.")

# Prepare contract deployment
FileRegistry = w3.eth.contract(
    abi=contract_interface["abi"],
    bytecode=contract_interface["bin"],
)

print("Deploying FileRegistry contract...")

tx_hash = FileRegistry.constructor().transact({
    "from": account,
    "gas": 3_000_000,
    "gasPrice": w3.eth.gas_price,
})

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

if receipt.status != 1 or not receipt.contractAddress:
    raise RuntimeError("Contract deployment failed.")

contract_address = Web3.to_checksum_address(
    receipt.contractAddress
)

# Verify deployed bytecode
deployed_code = w3.eth.get_code(contract_address)

if len(deployed_code) == 0:
    raise RuntimeError(
        "Deployment returned an address, but no contract code exists."
    )

# Save ABI
abi_path = os.path.join(BASE_DIR, "FileRegistry_abi.json")

with open(abi_path, "w", encoding="utf-8") as file:
    json.dump(contract_interface["abi"], file, indent=2)

# Save contract address
address_path = os.path.join(BASE_DIR, "contract_address.txt")

with open(address_path, "w", encoding="utf-8") as file:
    file.write(contract_address)

print("\nDEPLOYMENT SUCCESSFUL!")
print("Contract Address:", contract_address)
print("Transaction Hash:", receipt.transactionHash.hex())
print("Contract Code Length:", len(deployed_code))
print("ABI saved:", abi_path)
print("Address saved:", address_path)
print("FileRegistry is ready!")