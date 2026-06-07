# analysis/plot_results.py
import os
import pandas as pd
import matplotlib.pyplot as plt

# Mevcut dosyanın konumuna göre yolları kilitliyoruz
ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(ANALYSIS_DIR, "logs")
SUMMARY_FILE = os.path.join(LOG_DIR, "experiment_summary.csv")

def generate_plots():
    if not os.path.exists(SUMMARY_FILE):
        print(f"[HATA] Özet rapor dosyası bulunamadı: {SUMMARY_FILE}")
        print("Lütfen önce deney motorunu (experiment_runner.py) çalıştırın.")
        return

    # Veriyi oku
    df = pd.read_csv(SUMMARY_FILE)
    print("[ANALİZ] Veriler başarıyla okundu. Grafik çizimlerine başlanıyor...")

    # Grafiklerin kaydedileceği klasör
    output_dir = os.path.join(ANALYSIS_DIR, "plots")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Grafik tarzını güzelleştirelim
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # -------------------------------------------------------------
    # GRAFİK 1: Paket Boyutunun Etkisi (Senaryo 1)
    # -------------------------------------------------------------
    df_s1 = df[df['Senaryo'].str.contains('Senaryo1')]
    plt.figure(figsize=(8, 5))
    bars = plt.bar(df_s1['Paket_Boyutu'].astype(str), df_s1['Toplam_Sure_Sn'], color='#2ca02c', edgecolor='black', width=0.5)
    plt.title('Paket Boyutunun Toplam Transfer Süresine Etkisi\n(%0 Kayıp, 0ms Gecikme)', fontsize=12, fontweight='bold')
    plt.xlabel('Paket Boyutu (Bayt)', fontsize=10)
    plt.ylabel('Toplam Süre (Saniye)', fontsize=10)
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.01, f"{yval:.2f}s", ha='center', va='bottom', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "grafik1_paket_boyutu.png"), dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # GRAFİK 2: Ağ Gecikmesinin Etkisi (Senaryo 2)
    # -------------------------------------------------------------
    df_s2 = df[df['Senaryo'].str.contains('Senaryo2') | (df['Senaryo'] == 'Senaryo1_Size1024')]
    df_s2 = df_s2.sort_values(by='Gecikme')
    
    plt.figure(figsize=(8, 5))
    plt.plot(df_s2['Gecikme'] * 1000, df_s2['Toplam_Sure_Sn'], marker='o', linewidth=2.5, color='#1f77b4', markersize=8)
    plt.title('Ağ Gecikmesinin (RTT) Toplam Transfer Süresine Etkisi\n(1024B Paket, %0 Kayıp)', fontsize=12, fontweight='bold')
    plt.xlabel('Yapay Gecikme (Milisaniye - ms)', fontsize=10)
    plt.ylabel('Toplam Süre (Saniye)', fontsize=10)
    
    for x, y in zip(df_s2['Gecikme'] * 1000, df_s2['Toplam_Sure_Sn']):
        plt.text(x, y + 1, f"{y:.2f}s", ha='center', va='bottom', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "grafik2_ag_gecikme.png"), dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # GRAFİK 3: Paket Kaybının Etkisi (Senaryo 3)
    # -------------------------------------------------------------
    df_s3 = df[df['Senaryo'].str.contains('Senaryo3') | (df['Senaryo'] == 'Senaryo2_Delay10ms')]
    df_s3 = df_s3.sort_values(by='Kayip_Orani')

    plt.figure(figsize=(8, 5))
    bars3 = plt.bar((df_s3['Kayip_Orani'] * 100).astype(str) + "%", df_s3['Toplam_Sure_Sn'], color='#d62728', edgecolor='black', width=0.5)
    plt.title('Paket Kayıp Oranının Toplam Transfer Süresine Etkisi\n(1024B Paket, 10ms Gecikme)', fontsize=12, fontweight='bold')
    plt.xlabel('Paket Kayıp Oranı (%)', fontsize=10)
    plt.ylabel('Toplam Süre (Saniye)', fontsize=10)
    
    for bar in bars3:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval:.2f}s", ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "grafik3_paket_kaybi.png"), dpi=300)
    plt.close()

    print(f"[BAŞARI] 3 adet akademik grafik '{output_dir}' klasörüne kaydedildi!")

if __name__ == "__main__":
    generate_plots()