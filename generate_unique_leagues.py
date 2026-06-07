#!/usr/bin/env python3
"""
Gera uma lista Python com as ligas unicas de leagues.txt.
"""

from pathlib import Path
from pprint import pformat


BASE_DIR = Path(__file__).resolve().parent
SOURCE_FILE = BASE_DIR / "leagues.txt"
OUTPUT_FILE = BASE_DIR / "unique_leagues.py"


def load_unique_leagues(source_file=SOURCE_FILE):
    """Retorna as ligas sem repeticao, preservando a ordem do arquivo."""
    unique_leagues = []
    seen = set()

    with Path(source_file).open("r", encoding="utf-8") as file:
        for line in file:
            league = line.strip()
            if not league or league in seen:
                continue

            unique_leagues.append(league)
            seen.add(league)

    return unique_leagues


def write_unique_leagues(leagues, output_file=OUTPUT_FILE):
    content = (
        "# Arquivo gerado por generate_unique_leagues.py\n"
        "# Para atualizar, edite leagues.txt e rode: python3 generate_unique_leagues.py\n\n"
        f"LEAGUES = {pformat(leagues, width=100, sort_dicts=False)}\n"
    )
    Path(output_file).write_text(content, encoding="utf-8")


def main():
    leagues = load_unique_leagues()
    write_unique_leagues(leagues)
    print(f"{len(leagues)} ligas unicas salvas em {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
