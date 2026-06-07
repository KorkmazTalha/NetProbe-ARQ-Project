# src/experiment_runner.py
import subprocess
import time
import os
import csv
import sys

# Bu scriptin çalıştığı gerçek klasörü buluyoruz (src klasörü)
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
# Bir üst klasör projenin ana dizini (NetProbe_Project)
BASE_DIR = os.path.abspath(os.path.join(SRC_DIR, '..'))

# Doğru dosya yollarını mutlak (absolute) path olarak kilitliyoruz
SERVER_SCRIPT = os.path.join(SRC_DIR, "server.py")
CLIENT_SCRIPT = os.path.join(SRC_DIR, "client.py")
LOG_DIR = os.path.join(BASE_DIR, "analysis", "logs")

SCENARIOS = [
    # Senaryo 1: Temel Başarım (Farklı Paket Boyutları, %0 Kayıp)
    ("Senaryo1_Size512", 512, 0.0, 0.0),
    ("Senaryo1_Size1024", 1024, 0.0, 0.0),
    ("Senaryo1_Size2048", 2048, 0.0, 0.0),
    
    # Senaryo 2: Gecikmenin Etkisi (%0 Kayıp, Sabit Boyut)
    ("Senaryo2_Delay10ms", 1024, 0.0, 0.01),
    ("Senaryo2_Delay50ms", 1024, 0.0, 0.05),
    
    # Senaryo 3: Paket Kaybının Etkisi (Sabit Gecikme, Sabit Boyut)
    ("Senaryo3_Loss5", 1024, 0.05, 0.01),
    ("Senaryo3_Loss15", 1024, 0.15, 0.01),
]

def run_experiment(name, size, loss, delay):
    print(f"\n=========================================")
    print(f" DENEY BAŞLADI: {name}")
    print(f" Ayarlar -> Boyut: {size}B | Kayıp: %{loss*100} | Gecikme: {delay}sn")
    print(f"=========================================")

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    env = os.environ.copy()
    env["OVERRIDE_PACKET_SIZE"] = str(size)
    env["OVERRIDE_LOSS_RATE"] = str(loss)
    env["OVERRIDE_NETWORK_DELAY"] = str(delay)
    env["OVERRIDE_LOG_FILE"] = f"{name}_log.csv"

    # Sunucuyu mutlak yolla başlatıyoruz
    server_process = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Sunucunun tamamen açılması için kısa bir bekleme süresi
    time.sleep(0.6)

    # İstemciyi mutlak yolla başlatıyoruz
    start_time = time.time()
    client_process = subprocess.Popen(
        [sys.executable, CLIENT_SCRIPT],
        env=env
    )
    client_process.wait()  # İstemci bitene kadar kesin olarak bekle
    end_time = time.time()

    # İş bitince sunucuyu nazikçe kapat
    server_process.terminate()
    server_process.wait()

    duration = end_time - start_time
    print(f"[DENEY BİTTİ] Süre: {duration:.2f} saniye. Log kaydedildi: {name}_log.csv")
    return duration

def main():
    print("[OTOMASYON] Deney çalıştırma motoru başlatıldı.")
    results = []
    
    for sc in SCENARIOS:
        duration = run_experiment(sc[0], sc[1], sc[2], sc[3])
        results.append([sc[0], sc[1], sc[2], sc[3], duration])
        time.sleep(1.5)  # İşletim sisteminin UDP portunu temizlemesi için güvenli bekleme süresi
        
    summary_path = os.path.join(LOG_DIR, "experiment_summary.csv")
    with open(summary_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Senaryo", "Paket_Boyutu", "Kayip_Orani", "Gecikme", "Toplam_Sure_Sn"])
        writer.writerows(results)
        
    print("\n" + "#"*50)
    print(f"[TÜM DENEYLER TAMAMLANDI] Özet rapor şurada:\n{summary_path}")
    print("#"*50)

if __name__ == "__main__":
    main()