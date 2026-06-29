from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "database" / "track_info.db"
CERT_PATH = BASE_DIR / "certificates" / "cert.pem"
KEY_PATH = BASE_DIR / "certificates" / "key.pem"

JWT_SECRET = "yimYpaFYbk5XOIep7XHtswBE1L1Pe19g6ZJAgLHHVXF7iP0RTXMN8Td4EdKGA1ewEY14efnQ3"

LOGIN_PORT = 4443
PRODUCTS_PORT = 4444