from pathlib import Path

import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parent
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_SAMOCHODY = KATALOG_DANYCH / "tabela_samochody_panel.csv"
PLIK_PKB = KATALOG_DANYCH / "tabela_pkb_panel.csv"
PLIK_CENY = KATALOG_DANYCH / "tabela_ceny_energii_i_paliw_panel.csv"
PLIK_LADOWARKI = KATALOG_DANYCH / "tabela_ladowarki_panel.csv"
PLIK_PODSTAWOWY = KATALOG_DANYCH / "panel_analityczny_podstawowy.csv"
PLIK_ROZSZERZONY = KATALOG_DANYCH / "panel_analityczny_rozszerzony.csv"

KLUCZE = ["panstwo", "rok"]


def dodaj_zmienne_polityki_ue(tabela: pd.DataFrame) -> pd.DataFrame:
    tabela = tabela.copy()
    tabela["polityka_ue_etap"] = pd.cut(
        tabela["rok"],
        bins=[-float("inf"), 2019, 2024, 2034, float("inf")],
        labels=[0, 1, 2, 3],
    ).astype(int)
    tabela["po_2035"] = (tabela["rok"] >= 2035).astype(int)
    return tabela


def wczytaj(sciezka: Path) -> pd.DataFrame:
    dane = pd.read_csv(sciezka)
    if dane.duplicated(KLUCZE).any():
        raise ValueError(f"Powtórzone klucze panstwo-rok w pliku: {sciezka}")
    return dane


def scal_panele() -> tuple[pd.DataFrame, pd.DataFrame]:
    samochody = wczytaj(PLIK_SAMOCHODY)
    pkb = wczytaj(PLIK_PKB)
    ceny = wczytaj(PLIK_CENY)
    ladowarki = wczytaj(PLIK_LADOWARKI)

    podstawowy = samochody.merge(pkb, on=KLUCZE, how="inner", validate="one_to_one")
    podstawowy = podstawowy.merge(ceny, on=KLUCZE, how="inner", validate="one_to_one")
    podstawowy = dodaj_zmienne_polityki_ue(podstawowy)
    podstawowy = podstawowy.sort_values(KLUCZE).reset_index(drop=True)

    rozszerzony = podstawowy.merge(
        ladowarki, on=KLUCZE, how="inner", validate="one_to_one"
    )
    rozszerzony = rozszerzony.sort_values(KLUCZE).reset_index(drop=True)
    return podstawowy, rozszerzony


def wypisz_podsumowanie(nazwa: str, tabela: pd.DataFrame) -> None:
    print(f"--- {nazwa} ---")
    print(f"Państwa: {tabela['panstwo'].nunique()}")
    print(f"Obserwacje: {len(tabela)}")
    print(f"Lata: {tabela['rok'].min()}–{tabela['rok'].max()}")
    print(f"Kolumny: {len(tabela.columns)}")
    print("Braki według kolumn:")
    print(tabela.isna().sum()[lambda seria: seria > 0].to_string())


def main() -> None:
    podstawowy, rozszerzony = scal_panele()
    podstawowy.to_csv(PLIK_PODSTAWOWY, index=False, encoding="utf-8-sig")
    rozszerzony.to_csv(PLIK_ROZSZERZONY, index=False, encoding="utf-8-sig")
    print(f"Zapisano: {PLIK_PODSTAWOWY}")
    print(f"Zapisano: {PLIK_ROZSZERZONY}")
    wypisz_podsumowanie("PANEL PODSTAWOWY", podstawowy)
    wypisz_podsumowanie("PANEL ROZSZERZONY", rozszerzony)


if __name__ == "__main__":
    main()