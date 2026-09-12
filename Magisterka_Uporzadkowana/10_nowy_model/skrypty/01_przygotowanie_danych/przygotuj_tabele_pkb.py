from pathlib import Path

import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
PLIK_SUROWY = KATALOG_PROJEKTU / "dane_surowe" / "pkb" / "nama_10_pc_linear.csv"
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "dane_przetworzone" / "tabele_panelowe"
PLIK_WYNIKOWY = KATALOG_WYNIKOW / "tabela_pkb_panel.csv"

NAZWA_JEDNOSTKI = (
    "Current prices, purchasing power standard (PPS, EU27 from 2020) per capita"
)
NAZWA_POZYCJI = "Gross domestic product at market prices"

MAPA_PANSTW = {
    "Austria": "Austria",
    "Belgium": "Belgia",
    "Bulgaria": "Bułgaria",
    "Croatia": "Chorwacja",
    "Cyprus": "Cypr",
    "Czechia": "Czechy",
    "Denmark": "Dania",
    "Estonia": "Estonia",
    "Finland": "Finlandia",
    "France": "Francja",
    "Germany": "Niemcy",
    "Greece": "Grecja",
    "Hungary": "Węgry",
    "Iceland": "Islandia",
    "Ireland": "Irlandia",
    "Italy": "Włochy",
    "Lithuania": "Litwa",
    "Luxembourg": "Luksemburg",
    "Latvia": "Łotwa",
    "Malta": "Malta",
    "Netherlands": "Holandia",
    "Norway": "Norwegia",
    "Poland": "Polska",
    "Portugal": "Portugalia",
    "Romania": "Rumunia",
    "Slovakia": "Słowacja",
    "Slovenia": "Słowenia",
    "Spain": "Hiszpania",
    "Sweden": "Szwecja",
    "Türkiye": "Turcja",
    "United Kingdom": "Wielka_Brytania",
}


def main() -> None:
    dane = pd.read_csv(PLIK_SUROWY)
    tabela = dane[
        (dane["na_item"] == NAZWA_POZYCJI)
        & (dane["unit"] == NAZWA_JEDNOSTKI)
        & dane["geo"].isin(MAPA_PANSTW)
        & dane["TIME_PERIOD"].between(2008, 2025)
    ][["geo", "TIME_PERIOD", "OBS_VALUE"]].copy()

    tabela = tabela.rename(
        columns={
            "geo": "panstwo",
            "TIME_PERIOD": "rok",
            "OBS_VALUE": "pkb_per_capita_pps",
        }
    )
    tabela["panstwo"] = tabela["panstwo"].map(MAPA_PANSTW)
    tabela["rok"] = tabela["rok"].astype(int)
    tabela = tabela.sort_values(["panstwo", "rok"]).reset_index(drop=True)

    KATALOG_WYNIKOW.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")

    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(f"Państwa: {tabela['panstwo'].nunique()}")
    print(f"Obserwacje: {len(tabela)}")
    print(f"Lata: {tabela['rok'].min()}–{tabela['rok'].max()}")
    print(f"Braki wartości: {tabela['pkb_per_capita_pps'].isna().sum()}")


if __name__ == "__main__":
    main()