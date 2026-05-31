# etltool — CLI Tabanlı ETL Aracı

> **Kategori:** YZTA Learn Challenge  
> **Proje:** Komut satırından dosya girişi alan ve satırları dönüştürüp (filtre/normalize/birleştir) çıktı üreten bir araç

Komut satırından dosya okuyabilen, satırları filtreleyen, normalleştiren, birleştiren ve tekrarlı satırları kaldıran basit ancak işlevsel bir ETL aracı. Python argparse modülüyle derli toplu CLI arayüzü sunar.

---

## 📋 Ekip

- **Şifanur Karakılçık**
- **Ahmet Özdoğan**

---

## 🏗️ Proje Yapısı

```
etltool/
├── etltool/
│   ├── __init__.py
│   ├── __main__.py              ← python -m etltool desteği
│   ├── main.py                  ← argparse tabanlı CLI giriş noktası
│   └── transforms.py            ← ETL dönüşüm fonksiyonları
├── tests/
│   ├── __init__.py
│   ├── test_cli.py              ← CLI testleri
│   └── test_transforms.py       ← Dönüşüm fonksiyon testleri
├── ornek_girdi.csv              ← Örnek veri seti
├── pyproject.toml               ← Proje konfigürasyonu
├── requirements.txt             ← Bağımlılıklar
└── README.md
```

---

## 🚀 Kurulum

### 1. Projeyi klonlayın

```bash
git clone <repo-url>
cd etltool
```

### 2. Sanal ortam oluşturun ve etkinleştirin

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

### 4. (Opsiyonel) Konsol giriş noktası kurulumu

Kurulu etmek istiyorsanız CLI komutunu doğrudan çalıştırabilirsiniz:
```bash
pip install -e .
etltool --help
```

---

## 💡 Hızlı Başlangıç

### Örnek dosyayı görün
```bash
cat ornek_girdi.csv
```

**Çıktı:**
```
id,isim,sehir,puan
1,Ahmet Yılmaz,İstanbul,85
2,  Ayşe Kaya  ,Ankara,92
3,Mehmet Demir,İzmir,78
4,FATMA ŞAHİN,Bursa,65
5,ali veli,Antalya,90
6,Zeynep Arslan,İstanbul,88
HATA: bu satır bozuk veri içeriyor
7,Mustafa Çelik,Konya,73
```

---

## 📖 Kullanım Örnekleri

### 1️⃣ Basit Filtreleme — "İstanbul" içeren satırları bul

```bash
python -m etltool.main --input ornek_girdi.csv --filter "İstanbul" --output istanbul_sonucu.csv
```

**Sonuç:** `istanbul_sonucu.csv` dosyasında sadece İstanbul'u içeren satırlar bulunur.

```csv
id,isim,sehir,puan
1,Ahmet Yılmaz,İstanbul,85
6,Zeynep Arslan,İstanbul,88
```

---

### 2️⃣ Filtreleme + Hariç Tutma — Hataları dışarı bırak

Kalıp eşleşiyorsa bu sefer hariç TUT (--exclude bayrağı):

```bash
python -m etltool.main --input ornek_girdi.csv --filter "HATA" --exclude --output temiz.csv
```

**Sonuç:** Bozuk satır kaldırılır, temiz veri kalır:
```csv
id,isim,sehir,puan
1,Ahmet Yılmaz,İstanbul,85
2,  Ayşe Kaya  ,Ankara,92
...
```

---

### 3️⃣ Normalleştirme — Boşlukları temizle ve küçük harfe çevir

```bash
python -m etltool.main --input ornek_girdi.csv --normalize lower --output normalized.csv
```

**Etki:**
- Satır başı/sonu boşluklar kaldırılır
- Tüm metinler küçük harfe dönüştürülür
- Özel karakterler korunur (ç, ş, ü vb.)

---

### 4️⃣ Birleştirme + Tekrar Kaldırma — İki dosyayı merge et

Diyelim ki `dosya1.csv` ve `dosya2.csv` var:

```bash
python -m etltool.main --merge dosya1.csv dosya2.csv --dedup --output birlesik.csv
```

**Etki:**
- İki dosya birleştirilir
- Tekrarlı satırlar kaldırılır
- Sonuç `birlesik.csv` dosyasına yazılır

---

### 5️⃣ Birleştirme + Ayırıcı Ekle — Dosyaları ayırt et

```bash
python -m etltool.main --merge dosya1.csv dosya2.csv --separator --output birlesik_ayirici.csv
```

**Etki:** Dosyalar arasına `---` satırı eklenir (hangi satır hangi dosyadan geldiğini görmek için).

---

### 6️⃣ Özel Karakterleri Temizle

```bash
python -m etltool.main --input ornek_girdi.csv --remove-special --output ASCII_temiz.csv
```

**Etki:** Ç, Ş, Ğ, İ, Ö, Ü gibi Türkçe karakterler kaldırılır (veya ASCII eşdeğerleri çalışmıyor ise silinir).

---

### 7️⃣ stdin/stdout ile Pipe Kullanımı

```bash
cat ornek_girdi.csv | python -m etltool.main --normalize lower --filter "istanbul"
```

