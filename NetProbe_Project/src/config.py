# src/config.py
import os

# --- DİNAMİK ORTAM DEĞİŞKENİ KONTROLÜ (DENEY MOTORU İÇİN) ---
def get_env_or_default(key, default_value, cast_type=float):
    if key in os.environ:
        return cast_type(os.environ[key])
    return default_value

# Ağ Bağlantı Ayarları
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

# Protokol Ayarları (Eğer deney motoru çalışıyorsa onun değerlerini çeker, yoksa sağdaki defaultları kullanır)
DEFAULT_PACKET_SIZE = get_env_or_default("OVERRIDE_PACKET_SIZE", 1024, int)
MAX_RETRANSMISSIONS = 5
LOSS_RATE = get_env_or_default("OVERRIDE_LOSS_RATE", 0.1)
NETWORK_DELAY = get_env_or_default("OVERRIDE_NETWORK_DELAY", 0.01)
DEFAULT_TIMEOUT = 0.5

# Dinamik Log Dosyası Adı
LOG_FILE_NAME = os.environ.get("OVERRIDE_LOG_FILE", "transfer_log.csv")

# Dosya Yolları
INPUT_FILE_PATH = "../data/input_file.txt"
OUTPUT_FILE_PATH = "../data/received_file.txt"