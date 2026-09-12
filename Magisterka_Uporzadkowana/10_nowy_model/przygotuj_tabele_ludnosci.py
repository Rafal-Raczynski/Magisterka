from pathlib import Path

import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parent
PLIK_SUROWY = KATALOG_PROJEKTU / "dane_surowe" / "ludnosc" / "tps00001_linear.csv"
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_WYNIKOWY = KATALOG_WYNIKOW / "tabela_ludnosc_panel.csv"

MAPA_PANSTW = {
    "Austria": "Austria", "Belgium": "Belgia", "Bulgaria": "Bułgaria",
    "Croatia": "Chorwacja", "Cyprus": "Cypr", "Czechia": "Czechy",
    "Denmark": "Dania", "Estonia": "Estonia", "Finland": "Finlandia",
    "France": "Francja", "Germany": "Niemcy", "Greece": "Grecja",
    "Hungary": "Węgry", "Iceland": "Islandia", "Ireland": "Irlandia",
    "Italy": "Włochy", "Liechtenstein": "Liechtenstein", "Lithuania": "Litwa",
    "Luxembourg": "Luksemburg", "Latvia": "Łotwa", "Malta": "Malta",
    "Netherlands": "Holandia", "Norway": "Norwegia", "Poland": "Polska",
    "Portugal": "Portugalia", "Romania": "Rumunia", "Slovakia": "Słowacja",
    "Slovenia": "Słowenia", "Spain": "Hiszpania", "Sweden": "Szwecja",
    "Switzerland": "Szwajcaria", "Türkiye": "Turcja",
    "United Kingdom": "Wielka_Brytania",
}


def main() -> None:
    dane = pd.read_csv(PLIK_SUROWY)
    tabela = dane[
        dane["geo"].isin(MAPA_PANSTW)
        & dane["TIME_PERIOD"].between(2020, 2025)
    ][["geo", "TIME_PERIOD", "OBS_VALUE"]].copy()
    tabela = tabela.rename(
        columns={"geo": "panstwo", "TIME_PERIOD": "rok", "OBS_VALUE": "ludnosc"}
    )
    tabela["panstwo"] = tabela["panstwo"].map(MAPA_PANSTW)
    tabela["rok"] = tabela["rok"].astype(int)
    tabela["ludnosc"] = tabela["ludnosc"].astype(int)
    tabela = tabela.sort_values(["panstwo", "rok"]).reset_index(drop=True)

    KATALOG_WYNIKOW.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")
    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(f"Państwa: {tabela['panstwo'].nunique()}")
    print(f"Obserwacje: {len(tabela)}")
    print(f"Lata: {tabela['rok'].min()}–{tabela['rok'].max()}")
    print(f"Braki ludności: {tabela['ludnosc'].isna().sum()}")


if __name__ == "__main__":
    main()