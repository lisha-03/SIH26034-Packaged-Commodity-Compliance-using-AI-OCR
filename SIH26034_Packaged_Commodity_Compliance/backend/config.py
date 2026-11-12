import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = os.environ.get("SIH_SECRET_KEY", "sih26034-dev-secret-change-in-production")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
IMAGES_DIR = os.path.join(UPLOAD_DIR, "images")
REPORTS_DIR = os.path.join(UPLOAD_DIR, "reports")
DEMO_IMAGES_DIR = os.path.join(BASE_DIR, "demo_data", "images")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE_MB = 8

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
