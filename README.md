# etltool — CLI ETL Aracı (Şifanur Karakılçık Branch)

> Branch: `feature/etl-transform`

Komut satırından dosya okuyan, satırları filtreleyen, normalleştiren, birleştiren ve tekilleştiren küçük bir ETL aracı.

---

## Kurulum

```bash
pip install -r requirements.txt
pip install -e .   # opsiyonel — konsol giriş noktası için
```

---

## Kullanım

### 1. Filtrele — yalnızca "istanbul" içeren satırları al
```bash
python -m etltool.main --input ornek_girdi.csv --filter "istanbul" --output istanbul.csv
```

### 2. Hatalı satırları dışarıda bırak + normalleştir
```bash
python -m etltool.main --input ornek_girdi.csv --filter "HATA" --exclude --normalize lower --output temiz.csv
```

### 3. İki dosyayı birleştir, tekrarları kaldır, büyük harfe çevir
```bash
python -m etltool.main --merge dosya1.csv dosya2.csv --dedup --normalize upper --output birlesik.csv
```

### Ek örnekler

```bash
# stdin'den oku, stdout'a yaz
cat ornek_girdi.csv | python -m etltool.main --normalize lower

# Özel karakterleri temizle
python -m etltool.main --input ornek_girdi.csv --remove-special --output temiz.csv

# Dosyalar arasına ayırıcı ekle
python -m etltool.main --merge a.csv b.csv --separator --output birlesik.csv
```

---

## Argümanlar

| Argüman | Açıklama |
|---|---|
| `--input`, `-i` | Girdi dosyası. Belirtilmezse stdin. |
| `--output`, `-o` | Çıktı dosyası. Belirtilmezse stdout. `-` de stdout. |
| `--merge DOSYA [DOSYA ...]` | Birleştirilecek ek dosyalar. |
| `--filter`, `-f` | Yalnızca kalıbı içeren satırları tut. |
| `--exclude` | `--filter` ile birlikte: eşleşenleri ÇIKAR. |
| `--normalize [lower\|upper\|title]` | Harf büyüklüğü normalleştirmesi. |
| `--no-whitespace` | Boşluk normalleştirmesini kapat. |
| `--remove-special` | Özel karakterleri kaldır. |
| `--dedup` | Tekrarlı satırları kaldır. |
| `--separator` | Birleştirilen dosyalar arasına `---` ekle. |
| `--encoding`, `-e` | Dosya kodlaması (varsayılan: `utf-8`). |

---

## Testleri Çalıştırma

```bash
# Tüm testler
pytest tests/ -v

# Yalnızca dönüşüm testleri
pytest tests/test_transforms.py -v

# Kısa çıktı
pytest tests/
```

---

## Proje Yapısı

```
etltool/
├── etltool/
│   ├── __init__.py
│   ├── __main__.py       ← python -m etltool desteği
│   ├── main.py           ← CLI giriş noktası
│   └── transforms.py     ← ETL dönüşüm fonksiyonları
├── tests/
│   ├── __init__.py
│   └── test_transforms.py
├── ornek_girdi.csv
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## transforms.py — Fonksiyon Özeti

| Fonksiyon | Ne Yapar? |
|---|---|
| `filter_lines(lines, pattern)` | Kalıbı içeren satırları döndürür |
| `exclude_lines(lines, pattern)` | Kalıbı içeren satırları çıkarır |
| `normalize_lines(lines, ...)` | Boşluk + harf + unicode normalleştirme |
| `merge_files(paths)` | Dosyaları okur ve birleştirir |
| `merge_lines(sources)` | Bellek içi liste birleştirme |
| `deduplicate(lines)` | Tekrarlı satırları kaldırır |
