# etltool — CLI ETL Aracı (Ahmet Özdoğan Branch)

> Branch: `feature/cli-core`

Komut satırından dosya okuyan, satırları filtreleyen/normalleştiren ve çıktı üreten küçük bir ETL (Extract–Transform–Load) aracı.

---

## Kurulum

```bash
# Bağımlılıkları kur
pip install -r requirements.txt

# Paketi geliştirme modunda yükle (isteğe bağlı)
pip install -e .
```

---

## Kullanım

### Temel kullanım — dosyadan dosyaya
```bash
python -m etltool.main --input ornek_girdi.csv --output cikti.csv
```

### Filtre uygula — yalnızca "istanbul" içeren satırları al
```bash
python -m etltool.main --input ornek_girdi.csv --filter "istanbul" --output istanbul_kayitlar.csv
```

### Normalleştir + stdin/stdout akışı
```bash
cat ornek_girdi.csv | python -m etltool.main --normalize --output -
```

### Farklı dosya kodlaması
```bash
python -m etltool.main --input eski_dosya.txt --encoding latin-1 --output cikti.txt
```

### Konsol giriş noktası (pip install -e . sonrası)
```bash
etltool --input ornek_girdi.csv --filter "hata" --output -
```

---

## Argümanlar

| Argüman | Kısa | Açıklama |
|---|---|---|
| `--input` | `-i` | Girdi dosyası. Belirtilmezse stdin kullanılır. |
| `--output` | `-o` | Çıktı dosyası. Belirtilmezse stdout. `-` de stdout anlamına gelir. |
| `--filter` | `-f` | Yalnızca bu kalıbı içeren satırları tutar (büyük/küçük harf duyarsız). |
| `--normalize` | `-n` | Baş/son boşlukları temizler, büyük harfe çevirir. |
| `--encoding` | `-e` | Dosya kodlaması (varsayılan: `utf-8`). |

---

## Testleri Çalıştırma

```bash
# Tüm testler
pytest tests/ -v

# Yalnızca CLI testleri
pytest tests/test_cli.py -v

# Kısa çıktı
pytest tests/
```

---

## Proje Yapısı

```
etltool/
├── etltool/
│   ├── __init__.py
│   ├── __main__.py      ← python -m etltool desteği
│   └── main.py          ← CLI giriş noktası (argparse)
├── tests/
│   ├── __init__.py
│   └── test_cli.py      ← CLI testleri
├── ornek_girdi.csv
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Hata Mesajları

| Durum | Çıkış Kodu |
|---|---|
| Dosya bulunamadı | 2 |
| Kodlama hatası (açılırken) | 3 |
| Dosya okuma sırasında kodlama hatası | 3 |
| Dosya açma/yazma OS hatası | 4 / 5 |
