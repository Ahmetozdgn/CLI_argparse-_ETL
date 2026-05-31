import os
import sys
import pytest
import tempfile

from etltool.main import main, build_parser
from etltool.transforms import filter_lines, normalize_lines


class TestBuildParser:
    def test_varsayilan_degerler(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.input is None
        assert args.output is None
        assert args.filter_pattern is None
        assert args.normalize is None
        assert args.encoding == "utf-8"

    def test_input_output_kisayol(self):
        parser = build_parser()
        args = parser.parse_args(["-i", "a.csv", "-o", "b.csv"])
        assert args.input == "a.csv"
        assert args.output == "b.csv"

    def test_filter_ve_normalize(self):
        parser = build_parser()
        args = parser.parse_args(["--filter", "hata", "--normalize"])
        assert args.filter_pattern == "hata"
        assert args.normalize == "lower"

    def test_encoding_secenegi(self):
        parser = build_parser()
        args = parser.parse_args(["--encoding", "latin-1"])
        assert args.encoding == "latin-1"


class TestFilterLines:
    def test_filtre_eslesme(self):
        lines = ["elma\n", "armut\n", "erik\n"]
        sonuc = filter_lines(lines, "elma")
        assert sonuc == ["elma\n"]

    def test_filtre_buyuk_kucuk_harf_duyarsiz(self):
        lines = ["HATA: bağlantı kesildi\n", "bilgi mesajı\n"]
        sonuc = filter_lines(lines, "hata")
        assert len(sonuc) == 1

    def test_filtre_yok_tum_satirlar(self):
        lines = ["a\n", "b\n", "c\n"]
        sonuc = filter_lines(lines, "")
        assert len(sonuc) == 3

    def test_normalize_bosluk_temizle(self):
        lines = ["  merhaba dünya  \n"]
        sonuc = normalize_lines(lines, whitespace=True, case="upper")
        assert sonuc == ["MERHABA DÜNYA\n"]

    def test_bos_girdi(self):
        assert filter_lines([], "kalip") == []


class TestMainIntegrasyon:
    def _gecici_dosya(self, icerik, encoding="utf-8"):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding=encoding
        )
        tmp.write(icerik)
        tmp.close()
        return tmp.name

    def teardown_method(self, _):
        for attr in ("girdi", "cikti"):
            yol = getattr(self, attr, None)
            if yol and os.path.exists(yol):
                os.unlink(yol)

    def test_temel_kopyalama(self):
        self.girdi = self._gecici_dosya("satir1\nsatir2\n")
        self.cikti = self.girdi + "_out.txt"
        main(["--input", self.girdi, "--output", self.cikti])
        with open(self.cikti, encoding="utf-8") as f:
            icerik = f.read()
        assert "satir1" in icerik

    def test_filtre_cikti(self):
        self.girdi = self._gecici_dosya("elma\narmut\nerik\n")
        self.cikti = self.girdi + "_out.txt"
        main(["--input", self.girdi, "--output", self.cikti, "--filter", "elma"])
        with open(self.cikti, encoding="utf-8") as f:
            satirlar = f.readlines()
        assert len(satirlar) == 1

    def test_olmayan_dosya_cikis_kodu(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--input", "OLMAYAN_DOSYA_12345.csv"])
        assert exc_info.value.code != 0

    def test_normalize_buyuk_harf(self):
        self.girdi = self._gecici_dosya("küçük harf\n")
        self.cikti = self.girdi + "_out.txt"
        main(["--input", self.girdi, "--output", self.cikti, "--normalize", "upper"])
        with open(self.cikti, encoding="utf-8") as f:
            icerik = f.read()
        assert "KÜÇÜK HARF" in icerik
