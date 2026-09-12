from pathlib import Path

import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parent
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_WYNIKOWY = KATALOG_DANYCH / "panel_analityczny_2020_2025.csv"

PLIKI = {
    "samochody": KATALOG_DANYCH / "tabela_samochody_panel.csv",
    "pkb": KATALOG_DANYCH / "tabela_pkb_panel.csv",
    "ceny": KATALOG_DANYCH / "tabela_ceny_energii_i_paliw_panel.csv",
    "ladowarki": KATALOG_DANYCH / "tabela_ladowarki_panel.csv",
    "ludnosc": KATALOG_DANYCH / "tabela_ludnosc_panel.csv",
}


def main() -> None:
    panel = pd.read_csv(PLIKI["pkb"])
    panel = panel[panel["rok"].between(2020, 2025)].copy()

    for nazwa in ["samochody", "ceny", "ladowarki", "ludnosc"]:
        dane = pd.read_csv(PLIKI[nazwa])
        dane = dane[dane["rok"].between(2020, 2025)]
        panel = panel.merge(dane, on=["panstwo", "rok"], how="left", validate="one_to_one")

    panel["punkty_ladowania_na_100_tys_mieszkancow"] = (
        panel["punkty_ladowania_razem"] / panel["ludnosc"] * 100_000
    )
    panel = panel.sort_values(["panstwo", "rok"]).reset_index(drop=True)
    panel.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")

    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(f"Państwa: {panel['panstwo'].nunique()}")
    print(f"Obserwacje: {len(panel)}")
    print(f"Lata: {panel['rok'].min()}–{panel['rok'].max()}")
    print("Braki według kolumn:")
    print(panel.isna().sum()[panel.isna().sum().gt(0)].to_string())


if __name__ == "__main__":
    main()