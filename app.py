import hashlib
import logging
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet

from blockchain import store_file_hash, get_file_record


# Project paths
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

UPLOAD_DIR = BASE_DIR / "uploads"
ENCRYPTED_DIR = BASE_DIR / "encrypted_files"
KEY_DIR = BASE_DIR / "keys"

for folder in (UPLOAD_DIR, ENCRYPTED_DIR, KEY_DIR):
    folder.mkdir(parents=True, exist_ok=True)


app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

logging.basicConfig(level=logging.INFO)


def calculate_hash(file_path):
    """Return the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def read_uploaded_file():
    uploaded = request.files.get("file")

    if uploaded is None or not uploaded.filename:
        return None, None

    filename = secure_filename(uploaded.filename)

    if not filename:
        return None, None

    return uploaded, filename


@app.route("/", methods=["GET"])
def home():
    index_file = FRONTEND_DIR / "index.html"

    if not index_file.is_file():
        return jsonify({
            "success": False,
            "message": "frontend/index.html was not found."
        }), 404

    return send_from_directory(str(FRONTEND_DIR), "index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded, filename = read_uploaded_file()

    if uploaded is None:
        return jsonify({
            "success": False,
            "message": "Please select a file."
        }), 400

    original_path = UPLOAD_DIR / filename
    encrypted_path = ENCRYPTED_DIR / (filename + ".encrypted")
    key_path = KEY_DIR / (filename + ".key")

    try:
        uploaded.save(str(original_path))
        original_hash = calculate_hash(original_path)

        key = Fernet.generate_key()
        encrypted_data = Fernet(key).encrypt(original_path.read_bytes())

        encrypted_path.write_bytes(encrypted_data)
        key_path.write_bytes(key)

        # Store the hash in the blockchain.
        # Do not report success if registration fails.
        tx_result = store_file_hash(
            filename,
            original_hash,
            "Divya"
        )

        return jsonify({
            "success": True,
            "message": "File uploaded, encrypted and registered on blockchain.",
            "filename": filename,
            "sha256": original_hash,
            "blockchain_result": str(tx_result)
        }), 200

    except Exception:
        app.logger.exception("Upload failed")

        return jsonify({
            "success": False,
            "message": "Upload or blockchain registration failed. Check the VS Code terminal."
        }), 500


@app.route("/verify", methods=["POST"])
def verify_file():
    uploaded, filename = read_uploaded_file()

    if uploaded is None:
        return jsonify({
            "success": False,
            "verified": False,
            "message": "Please select a file to verify."
        }), 400

    original_path = UPLOAD_DIR / filename
    temp_path = UPLOAD_DIR / ("verify_" + filename)

    if not original_path.is_file():
        return jsonify({
            "success": False,
            "verified": False,
            "message": "Original uploaded file not found. Upload it first."
        }), 404

    try:
        # Hash the actual newly selected file first.
        uploaded.save(str(temp_path))
        current_hash = calculate_hash(temp_path)

        # Hash the saved original upload independently.
        original_hash = calculate_hash(original_path)

        file_matches = current_hash == original_hash

        # Only accept the blockchain record if it exists and its
        # stored file hash matches the saved original hash.
        record = get_file_record(original_hash)
        blockchain_hash = ""

        if isinstance(record, dict):
            blockchain_hash = str(
                record.get("file_hash", record.get("fileHash", ""))
            )
        elif isinstance(record, (list, tuple)) and len(record) > 1:
            blockchain_hash = str(record[1] or "")

        blockchain_matches = (
            bool(blockchain_hash)
            and blockchain_hash.lower() == original_hash.lower()
        )

        verified = file_matches and blockchain_matches

        if verified:
            message = "Verification Successful: file and blockchain hashes match."
        elif not file_matches:
            message = "Verification Failed: selected file content has changed."
        elif not blockchain_matches:
            message = "Verification Failed: matching blockchain record not found."
        else:
            message = "Verification Failed."

        return jsonify({
            "success": True,
            "verified": verified,
            "message": message,
            "filename": filename,
            "original_hash": original_hash,
            "current_hash": current_hash,
            "blockchain_hash": blockchain_hash,
            "file_matches": file_matches,
            "blockchain_matches": blockchain_matches
        }), 200

    except Exception:
        app.logger.exception("Verification error")

        return jsonify({
            "success": False,
            "verified": False,
            "message": "Verification error. Check the VS Code terminal."
        }), 500

    finally:
        if temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    # Local testing only; keep Ganache running too.
    app.run(host="127.0.0.1", port=5000, debug=False)