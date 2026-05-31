"""
ETL dönüşüm fonksiyonlarını test eder: filtreleme, normalleştirme, birleştirme.
Çalıştırma: pytest tests/test_transforms.py -v
"""

import os
import tempfile
import pytest

from etltool.transforms import (
    filter_lines,
    exclude_lines,
    normalize_whitespace,
    normalize_case,
    remove_special_chars,
    normalize_lines,
    merge_files,
    merge_lines,
    deduplicate,
)


# ---------------------------------------------------------------------------
# filter_lines
# ---------------------------------------------------------------------------

class TestFilterLines:
    def test_basit_eslesme(self):
        lines = ["elma\n", "armut\n", "erik\n"]
        assert filter_lines(lines, "elma") == ["elma\n"]

    def test_buyuk_kucuk_harf_duyarsiz(self):
        lines = ["HATA oluştu\n", "bilgi\n"]
        assert filter_lines(lines, "hata") == ["HATA oluştu\n"]

    def test_buyuk_kucuk_harf_duyarli(self):
        lines = ["HATA\n", "hata\n"]
        assert filter_lines(lines, "hata", case_sensitive=True) == ["hata\n"]

    def test_bos_kalip_tum_satirlar(self):
        lines = ["a\n", "b\n"]
        assert filter_lines(lines, "") == lines

    def test_bos_giris(self):
        assert filter_lines([], "kalip") == []

    def test_coklu_eslesme(self):
        lines = ["istanbul satırı\n", "ISTANBUL bilgisi\n", "ankara\n"]
        sonuc = filter_lines(lines, "istanbul")
        assert len(sonuc) == 2

    def test_eslesme_yok(self):
        lines = ["elma\n", "armut\n"]
        assert filter_lines(lines, "kiraz") == []


# ---------------------------------------------------------------------------
# exclude_lines
# ---------------------------------------------------------------------------

class TestExcludeLines:
    def test_hata_satirlarini_cikart(self):
        lines = ["HATA: bozuk\n", "normal satır\n", "HATA: tekrar\n"]
        sonuc = exclude_lines(lines, "HATA")
        assert sonuc == ["normal satır\n"]

    def test_eslesme_yok_hepsi_kalsin(self):
        lines = ["a\n", "b\n"]
        assert exclude_lines(lines, "XYZ") == lines


# ---------------------------------------------------------------------------
# normalize_whitespace
# ---------------------------------------------------------------------------

class TestNormalizeWhitespace:
    def test_bas_son_bosluk(self):
        assert normalize_whitespace("  merhaba  ") == "merhaba"

    def test_coklu_ic_bosluk(self):
        assert normalize_whitespace("merhaba   dünya") == "merhaba dünya"

    def test_sekme_karakteri(self):
        assert normalize_whitespace("\tmerhaba\t") == "merhaba"

    def test_bos_string(self):
        assert normalize_whitespace("   ") == ""


# ---------------------------------------------------------------------------
# normalize_case
# ---------------------------------------------------------------------------

class TestNormalizeCase:
    def test_lower(self):
        assert normalize_case("MERHABA DÜNYA\n", "lower") == "merhaba dünya\n"

    def test_upper(self):
        assert normalize_case("merhaba dünya\n", "upper") == "MERHABA DÜNYA\n"

    def test_title(self):
        assert normalize_case("merhaba dünya\n", "title") == "Merhaba Dünya\n"

    def test_gecersiz_mod(self):
        with pytest.raises(ValueError):
            normalize_case("test\n", "invalid")

    def test_newline_korunur(self):
        sonuc = normalize_case("test\n", "upper")
        assert sonuc.endswith("\n")


# ---------------------------------------------------------------------------
# remove_special_chars
# ---------------------------------------------------------------------------

class TestRemoveSpecialChars:
    def test_ozel_karakter_kaldir(self):
        sonuc = remove_special_chars("merhaba! dünya@#$\n")
        assert "!" not in sonuc
        assert "@" not in sonuc
        assert "merhaba" in sonuc

    def test_normal_metin_korunur(self):
        sonuc = remove_special_chars("merhaba dünya\n")
        assert "merhaba" in sonuc
        assert "dünya" in sonuc