**Sonuç:** Doğrudan terminale yazdırılır (stdout'a).

---

### 8️⃣ Kombinasyon — Filtre + Normalize + Dedup + Çıktı

```bash
python -m etltool.main \
  --input ornek_girdi.csv \
  --filter "HATA" \
  --exclude \
  --normalize upper \
  --remove-special \
  --dedup \
  --output final_veri.csv
```

**Etki:**
1. "HATA" içeren satırlar çıkarılır
2. Tüm metinler BÜYÜK HARFE çevrilir
3. Özel karakterler kaldırılır
4. Tekrarlar silinir
5. Sonuç `final_veri.csv` dosyasına kaydedilir

---

## 📋 Argümanlar Referansı

| Argüman | Kısa | Açıklama | Örnek |
|---|---|---|---|
| `--input` | `-i` | Girdi dosyası yolu (belirtilmezse stdin) | `--input girdi.csv` |
| `--output` | `-o` | Çıktı dosyası yolu (belirtilmezse stdout) | `--output cikti.csv` |
| `--merge` | — | Birleştirilecek dosya listesi (2+ dosya) | `--merge dosya1.csv dosya2.csv` |
| `--filter` | `-f` | İçerdiği kalıbı bul (case-sensitive) | `--filter "istanbul"` |
| `--exclude` | — | `--filter` sonucunu tersine çevir (kalıbı ÇIKAR) | `--filter "HATA" --exclude` |
| `--normalize` | `-n` | Harf büyüklüğü normalleştirmesi: `lower`, `upper`, `title` | `--normalize lower` |
| `--no-whitespace` | — | Boşluk normalleştirmesini devre dışı bırak | `--no-whitespace` |
| `--remove-special` | — | Özel karakterleri kaldır | `--remove-special` |
| `--dedup` | — | Tekrarlı satırları sil (ilk oluşumu tutar) | `--dedup` |
| `--separator` | — | Merge yapılırken dosyalar arası `---` ekle | `--merge dosya1.csv dosya2.csv --separator` |
| `--encoding` | `-e` | Dosya kodlaması (varsayılan: `utf-8`) | `--encoding latin-1` |

---

## 🧪 Testleri Çalıştırma

Tüm testleri çalıştırın:
```bash
pytest tests/ -v
```

Yalnızca dönüşüm testleri:
```bash
pytest tests/test_transforms.py -v
```

Yalnızca CLI testleri:
```bash
pytest tests/test_cli.py -v
```

Kısa çıktı:
```bash
pytest tests/
```

---

## 🔧 transforms.py — Fonksiyon Özeti

Temel dönüşüm fonksiyonları `etltool/transforms.py` içinde tanımlı:

| Fonksiyon | Girdi | Çıktı | Açıklama |
|---|---|---|---|
| `filter_lines(lines, pattern)` | Satır listesi, aranacak kalıp | Satır listesi | Kalıbı içeren satırları döndürür |
| `exclude_lines(lines, pattern)` | Satır listesi, aranacak kalıp | Satır listesi | Kalıbı içeren satırları çıkarır |
| `normalize_lines(lines, ...)` | Satır listesi, normalizasyon seçenekleri | Satır listesi | Boşluk, harf büyüklüğü, özel char normalleştir |
| `merge_files(paths, encoding)` | Dosya yolu listesi, kodlama | Satır listesi | Dosyaları sırayla okur ve birleştirir |
| `deduplicate(lines)` | Satır listesi | Satır listesi | Tekrarlı satırları sil (ilk oluşumu tutar) |

---

## 📝 Örnek İş Akışı

1. **Veri temizliği:** Bozuk satırları dışarı bırak
   ```bash
   python -m etltool.main --input ham_veri.csv --filter "ERROR" --exclude --output temiz.csv
   ```

2. **Normalleştirme:** Boşlukları temizle ve standartlaştır
   ```bash
   python -m etltool.main --input temiz.csv --normalize lower --output normalized.csv
   ```

3. **Birleştirme:** Birden fazla kaynaktan veri topla
   ```bash
   python -m etltool.main --merge normalized.csv ek_veri.csv --dedup --output final.csv
   ```

Tüm adımlar aynı komutla kombinlenebilir:
```bash
python -m etltool.main \
  --input ham_veri.csv \
  --filter "ERROR" --exclude \
  --merge ek_veri.csv \
  --normalize lower \
  --dedup \
  --output final_temiz.csv
```

---

## ⚙️ Hata Çıkış Kodları

| Kod | Anlamı |
|---|---|
| `0` | Başarı |
| `2` | Dosya bulunamadı |
| `3` | Kodlama hatası |
| `4` | Dosya okuma hatası |
| `5` | Çıktı dosyası yazma hatası |

---

## 📚 İleri Kullanım

### Büyük dosyaları satır satır işle

```bash
# 1GB dosyayı stdin üzerinden işle
cat gercek_veri.csv | python -m etltool.main --normalize lower > temiz_cikti.csv
```

### Farklı kodlama ile dosya oku

```bash
# Windows-1252 (CP1252) kodlamasında dosya oku
python -m etltool.main --input windows_dosyasi.csv --encoding cp1252 --output utf8_cikti.csv
```

### Shell script içinde kullan

```bash
#!/bin/bash

INPUT="ham_veri.csv"
OUTPUT="sonuc.csv"

python -m etltool.main \
  --input "$INPUT" \
  --filter "GEÇERSIZ" --exclude \
  --normalize lower \
  --dedup \
  --output "$OUTPUT"

echo "İşlem tamamlandı: $OUTPUT"
```

---

## 📌 Notlar

- **Filtreleme case-sensitive'dir:** `"İstanbul"` ile `"istanbul"` farklı sonuç verir.
- **Dedup:** İlk oluşan satırı tutar, sonraki tekrarları siler.
- **Unicode Desteği:** Türkçe karakterler (ç, ş, ü, ö, ğ, ı) tam olarak desteklenir.
- **stdin/stdout:** Varsayılan giriş stdin, varsayılan çıkış stdout'dur. Pipe ile zincirleme mümkün.

---

## 📄 Lisans

Bu proje YZTA Learn Challenge kapsamında geliştirilmiştir.
