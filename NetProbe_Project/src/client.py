# src/client.py
import socket
import os
import time
import sys

# utils klasörünü Python path'ine ekliyoruz ki logger'ı görebilsin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import NetworkLogger

from config import SERVER_IP, SERVER_PORT, DEFAULT_PACKET_SIZE, DEFAULT_TIMEOUT, MAX_RETRANSMISSIONS, INPUT_FILE_PATH
from protocol import create_packet, parse_packet

def run_client():
    if not os.path.exists(INPUT_FILE_PATH):
        print(f"[HATA] Gönderilecek dosya bulunamadı: {INPUT_FILE_PATH}")
        return

    # --- LOGGER BAŞLATMA ---
    # Her çalıştırmada temiz bir log dosyası açar
    logger = NetworkLogger()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(DEFAULT_TIMEOUT)
    server_address = (SERVER_IP, SERVER_PORT)
    
    with open(INPUT_FILE_PATH, "rb") as f:
        file_data = f.read()
    
    chunks = [file_data[i:i + DEFAULT_PACKET_SIZE] for i in range(0, len(file_data), DEFAULT_PACKET_SIZE)]
    total_packets = len(chunks)
    
    print(f"[İSTEMCİ] Dosya okundu. Toplam {total_packets} paket gönderilecek.")
    print("-" * 50)
    
    seq_no = 1
    start_time = time.time()
    
    def send_packet_reliably(p_type, s_no, payload_data):
        """Uygulama katmanında Stop-and-Wait ARQ protokol motoru.
        Paketin güvenilir şekilde iletilmesini, zaman aşımlarının yakalanmasını
        ve olayların anlık olarak loglanmasını yönetir."""
        retransmit_count = 0
        packet = create_packet(p_type, s_no, payload_data)
        p_size = len(packet)
        
        while retransmit_count <= MAX_RETRANSMISSIONS:
            try:
                # Olayı Logla: İlk gönderim veya Yeniden iletim ayrımı
                if retransmit_count == 0:
                    logger.log_event("SEND", s_no, packet_size=p_size)
                else:
                    logger.log_event("RETRANSMIT", s_no, packet_size=p_size, retransmit_count=retransmit_count)

                # Paketin UDP soketi üzerinden gönderilmesi
                client_socket.sendto(packet, server_address)
                
                # ACK paketinin beklenmesi
                ack_bytes, _ = client_socket.recvfrom(1024)
                ack_type, ack_no, _, _ = parse_packet(ack_bytes)
                
                # Alınan paketin tip ve sıra numarası doğrulaması
                if ack_type == 'A' and ack_no == s_no:
                    # Olayı Logla: Başarılı ACK Doğrulaması
                    logger.log_event("ACK_RCVD", s_no, retransmit_count=retransmit_count)
                    return True
                    
            except socket.timeout:
                # Zaman aşımı durumunda retransmit sayacı artırılır ve döngü devam eder
                retransmit_count += 1
                # Olayı Logla: Timeout Oluştu
                logger.log_event("TIMEOUT", s_no, retransmit_count=retransmit_count)
                
                if retransmit_count > MAX_RETRANSMISSIONS:
                    logger.log_event("FAILED", s_no, is_success=False)
                    print(f"[KRİTİK HATA] Paket {s_no} için {MAX_RETRANSMISSIONS} deneme başarısız!")
                    return False
                print(f"[TIMEOUT] Paket {s_no} için ACK gelmedi. Yeniden gönderiliyor... ({retransmit_count}/{MAX_RETRANSMISSIONS})")
        return False

    # ADIM A: START
    if not send_packet_reliably('S', seq_no, b"START_STREAM"): return
    seq_no += 1
    
    # ADIM B: DATA
    for i, chunk in enumerate(chunks):
        if not send_packet_reliably('D', seq_no, chunk): return
        seq_no += 1
        
    # ADIM C: END
    if not send_packet_reliably('E', seq_no, b"END_STREAM"): return

    end_time = time.time()
    total_duration = end_time - start_time
    
    # Genel Başarı Logu
    logger.log_event("SUCCESS", seq_no, packet_size=os.path.getsize(INPUT_FILE_PATH))
    
    print("-" * 50)
    print(f"[BAŞARI] Dosya aktarıldı ve tüm ağ hareketleri loglandı!")

if __name__ == "__main__":
    run_client()