# ---------------------------------------------------------------------------
# normalize_lines (entegre)
# ---------------------------------------------------------------------------

class TestNormalizeLines:
    def test_varsayilan_lower_whitespace(self):
        lines = ["  MERHABA DÜNYA  \n"]
        sonuc = normalize_lines(lines)
        assert sonuc == ["merhaba dünya\n"]

    def test_upper_mod(self):
        lines = ["merhaba\n"]
        sonuc = normalize_lines(lines, case="upper")
        assert sonuc == ["MERHABA\n"]

    def test_whitespace_kapali(self):
        lines = ["  test  \n"]
        sonuc = normalize_lines(lines, whitespace=False, case=None)
        assert sonuc == ["  test  \n"]

    def test_case_none(self):
        lines = ["Karma Büyüklük\n"]
        sonuc = normalize_lines(lines, case=None)
        assert sonuc == ["Karma Büyüklük\n"]

    def test_bos_liste(self):
        assert normalize_lines([]) == []


# ---------------------------------------------------------------------------
# merge_files
# ---------------------------------------------------------------------------

class TestMergeFiles:
    def _yaz(self, icerik: str, encoding: str = "utf-8") -> str:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding=encoding
        )
        tmp.write(icerik)
        tmp.close()
        return tmp.name

    def teardown_method(self, _):
        for attr in ("f1", "f2"):
            yol = getattr(self, attr, None)
            if yol and os.path.exists(yol):
                os.unlink(yol)

    def test_iki_dosya_birlestir(self):
        self.f1 = self._yaz("satir1\nsatir2\n")
        self.f2 = self._yaz("satir3\nsatir4\n")
        sonuc = merge_files([self.f1, self.f2])
        assert len(sonuc) == 4
        assert "satir1\n" in sonuc
        assert "satir4\n" in sonuc

    def test_olmayan_dosya_hata(self):
        with pytest.raises(FileNotFoundError):
            merge_files(["OLMAYAN_DOSYA_99999.txt"])

    def test_tek_dosya(self):
        self.f1 = self._yaz("tek satır\n")
        sonuc = merge_files([self.f1])
        assert sonuc == ["tek satır\n"]


# ---------------------------------------------------------------------------
# merge_lines
# ---------------------------------------------------------------------------

class TestMergeLines:
    def test_iki_liste_birlestir(self):
        a = ["a1\n", "a2\n"]
        b = ["b1\n", "b2\n"]
        sonuc = merge_lines([a, b])
        assert sonuc == ["a1\n", "a2\n", "b1\n", "b2\n"]

    def test_ayirici_ekle(self):
        a = ["a\n"]
        b = ["b\n"]
        sonuc = merge_lines([a, b], add_separator=True)
        assert "---\n" in sonuc
        assert len(sonuc) == 3

    def test_bos_liste(self):
        assert merge_lines([]) == []


# ---------------------------------------------------------------------------
# deduplicate
# ---------------------------------------------------------------------------

class TestDeduplicate:
    def test_tekrarlari_kaldir(self):
        lines = ["a\n", "b\n", "a\n", "c\n"]
        sonuc = deduplicate(lines)
        assert sonuc == ["a\n", "b\n", "c\n"]

    def test_bosluklu_tekrar(self):
        lines = ["merhaba\n", "  merhaba  \n"]
        sonuc = deduplicate(lines, strip_before_compare=True)
        assert len(sonuc) == 1

    def test_bosluklu_tekrar_devre_disi(self):
        lines = ["merhaba\n", "  merhaba  \n"]
        sonuc = deduplicate(lines, strip_before_compare=False)
        assert len(sonuc) == 2

    def test_ilk_gorulum_korunur(self):
        lines = ["BIRINCI\n", "BIRINCI\n"]
        assert deduplicate(lines) == ["BIRINCI\n"]

    def test_bos_liste(self):
        assert deduplicate([]) == []
