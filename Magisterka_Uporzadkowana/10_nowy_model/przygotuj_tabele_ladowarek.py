from pathlib import Path

import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parent
KATALOG_SUROWY = KATALOG_PROJEKTU / "dane_surowe" / "ladowarki"
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_WYNIKOWY = KATALOG_WYNIKOW / "tabela_ladowarki_panel.csv"
PLIK_LUDNOSCI = KATALOG_WYNIKOW / "tabela_ludnosc_panel.csv"
LATA = range(2020, 2026)


def pobierz_plik(katalog: Path) -> Path:
    pliki = sorted(path for path in katalog.iterdir() if path.is_file())
    if len(pliki) != 1:
        raise ValueError(
            f"Folder {katalog} powinien zawierać dokładnie jeden plik, "
            f"a zawiera {len(pliki)}."
        )
    return pliki[0]


def suma_kategorii_mocy(dane: pd.DataFrame) -> pd.DataFrame:
    dane = dane.copy()
    dane["rok"] = pd.to_numeric(dane.iloc[:, 0], errors="coerce")
    kolumny_wartosci = list(dane.columns[1:-1])
    wartosci = dane[kolumny_wartosci].apply(pd.to_numeric, errors="coerce")
    dane["liczba_punktow"] = wartosci.sum(axis=1, min_count=1)
    return dane[dane["rok"].isin(LATA)][["rok", "liczba_punktow"]]


def przygotuj_wszystkie_punkty(dane: pd.DataFrame) -> pd.DataFrame:
    dane = dane.copy()
    dane["okres"] = dane.iloc[:, 0].astype(str).str.strip()
    dane["rok"] = pd.to_numeric(dane["okres"].str.extract(r"^(\d{4})")[0], errors="coerce")
    dane = dane[dane["rok"].isin(LATA) & dane["okres"].str.endswith("Q4")]
    wartosci = dane.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
    dane["punkty_ac"] = wartosci.iloc[:, 0]
    dane["punkty_dc"] = wartosci.iloc[:, 1]
    dane["punkty_ladowania_razem"] = dane["punkty_ac"] + dane["punkty_dc"]
    return dane[["rok", "punkty_ladowania_razem"]]


def przygotuj_dane_panstwa(katalog_panstwa: Path) -> pd.DataFrame:
    plik_razem = pobierz_plik(katalog_panstwa / "01_wszystkie_punkty")
    plik_ac = pobierz_plik(katalog_panstwa / "02_punkty_ac")
    plik_dc = pobierz_plik(katalog_panstwa / "03_punkty_dc")

    razem = przygotuj_wszystkie_punkty(pd.read_csv(plik_razem))
    ac = suma_kategorii_mocy(pd.read_csv(plik_ac)).rename(columns={"liczba_punktow": "punkty_ac"})
    dc = suma_kategorii_mocy(pd.read_csv(plik_dc)).rename(columns={"liczba_punktow": "punkty_dc"})

    wynik = razem.merge(ac, on="rok", how="outer").merge(dc, on="rok", how="outer")
    wynik.insert(0, "panstwo", katalog_panstwa.name)
    return wynik.sort_values("rok")


def dodaj_przeliczenie_na_100_tys_mieszkancow(tabela: pd.DataFrame) -> pd.DataFrame:
    ludnosc = pd.read_csv(PLIK_LUDNOSCI)
    ludnosc = ludnosc[["panstwo", "rok", "ludnosc"]]
    tabela = tabela.merge(ludnosc, on=["panstwo", "rok"], how="left", validate="one_to_one")
    tabela["punkty_ladowania_na_100_tys_mieszkancow"] = (
        tabela["punkty_ladowania_razem"] / tabela["ludnosc"] * 100_000
    )
    return tabela


def main() -> None:
    panstwa = sorted(path for path in KATALOG_SUROWY.iterdir() if path.is_dir())
    tabela = pd.concat(
        [przygotuj_dane_panstwa(panstwo) for panstwo in panstwa],
        ignore_index=True,
    )
    tabela = dodaj_przeliczenie_na_100_tys_mieszkancow(tabela)
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