from pathlib import Path

import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_SUROWY = KATALOG_PROJEKTU / "dane_surowe" / "samochody"
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "dane_przetworzone" / "tabele_panelowe"
PLIK_WYNIKOWY = KATALOG_WYNIKOW / "tabela_samochody_panel.csv"

KATEGORIE = {
    "01_calkowita_flota": "flota",
    "02_procent_floty": "procent_floty",
    "03_nowe_rejestracje": "rejestracje",
    "04_procent_nowych_rejestracji": "procent_rejestracji",
}
NAPEDY = ("bev", "phev", "h2", "lpg", "cng", "lng")
NAZWY_NAPEDOW = {
    "bev": "bev",
    "phev": "phev",
    "h2": "h2",
    "lpg": "lpg",
    "cng": "cng",
    "lng": "lng",
}


def wczytaj_plik(sciezka: Path) -> pd.DataFrame:
    dane = pd.read_csv(sciezka)
    dane.columns = [str(kolumna).strip().lower() for kolumna in dane.columns]
    dane = dane.rename(columns={"category": "rok"})
    dane["rok"] = pd.to_numeric(dane["rok"], errors="coerce")
    dane = dane.dropna(subset=["rok"]).copy()
    dane["rok"] = dane["rok"].astype(int)

    for naped in NAPEDY:
        if naped not in dane.columns:
            dane[naped] = pd.NA
        dane[naped] = pd.to_numeric(dane[naped], errors="coerce")

    return dane[["rok", *NAPEDY]]


def pobierz_jeden_plik(katalog: Path) -> Path:
    pliki = sorted(katalog.glob("*"))
    pliki = [plik for plik in pliki if plik.is_file()]
    if len(pliki) != 1:
        raise ValueError(
            f"Folder {katalog} powinien zawierać dokładnie jeden plik, "
            f"a zawiera {len(pliki)}."
        )
    return pliki[0]


def przygotuj_dane_panstwa(katalog_panstwa: Path) -> pd.DataFrame:
    ramki = {}
    for folder, nazwa in KATEGORIE.items():
        sciezka_folderu = katalog_panstwa / folder
        if not sciezka_folderu.is_dir():
            raise FileNotFoundError(f"Brak folderu: {sciezka_folderu}")
        ramki[nazwa] = wczytaj_plik(pobierz_jeden_plik(sciezka_folderu))

    wspolne_lata = set(ramki["flota"]["rok"])
    wspolne_lata &= set(ramki["procent_floty"]["rok"])
    wspolne_lata &= set(ramki["rejestracje"]["rok"])
    wspolne_lata &= set(ramki["procent_rejestracji"]["rok"])
    wspolne_lata = sorted(wspolne_lata)

    wynik = pd.DataFrame({"rok": wspolne_lata})
    for nazwa, ramka in ramki.items():
        ramka = ramka[ramka["rok"].isin(wspolne_lata)].copy()
        ramka = ramka.rename(
            columns={naped: f"{naped}_{nazwa}" for naped in NAPEDY}
        )
        wynik = wynik.merge(ramka, on="rok", how="left", validate="one_to_one")

    wynik.insert(0, "panstwo", katalog_panstwa.name)

    wynik["ev_flota"] = wynik["bev_flota"] + wynik["phev_flota"]
    wynik["ev_procent_floty"] = (
        wynik["bev_procent_floty"] + wynik["phev_procent_floty"]
    )
    wynik["ev_rejestracje"] = (
        wynik["bev_rejestracje"] + wynik["phev_rejestracje"]
    )
    wynik["ev_procent_rejestracji"] = (
        wynik["bev_procent_rejestracji"]
        + wynik["phev_procent_rejestracji"]
    )

    nazwy_kolumn = {"ev_flota": "liczba_ev_we_flocie"}
    nazwy_kolumn["ev_procent_floty"] = "procent_ev_we_flocie"
    nazwy_kolumn["ev_rejestracje"] = "liczba_ev_w_nowych_rejestracjach"
    nazwy_kolumn["ev_procent_rejestracji"] = (
        "procent_ev_w_nowych_rejestracjach"
    )
    for naped, nazwa in NAZWY_NAPEDOW.items():
        nazwy_kolumn[f"{naped}_flota"] = f"liczba_{nazwa}_we_flocie"
        nazwy_kolumn[f"{naped}_procent_floty"] = f"procent_{nazwa}_we_flocie"
        nazwy_kolumn[f"{naped}_rejestracje"] = (
            f"liczba_{nazwa}_w_nowych_rejestracjach"
        )
        nazwy_kolumn[f"{naped}_procent_rejestracji"] = (
            f"procent_{nazwa}_w_nowych_rejestracjach"
        )

    wynik = wynik.rename(columns=nazwy_kolumn)
    kolumny_analityczne = [
        "panstwo",
        "rok",
        "liczba_bev_we_flocie",
        "liczba_phev_we_flocie",
        "procent_bev_we_flocie",
        "procent_phev_we_flocie",
        "liczba_bev_w_nowych_rejestracjach",
        "liczba_phev_w_nowych_rejestracjach",
        "procent_bev_w_nowych_rejestracjach",
        "procent_phev_w_nowych_rejestracjach",
        "liczba_ev_we_flocie",
        "procent_ev_we_flocie",
        "liczba_ev_w_nowych_rejestracjach",
        "procent_ev_w_nowych_rejestracjach",
    ]

    return wynik[kolumny_analityczne]


def main() -> None:
    panstwa = sorted(katalog for katalog in KATALOG_SUROWY.iterdir() if katalog.is_dir())
    if not panstwa:
        raise FileNotFoundError(f"Nie znaleziono państw w {KATALOG_SUROWY}")

    tabela = pd.concat(
        [przygotuj_dane_panstwa(panstwo) for panstwo in panstwa],
        ignore_index=True,
    )
    tabela = tabela.sort_values(["panstwo", "rok"]).reset_index(drop=True)
    KATALOG_WYNIKOW.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")

    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(f"Państwa: {tabela['panstwo'].nunique()}")
    print(f"Obserwacje: {len(tabela)}")
    print(f"Lata: {tabela['rok'].min()}–{tabela['rok'].max()}")
    print(f"Kolumny: {len(tabela.columns)}")


if __name__ == "__main__":
    main()