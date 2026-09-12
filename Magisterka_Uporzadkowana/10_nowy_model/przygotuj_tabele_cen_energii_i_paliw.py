from pathlib import Path

import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parent
KATALOG_SUROWY = KATALOG_PROJEKTU / "dane_surowe" / "ceny_energii_i_paliw"
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_PRADU = KATALOG_SUROWY / "nrg_pc_204_linear.csv"
PLIK_PALIW = KATALOG_SUROWY / "ceny_paliw_biuletyn_olejowy.xlsx"
PLIK_WYNIKOWY = KATALOG_WYNIKOW / "tabela_ceny_energii_i_paliw_panel.csv"
PLIK_ZALOZEN = KATALOG_WYNIKOW / "zalozenia_zuzycia.csv"

MAPA_PANSTW = {
    "AT": "Austria", "BE": "Belgia", "BG": "Bułgaria", "CY": "Cypr",
    "CZ": "Czechy", "DE": "Niemcy", "DK": "Dania", "EE": "Estonia",
    "ES": "Hiszpania", "FI": "Finlandia", "FR": "Francja", "GR": "Grecja",
    "HR": "Chorwacja", "HU": "Węgry", "IE": "Irlandia", "IS": "Islandia",
    "IT": "Włochy", "LT": "Litwa", "LU": "Luksemburg", "LV": "Łotwa",
    "MT": "Malta", "NL": "Holandia", "NO": "Norwegia", "PL": "Polska",
    "PT": "Portugalia", "RO": "Rumunia", "SE": "Szwecja", "SI": "Słowenia",
    "SK": "Słowacja", "TR": "Turcja", "UK": "Wielka_Brytania",
}

MAPA_EUROSTAT = {
    "Austria": "Austria", "Belgium": "Belgia", "Bulgaria": "Bułgaria",
    "Croatia": "Chorwacja", "Cyprus": "Cypr", "Czechia": "Czechy",
    "Denmark": "Dania", "Estonia": "Estonia", "Finland": "Finlandia",
    "France": "Francja", "Germany": "Niemcy", "Greece": "Grecja",
    "Hungary": "Węgry", "Iceland": "Islandia", "Ireland": "Irlandia",
    "Italy": "Włochy", "Lithuania": "Litwa", "Luxembourg": "Luksemburg",
    "Latvia": "Łotwa", "Malta": "Malta", "Netherlands": "Holandia",
    "Norway": "Norwegia", "Poland": "Polska", "Portugal": "Portugalia",
    "Romania": "Rumunia", "Slovakia": "Słowacja", "Slovenia": "Słowenia",
    "Spain": "Hiszpania", "Sweden": "Szwecja", "Türkiye": "Turcja",
    "United Kingdom": "Wielka_Brytania",
}


def przygotuj_prad() -> pd.DataFrame:
    dane = pd.read_csv(PLIK_PRADU)
    dane = dane[
        (dane["nrg_cons"] == "Consumption from 2 500 kWh to 4 999 kWh - band DC")
        & (dane["tax"] == "All taxes and levies included")
        & (dane["currency"] == "Euro")
        & dane["geo"].isin(MAPA_EUROSTAT)
    ].copy()
    dane["rok"] = dane["TIME_PERIOD"].str.extract(r"^(\d{4})")[0].astype(int)
    dane["panstwo"] = dane["geo"].map(MAPA_EUROSTAT)
    return (
        dane[dane["rok"].between(2008, 2025)]
        .groupby(["panstwo", "rok"], as_index=False)["OBS_VALUE"]
        .mean()
        .rename(columns={"OBS_VALUE": "cena_energii_eur_kwh"})
    )


def przygotuj_paliwa() -> pd.DataFrame:
    surowe = pd.read_excel(PLIK_PALIW, sheet_name="Prices with taxes", header=None)
    naglowki = surowe.iloc[0].tolist()
    kolumny = {str(wartosc): indeks for indeks, wartosc in enumerate(naglowki) if pd.notna(wartosc)}
    daty = pd.to_datetime(surowe.iloc[3:, 0], errors="coerce")
    wynik = []
    for kod, panstwo in MAPA_PANSTW.items():
        benzyna = kolumny.get(f"{kod}_price_with_tax_euro95")
        diesel = kolumny.get(f"{kod}_price_with_tax_diesel")
        if benzyna is None or diesel is None:
            continue
        ramka = pd.DataFrame({
            "data": daty,
            "cena_benzyny": pd.to_numeric(surowe.iloc[3:, benzyna], errors="coerce"),
            "cena_diesla": pd.to_numeric(surowe.iloc[3:, diesel], errors="coerce"),
        }).dropna(subset=["data"])
        ramka["rok"] = ramka["data"].dt.year
        ramka = ramka[ramka["rok"].between(2008, 2025)]
        rocznie = ramka.groupby("rok", as_index=False)[["cena_benzyny", "cena_diesla"]].mean()
        rocznie["panstwo"] = panstwo
        rocznie["cena_benzyny_eur_litr"] = rocznie["cena_benzyny"] / 1000
        rocznie["cena_diesla_eur_litr"] = rocznie["cena_diesla"] / 1000
        wynik.append(rocznie[["panstwo", "rok", "cena_benzyny_eur_litr", "cena_diesla_eur_litr"]])
    return pd.concat(wynik, ignore_index=True)


def dodaj_koszty_przejazdu(tabela: pd.DataFrame) -> pd.DataFrame:
    zalozenia = pd.read_csv(PLIK_ZALOZEN).set_index("typ_pojazdu")
    zuzycie_ev = zalozenia.loc["bev", "zuzycie_na_100_km"]
    zuzycie_benzyna = zalozenia.loc["samochod_benzynowy", "zuzycie_na_100_km"]
    zuzycie_diesel = zalozenia.loc["samochod_diesla", "zuzycie_na_100_km"]

    tabela["koszt_100_km_ev"] = tabela["cena_energii_eur_kwh"] * zuzycie_ev
    tabela["koszt_100_km_benzyna"] = (
        tabela["cena_benzyny_eur_litr"] * zuzycie_benzyna
    )
    tabela["koszt_100_km_diesel"] = tabela["cena_diesla_eur_litr"] * zuzycie_diesel
    tabela["relacja_kosztu_ev_do_benzyny"] = (
        tabela["koszt_100_km_ev"] / tabela["koszt_100_km_benzyna"]
    )
    tabela["relacja_kosztu_ev_do_diesla"] = (
        tabela["koszt_100_km_ev"] / tabela["koszt_100_km_diesel"]
    )
    return tabela


def main() -> None:
    tabela = przygotuj_prad().merge(
        przygotuj_paliwa(), on=["panstwo", "rok"], how="outer"
    )
    tabela = dodaj_koszty_przejazdu(tabela)
    tabela = tabela.sort_values(["panstwo", "rok"]).reset_index(drop=True)
    KATALOG_WYNIKOW.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")
    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(f"Państwa: {tabela['panstwo'].nunique()}")
    print(f"Obserwacje: {len(tabela)}")
    print(f"Lata: {tabela['rok'].min()}–{tabela['rok'].max()}")
    print("Braki według kolumn:")
    print(tabela.isna().sum().to_string())


if __name__ == "__main__":
    main()