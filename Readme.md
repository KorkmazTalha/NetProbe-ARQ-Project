# NetProbe Project: Application-Layer Stop-and-Wait ARQ Protocol

Bu proje, güvensiz ve paket kayıplarına açık bir taşıma katmanı protokolü olan **UDP** üzerinde, uygulama katmanında (Application Layer) sıfırdan geliştirilmiş bir **Stop-and-Wait ARQ (Automatic Repeat Request)** güvenilir veri iletim protokolü simülasyonudur. Sistem; kontrolsüz ağ ortamlarında yapay paket kayıpları ve ağ gecikmeleri (RTT) altında bile verinin alıcı tarafa %100 kararlılıkla, MD5 bütünlük doğrulamalı ve hatasız ulaştırılmasını garanti eder.

## 🚀 Bağımlılıklar (Dependencies)

Projenin temel ağ motoru ve soket yönetimi Python'ın tamamen yerleşik (built-in) standart kütüphaneleriyle yazılmıştır. Deney sonrası oluşan metriklerin analizi ve akademik grafik üretimi için aşağıdaki harici kütüphaneler kullanılmaktadır:

* Python 3.12+
* Pandas (v2.2+)
* Matplotlib (v3.8+)

Bağımlılıkları sisteminize hızlıca entegre etmek için terminalde aşağıdaki komutu çalıştırabilirsiniz:

```bash
pip install pandas matplotlib

```

---

## 📁 Proje Yapısı (Project Structure)

Proje, nesne yönelimli ve katmanlı mimari standartlarına tam uyumlu olarak şu şekilde yapılandırılmıştır:

```text
NetProbe_Project/
│
├── src/
│   ├── config.py                 # Merkezi ağ parametreleri ve dinamik çevre değişkenleri
│   ├── protocol.py               # Paketleme motoru (TYPE|SEQ|CHECKSUM|PAYLOAD) ve MD5
│   ├── server.py                 # UDP Sunucu ve Yapay Ağ Simülatörü (Drop/Delay)
│   ├── client.py                 # UDP İstemci ve Stop-and-Wait ARQ Protokol Motoru
│   └── experiment_runner.py       # Senaryoları ardışık koşturan otomasyon motoru
│
├── utils/
│   ├── simulator.py              # Ağ simülasyon fonksiyonları (Random Drop & Sleep)
│   └── logger.py                 # Ağ olaylarını anlık CSV'ye işleyen log motoru
│
├── analysis/
│   ├── logs/                     # Senaryo bazlı ham CSV logları ve özet raporlar
│   ├── plots/                    # Matplotlib tarafından üretilen akademik grafikler (.png)
│   └── plot_results.py           # Deney sonuçlarını analiz edip görselleştiren script
│
└── README.md                     # Proje dokümantasyonu

```

---

## 🛠️ Çalıştırma Adımları (How to Run)

Sistem, deneylerin yapılmasından grafiklerin üretilmesine kadar olan tüm süreci tam otomasyonla tek komut üzerinden yönetebilecek şekilde tasarlanmıştır.

### 1. Tüm Deney Senaryolarını Çalıştırma

Aşağıdaki otomasyon scripti, `src/config.py` içerisindeki varsayılan değerleri dinamik çevre değişkenleri (environment variables) ile ezerek tanımlı ağ senaryolarını arka arkaya koşturur. Her senaryo bittiğinde, işletim sisteminin UDP portunu temizlemesi için güvenli bir bekleme süresi bırakır ve logları `analysis/logs/` içerisine kaydeder:

```bash
python src/experiment_runner.py

```

### 2. Veri Analizi ve Grafiklerin Üretilmesi

Deney motoru tamamlandıktan sonra üretilen `experiment_summary.csv` dosyasındaki verileri anlamlı akademik grafiklere dönüştürmek için analiz scriptini çalıştırın:

```bash
python analysis/plot_results.py

```

