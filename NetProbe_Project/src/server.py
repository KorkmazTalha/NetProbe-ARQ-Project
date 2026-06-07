# src/server.py
import socket
import os
import sys

# utils'e erişim için path ekliyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.simulator import should_drop_packet, simulate_network_delay

from config import SERVER_IP, SERVER_PORT, OUTPUT_FILE_PATH, LOSS_RATE, NETWORK_DELAY
from protocol import parse_packet, create_packet

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    
    print(f"[SUNUCU] Dinlemede... {SERVER_IP}:{SERVER_PORT}")
    print(f"[SİMÜLASYON] Aktif Ayarlar -> Kayıp Oranı: %{LOSS_RATE*100}, Gecikme: {NETWORK_DELAY}sn")
    print("-" * 50)
    
    received_chunks = {}
    expected_seq = 1
    transfer_active = False

    while True:
        # 1. Paketi fiziksel olarak hattan alıyoruz
        packet_bytes, client_address = server_socket.recvfrom(2048)
        
        # --- AĞ SİMÜLASYONU BURADA DEVREYE GİRİYOR ---
        # Önce paketin düşüp düşmeyeceğine karar verelim
        if should_drop_packet(LOSS_RATE):
            # Paketi parse bile etmeden hafızadan siliyoruz, istemciye hiç ses etmiyoruz (Drop)
            try:
                _, s_no, _, _ = parse_packet(packet_bytes)
                print(f"[SİMÜLASYON] X Paket {s_no} YAPAY OLARAK DÜŞÜRÜLDÜ (LOSS) X")
            except:
                print("[SİMÜLASYON] X Bozuk bir paket yapay olarak düşürüldü X")
            continue # Döngünün başına dön, sanki paket hiç gelmemiş gibi davran!

        # Paket düşmediyse gecikme (ping) simülasyonunu uyguluyoruz
        simulate_network_delay(NETWORK_DELAY)
        # ---------------------------------------------

        try:
            p_type, seq_no, checksum, payload = parse_packet(packet_bytes)
        except ValueError as e:
            print(f"[SUNUCU HATA] Paket ayrıştırılamadı: {e}")
            continue

        if p_type == 'S':  # START Paketi
            print(f"[SUNUCU] Baslangic paketi alindi (Seq: {seq_no}). Transfer basliyor...")
            transfer_active = True
            received_chunks.clear()
            expected_seq = seq_no
            
            ack_packet = create_packet('A', seq_no, b"ACK_START")
            server_socket.sendto(ack_packet, client_address)
            expected_seq += 1
            
        elif p_type == 'D' and transfer_active:  # DATA Paketi
            if seq_no == expected_seq:
                received_chunks[seq_no] = payload
                print(f"[SUNUCU] Veri paketi alindi: Seq {seq_no} | Boyut: {len(payload)} byte")
                
                ack_packet = create_packet('A', seq_no, b"ACK_DATA")
                server_socket.sendto(ack_packet, client_address)
                expected_seq += 1
            elif seq_no < expected_seq:
                print(f"[SUNUCU UYARI] Eski/Duplike paket geldi: Seq {seq_no}. Tekrar ACK gönderiliyor.")
                ack_packet = create_packet('A', seq_no, b"ACK_DATA")
                server_socket.sendto(ack_packet, client_address)
                
        elif p_type == 'E' and transfer_active:  # END Paketi
            if seq_no == expected_seq:
                print(f"[SUNUCU] Bitis paketi alindi (Seq: {seq_no}). Dosya yaziliyor...")
                
                ack_packet = create_packet('A', seq_no, b"ACK_END")
                server_socket.sendto(ack_packet, client_address)
                
                output_dir = os.path.dirname(OUTPUT_FILE_PATH)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                with open(OUTPUT_FILE_PATH, "wb") as f:
                    for s in sorted(received_chunks.keys()):
                        f.write(received_chunks[s])
                        
                print(f"[BAŞARI] Dosya kaydedildi: {OUTPUT_FILE_PATH}")
                print("-" * 50)
                transfer_active = False

if __name__ == "__main__":
    run_server()