"""
etltool.main
============
Komut satırı giriş noktası.

Kullanım:
    python -m etltool.main --input girdi.csv --output cikti.csv
    python -m etltool.main --input girdi.csv --filter "python" --normalize --output cikti.csv
    cat girdi.csv | python -m etltool.main --output cikti.csv
"""

import argparse
import sys
import os


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="etltool",
        description="Küçük ETL aracı: dosya okur, dönüştürür, çıktı üretir.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python -m etltool.main --input girdi.csv --output cikti.csv
  python -m etltool.main --input girdi.csv --filter "hata" --output cikti.csv
  cat girdi.csv | python -m etltool.main --normalize --output -
""",
    )

    parser.add_argument(
        "--input", "-i",
        metavar="DOSYA",
        default=None,
        help="Girdi dosyası yolu. Belirtilmezse standart girişten (stdin) okur.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="DOSYA",
        default=None,
        help="Çıktı dosyası yolu. Belirtilmezse standart çıkışa (stdout) yazar. '-' de stdout anlamına gelir.",
    )
    parser.add_argument(
        "--filter", "-f",
        metavar="KALIP",
        default=None,
        dest="filter_pattern",
        help="Yalnızca bu kalıbı içeren satırları tut (büyük/küçük harf duyarsız).",
    )
    parser.add_argument(
        "--normalize", "-n",
        action="store_true",
        help="Satırları normalleştir: baş/son boşlukları temizle, büyük harfe çevir.",
    )
    parser.add_argument(
        "--encoding", "-e",
        default="utf-8",
        help="Dosya kodlaması (varsayılan: utf-8).",
    )
    return parser


def open_input(path: str | None, encoding: str):
    """Girdi akışını döndürür. path=None → stdin."""
    if path is None:
        return sys.stdin
    if not os.path.exists(path):
        print(
            f"HATA: Girdi dosyası bulunamadı: '{path}'",
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        return open(path, "r", encoding=encoding)
    except (UnicodeDecodeError, LookupError) as exc:
        print(
            f"HATA: Dosya kodlaması okunamadı ('{encoding}'). "
            f"--encoding ile doğru kodlamayı belirtin.\nAyrıntı: {exc}",
            file=sys.stderr,
        )
        sys.exit(3)
    except OSError as exc:
        print(f"HATA: Dosya açılamadı: {exc}", file=sys.stderr)
        sys.exit(4)


def open_output(path: str | None, encoding: str):
    """Çıktı akışını döndürür. path=None veya '-' → stdout."""
    if path is None or path == "-":
        return sys.stdout
    try:
        return open(path, "w", encoding=encoding, newline="")
    except OSError as exc:
        print(f"HATA: Çıktı dosyası oluşturulamadı: {exc}", file=sys.stderr)
        sys.exit(5)


def process_lines(lines, filter_pattern: str | None, normalize: bool) -> list[str]:
    """
    Satırları filtreler ve/veya normalleştirir.
    Dönüşüm mantığı Şifanur'un transforms.py modülünde genişletilecek.
    Şimdilik temel işlemler burada yer alıyor.
    """
    result = []
    for line in lines:
        # Sondaki newline'ı koru ama işlem için şerit uygula
        stripped = line.rstrip("\n\r")

        if normalize:
            stripped = stripped.strip().upper()

        if filter_pattern is not None:
            if filter_pattern.lower() not in stripped.lower():
                continue

        result.append(stripped + "\n")
    return result


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    in_stream = open_input(args.input, args.encoding)
    out_stream = open_output(args.output, args.encoding)

    close_in = args.input is not None
    close_out = args.output is not None and args.output != "-"

    try:
        try:
            lines = in_stream.readlines()
        except UnicodeDecodeError as exc:
            print(
                f"HATA: Dosya okunurken kodlama hatası oluştu. "
                f"--encoding seçeneği ile doğru kodlamayı (örn. latin-1, cp1252) belirtin.\nAyrıntı: {exc}",
                file=sys.stderr,
            )
            sys.exit(3)

        processed = process_lines(lines, args.filter_pattern, args.normalize)
        out_stream.writelines(processed)

        if args.output and args.output != "-":
            print(
                f"Tamamlandı: {len(processed)} satır '{args.output}' dosyasına yazıldı.",
                file=sys.stderr,
            )

    finally:
        if close_in:
            in_stream.close()
        if close_out:
            out_stream.close()


if __name__ == "__main__":
    main()
