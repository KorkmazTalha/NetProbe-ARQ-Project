# utils/logger.py
import csv
import os
import time

from config import LOG_FILE_NAME 

class NetworkLogger:
    def __init__(self, filename=None):
        # Eğer dışarıdan isim verilmediyse config'deki dinamik ismi al diyoruz
        if filename is None:
            filename = LOG_FILE_NAME
            
        self.log_dir = "../analysis/logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        self.filepath = os.path.join(self.log_dir, filename)
        self.headers = [
            "Timestamp", "Event_Type", "Seq_No", "Packet_Size_Byte", 
            "Retransmit_Count", "Is_Success"
        ]
        
        # Dosyayı oluşturup başlıkları (headers) yazıyoruz
        with open(self.filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)

    def log_event(self, event_type, seq_no, packet_size=0, retransmit_count=0, is_success=True):
        """
        Ağ olaylarını CSV dosyasına kaydeder.
        event_type: 'SEND', 'ACK_RCVD', 'TIMEOUT', 'RETRANSMIT', 'SUCCESS', 'FAILED'
        """
        current_time = time.time()
        with open(self.filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                current_time, event_type, seq_no, packet_size, 
                retransmit_count, 1 if is_success else 0
            ])