*Bu komutun ardından grafikler otomatik olarak `analysis/plots/` dizini altında yüksek çözünürlüklü (.png) olarak doğrulanacaktır.*

---

## 📊 Deneysel Senaryolar ve Performans Analizi

Sistem, gerçekleştirilen simülasyonlarda Stop-and-Wait ARQ protokolünün karakteristiğini doğrulamak adına 3 farklı ana senaryo kümesi üzerinde test edilmiştir:

### 1. Paket Boyutunun Toplam Transfer Süresine Etkisi (Senaryo 1)

* **Koşullar:** %0 Paket Kaybı, 0ms Yapay Gecikme.
* **Gözlem:** Paket boyutu 512 Byte'tan 2048 Byte'a çıkarıldığında toplam transfer süresi doğrusal olarak **0.40 saniyeden 0.15 saniyeye** düşmüştür.
* **Akademik Çıkarım:** Stop-and-Wait mimarisinde paket boyutu büyüdükçe, toplam paket sayısı ve dolayısıyla her paket başına harcanan soket/başlık (header overhead) ek yükü azalarak kanal verimliliği artmaktadır.

### 2. Ağ Gecikmesinin (RTT) Toplam Transfer Süresine Etkisi (Senaryo 2)

* **Koşullar:** 1024B Sabit Paket Boyutu, %0 Paket Kaybı.
* **Gözlem:** Yapay ağ gecikmesi 0ms'den 50ms'ye çıkarıldığında transfer süresi **30.22 saniyeye** fırlamıştır.
* **Akademik Çıkarım:** Hat üzerinde hiçbir kayıp olmasa dahi, Stop-and-Wait ARQ protokolü doğası gereği hattı dolduramaz ve **Bant Genişliği - Gecikme Çarpımı (BDP)** sınırına takılır. İstemci sonraki paketi göndermek için RTT süresince engellendiğinden (blocked state), gecikme artışı süreyi doğrudan katlar.

### 3. Paket Kayıp Oranının Toplam Transfer Süresine Etkisi (Senaryo 3)

* **Koşullar:** 1024B Sabit Paket Boyutu, 10ms Sabit Yapay Gecikme.
* **Gözlem:** %15 agresif paket kaybı altında, toplam **539 paketlik** (538 veri + 1 bitiş) transfer süreci **53.89 saniyede** %100 başarıyla tamamlanmıştır.
* **Akademik Çıkarım:** `src/config.py` dosyasında `0.5 saniye` olarak kilitlenen sabit Zaman Aşımı (Timeout - RTO) değeri, hattan düşürülen paketleri başarıyla yakalamıştır. İstemci tarafındaki `socket.timeout` mekanizması cezayı çekerek paketi hattan yeniden sürmüş (Retransmit), alıcı tarafta veri bütünlüğü sıfır hata ve tam MD5 doğrulamasıyla korunmuştur.

---

## 💡 Öne Çıkan Mühendislik Detayları

* **Dinamik Artık Paket Yönetimi (Residual Chunk Control):** Dosya okuma işlemlerinde son parça RAM'i şişirmemek adına dinamik buffer kontrolüyle yönetilir. Deney çıktılarında görüleceği üzere, 1024B'lık akışın sonunda kalan son paket tam olarak **`Boyut: 480 byte`** olarak paketlenip hatta sürülmüştür.
* **Tam Güvenilirlik:** İstemci tarafında peş peşe yaşanan kayıplarda (Örn: Paket 516 veya Paket 205), `MAX_RETRANSMISSIONS = 5` sınırı aşılmadan durum `(1/5)`, `(2/5)` şeklinde retransmit sayacıyla anlık loglanarak hata toleransı gösterilmiştir.

---

## 🔗 GitHub Bağlantısı

Projenin güncel kaynak kodlarına, log geçmişine ve rapor dokümanlarına aşağıdaki depo (repository) üzerinden erişebilirsiniz:

* **GitHub Repository:** https://github.com/kullanici_adin/NetProbe_Project