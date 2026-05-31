"""
etltool.main
============
Komut satırı giriş noktası — transforms modülü ile entegre.

Kullanım:
    python -m etltool.main --input girdi.csv --output cikti.csv
    python -m etltool.main --input girdi.csv --filter "python" --normalize lower
    python -m etltool.main --merge dosya1.csv dosya2.csv --output birlesik.csv
"""

import argparse
import sys
import os

from etltool.transforms import (
    filter_lines,
    exclude_lines,
    normalize_lines,
    merge_files,
    deduplicate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="etltool",
        description="Küçük ETL aracı: dosya okur, dönüştürür, çıktı üretir.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python -m etltool.main --input girdi.csv --output cikti.csv
  python -m etltool.main --input girdi.csv --filter "hata" --exclude --output temiz.csv
  python -m etltool.main --merge dosya1.csv dosya2.csv --normalize upper --output birlesik.csv
""",
    )

    parser.add_argument("--input", "-i", metavar="DOSYA", default=None,
                        help="Girdi dosyası. Belirtilmezse stdin.")
    parser.add_argument("--output", "-o", metavar="DOSYA", default=None,
                        help="Çıktı dosyası. Belirtilmezse stdout. '-' de stdout.")
    parser.add_argument("--merge", metavar="DOSYA", nargs="+",
                        help="Birleştirilecek ek dosyalar (--input ile birlikte kullanılabilir).")
    parser.add_argument("--filter", "-f", metavar="KALIP", default=None, dest="filter_pattern",
                        help="Yalnızca bu kalıbı içeren satırları tut.")
    parser.add_argument("--exclude", action="store_true",
                        help="--filter kalıbını içeren satırları ÇIKAR (varsayılan: tut).")
    parser.add_argument("--normalize", "-n", metavar="MOD", nargs="?", const="lower",
                        choices=["lower", "upper", "title"],
                        help="Normalleştirme modu: lower (varsayılan), upper, title.")
    parser.add_argument("--no-whitespace", action="store_true",
                        help="Boşluk normalleştirmesini devre dışı bırak.")
    parser.add_argument("--remove-special", action="store_true",
                        help="Özel karakterleri kaldır.")
    parser.add_argument("--dedup", action="store_true",
                        help="Tekrarlı satırları kaldır.")
    parser.add_argument("--separator", action="store_true",
                        help="Birleştirilen dosyalar arasına '---' ayırıcı ekle.")
    parser.add_argument("--encoding", "-e", default="utf-8",
                        help="Dosya kodlaması (varsayılan: utf-8).")
    return parser


def open_output(path: str | None, encoding: str):
    if path is None or path == "-":
        return sys.stdout
    try:
        return open(path, "w", encoding=encoding, newline="")
    except OSError as exc:
        print(f"HATA: Çıktı dosyası oluşturulamadı: {exc}", file=sys.stderr)
        sys.exit(5)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # --- Girdi toplama ---
    all_lines: list[str] = []

    if args.merge:
        file_paths = []
        if args.input:
            file_paths.append(args.input)
        file_paths.extend(args.merge)
        try:
            all_lines = merge_files(file_paths, encoding=args.encoding)
        except FileNotFoundError as exc:
            print(f"HATA: Dosya bulunamadı: {exc.filename}", file=sys.stderr)
            sys.exit(2)
        except UnicodeDecodeError as exc:
            print(
                f"HATA: Kodlama hatası. --encoding ile doğru kodlamayı belirtin.\nAyrıntı: {exc}",
                file=sys.stderr,
            )
            sys.exit(3)
    elif args.input:
        if not os.path.exists(args.input):
            print(f"HATA: Girdi dosyası bulunamadı: '{args.input}'", file=sys.stderr)
            sys.exit(2)
        try:
            with open(args.input, "r", encoding=args.encoding) as f:
                all_lines = f.readlines()
        except UnicodeDecodeError as exc:
            print(
                f"HATA: Dosya kodlaması okunamadı. --encoding seçeneğini deneyin.\nAyrıntı: {exc}",
                file=sys.stderr,
            )
            sys.exit(3)
        except OSError as exc:
            print(f"HATA: Dosya açılamadı: {exc}", file=sys.stderr)
            sys.exit(4)
    else:
        try:
            all_lines = sys.stdin.readlines()
        except UnicodeDecodeError as exc:
            print(f"HATA: Stdin kodlama hatası: {exc}", file=sys.stderr)
            sys.exit(3)

    # --- Dönüşümler ---
    lines = all_lines

    if args.filter_pattern:
        if args.exclude:
            lines = exclude_lines(lines, args.filter_pattern)
        else:
            lines = filter_lines(lines, args.filter_pattern)

    if args.normalize is not None:
        lines = normalize_lines(
            lines,
            whitespace=not args.no_whitespace,
            case=args.normalize,
            special_chars=args.remove_special,
        )

    if args.dedup:
        lines = deduplicate(lines)

    # --- Çıktı ---
    out_stream = open_output(args.output, args.encoding)
    close_out = args.output is not None and args.output != "-"

    try:
        out_stream.writelines(lines)
    finally:
        if close_out:
            out_stream.close()

    if args.output and args.output != "-":
        print(
            f"Tamamlandı: {len(lines)} satır '{args.output}' dosyasına yazıldı.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
