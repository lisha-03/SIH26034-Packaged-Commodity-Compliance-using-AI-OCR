import os
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_size(file_storage) -> bool:
    file_storage.seek(0, os.SEEK_END)
    size_mb = file_storage.tell() / (1024 * 1024)
    file_storage.seek(0)
    return size_mb <= MAX_FILE_SIZE_MB
