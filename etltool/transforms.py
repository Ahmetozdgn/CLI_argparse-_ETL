"""
etltool.transforms
==================
ETL dönüşüm fonksiyonları: filtreleme, normalleştirme, birleştirme.

Bu modül Ahmet'in main.py'si tarafından import edilir.
Tüm fonksiyonlar satır listesi (list[str]) alır, list[str] döndürür.
"""

import re
import unicodedata


# ---------------------------------------------------------------------------
# Filtreleme
# ---------------------------------------------------------------------------

def filter_lines(lines: list[str], pattern: str, case_sensitive: bool = False) -> list[str]:
    """
    Yalnızca `pattern` kalıbını içeren satırları döndürür.

    Args:
        lines: İşlenecek satır listesi.
        pattern: Aranacak metin kalıbı (düz metin, regex DEĞİL).
        case_sensitive: True ise büyük/küçük harf duyarlı arama yapar.

    Returns:
        Kalıbı içeren satırların listesi.

    Örnek:
        >>> filter_lines(["elma\\n", "armut\\n"], "elma")
        ['elma\\n']
    """
    if not pattern:
        return list(lines)

    if case_sensitive:
        return [line for line in lines if pattern in line]
    else:
        pattern_lower = pattern.lower()
        return [line for line in lines if pattern_lower in line.lower()]


def exclude_lines(lines: list[str], pattern: str, case_sensitive: bool = False) -> list[str]:
    """
    `pattern` kalıbını içeren satırları ÇIKARIR; kalanları döndürür.

    Örnek:
        >>> exclude_lines(["HATA: bozuk\\n", "normal satır\\n"], "HATA")
        ['normal satır\\n']
    """
    matched = set(id(line) for line in filter_lines(lines, pattern, case_sensitive))
    return [line for line in lines if id(line) not in matched]


# ---------------------------------------------------------------------------
# Normalleştirme
# ---------------------------------------------------------------------------

def normalize_whitespace(line: str) -> str:
    """Baş ve son boşlukları temizler, ortadaki çoklu boşlukları tek boşluğa indirger."""
    return re.sub(r"[ \t]+", " ", line.strip())


def normalize_case(line: str, mode: str = "lower") -> str:
    """
    Harf büyüklüğünü normalleştirir.

    Args:
        line: İşlenecek satır (newline içerebilir).
        mode: 'lower' (küçük), 'upper' (büyük), 'title' (kelime başı büyük).
    """
    content = line.rstrip("\n\r")
    suffix = line[len(content):]  # newline karakterini koru

    if mode == "lower":
        return content.lower() + suffix
    elif mode == "upper":
        return content.upper() + suffix
    elif mode == "title":
        return content.title() + suffix
    else:
        raise ValueError(f"Geçersiz mod: '{mode}'. 'lower', 'upper' veya 'title' kullanın.")


def remove_special_chars(line: str, keep_pattern: str = r"[a-zA-Z0-9ğüşıöçĞÜŞİÖÇ \t,.\-_]") -> str:
    """
    Satırdan özel karakterleri temizler; `keep_pattern`'e uyanları korur.

    Args:
        line: İşlenecek satır.
        keep_pattern: Korunacak karakter sınıfı (regex karakter sınıfı).

    Örnek:
        >>> remove_special_chars("merhaba! dünya@#$")
        'merhaba dünya'
    """
    content = line.rstrip("\n\r")
    suffix = line[len(content):]
    cleaned = re.sub(f"[^{keep_pattern[1:-1]}]", "", content)
    return cleaned + suffix


def normalize_unicode(line: str, form: str = "NFC") -> str:
    """
    Unicode normalleştirme uygular (NFC, NFD, NFKC, NFKD).
    Farklı kaynaklardan gelen Türkçe karakterlerin tutarlı olmasını sağlar.
    """
    content = line.rstrip("\n\r")
    suffix = line[len(content):]
    return unicodedata.normalize(form, content) + suffix


def normalize_lines(
    lines: list[str],
    whitespace: bool = True,
    case: str | None = "lower",
    special_chars: bool = False,
    unicode_form: str = "NFC",
) -> list[str]:
    """
    Satır listesine normalleştirme adımlarını uygular.

    Args:
        lines: İşlenecek satır listesi.
        whitespace: Boşluk normalleştirmesi uygulansın mı?
        case: Harf büyüklüğü modu: 'lower', 'upper', 'title' veya None (değiştirme).
        special_chars: Özel karakterler kaldırılsın mı?
        unicode_form: Unicode normalleştirme formu.

    Returns:
        Normalleştirilmiş satır listesi.
    """
    result = []
    for line in lines:
        content = line.rstrip("\n\r")
        suffix = "\n"  # standart satır sonu

        content = unicodedata.normalize(unicode_form, content)

        if whitespace:
            content = normalize_whitespace(content)

        if case is not None:
            content = normalize_case(content + suffix, mode=case).rstrip("\n\r")

        if special_chars:
            content = remove_special_chars(content + suffix).rstrip("\n\r")

        result.append(content + suffix)
    return result


# ---------------------------------------------------------------------------
# Birleştirme
# ---------------------------------------------------------------------------

def merge_files(file_paths: list[str], encoding: str = "utf-8") -> list[str]:
    """
    Birden fazla dosyayı okur ve satırlarını birleştirir.

    Args:
        file_paths: Okunacak dosyaların yolları.
        encoding: Dosya kodlaması.

    Returns:
        Tüm dosyaların satırlarını içeren tek bir liste.

    Raises:
        FileNotFoundError: Dosya bulunamazsa.
        UnicodeDecodeError: Kodlama hatası olursa.
    """
    merged: list[str] = []
    for path in file_paths:
        with open(path, "r", encoding=encoding) as f:
            merged.extend(f.readlines())
    return merged


def merge_lines(sources: list[list[str]], add_separator: bool = False) -> list[str]:
    """
    Birden fazla satır listesini birleştirir (bellek içi).

    Args:
        sources: Birleştirilecek satır listeleri.
        add_separator: Her kaynak arasına ayırıcı satır eklensin mi?

    Returns:
        Birleştirilmiş satır listesi.
    """
    result: list[str] = []
    for i, source in enumerate(sources):
        if add_separator and i > 0:
            result.append("---\n")
        result.extend(source)
    return result


def deduplicate(lines: list[str], strip_before_compare: bool = True) -> list[str]:
    """
    Tekrarlı satırları kaldırır, ilk görünümü korur.

    Args:
        lines: İşlenecek satırlar.
        strip_before_compare: Karşılaştırma yaparken baş/son boşlukları yoksay.
    """
    seen: set[str] = set()
    result: list[str] = []
    for line in lines:
        key = line.strip() if strip_before_compare else line
        if key not in seen:
            seen.add(key)
            result.append(line)
    return result
