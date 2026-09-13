from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_SAMOCHODY = KATALOG_DANYCH / "tabele_panelowe" / "tabela_samochody_panel.csv"
PLIK_GUS = KATALOG_PROJEKTU / "dane_surowe" / "rejestracje_i_flota" / "TRAN_1733_CTAB_20260913121634.csv"
PLIK_WYNIKI_EV = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "prognoza_liczby_ev_we_flocie_2026_2040.csv"
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu"
PLIK_WYNIKOWY = KATALOG_WYNIKOW / "prognoza_calkowitej_flota_samochodow_2025_2040.csv"
PLIK_WYKRESU = KATALOG_PROJEKTU / "wyniki" / "wykresy" / "prognoza_calkowitej_flota_samochodow_2025_2040.png"


def formatuj_tysiace(wartosc, _):
    return f"{wartosc:,.0f}".replace(",", " ")


def main() -> None:
    samochody = pd.read_csv(PLIK_SAMOCHODY)
    gus = pd.read_csv(PLIK_GUS, sep=";")
    kolumny_lat = [kolumna for kolumna in gus.columns if kolumna.startswith("samochody osobowe;")]
    historia_gus = pd.DataFrame(
        {
            "rok": [int(kolumna.split(";")[1]) for kolumna in kolumny_lat],
            "szacowana_calkowita_flota_samochodow_osobowych": [
                float(gus.loc[0, kolumna]) for kolumna in kolumny_lat
            ],
        }
    )
    polska = samochody[samochody["panstwo"] == "Polska"].dropna(
        subset=["rok", "szacowana_liczba_wszystkich_nowych_rejestracji"]
    )
    polska = polska[polska["rok"].between(2020, 2024)]
    wspolczynniki = np.polyfit(
        polska["rok"], polska["szacowana_liczba_wszystkich_nowych_rejestracji"], 1
    )
    lata = np.arange(2025, 2041)
    nowe_rejestracje = np.maximum(np.polyval(wspolczynniki, lata), 0)
    flota_2024 = float(historia_gus.loc[historia_gus["rok"] == 2024, "szacowana_calkowita_flota_samochodow_osobowych"].iloc[0])
    wynik = pd.DataFrame(
        {
            "rok": np.r_[2024, lata],
            "szacowana_calkowita_flota_samochodow_osobowych": np.r_[flota_2024, flota_2024 + np.cumsum(nowe_rejestracje)],
            "szacowane_wszystkie_nowe_rejestracje": np.r_[np.nan, nowe_rejestracje],
            "metoda": "skumulowana_bez_wycofan",
        }
    )
    KATALOG_WYNIKOW.mkdir(parents=True, exist_ok=True)
    wynik.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")

    historia = historia_gus.sort_values("rok")

    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.plot(
        historia["rok"],
        historia["szacowana_calkowita_flota_samochodow_osobowych"],
        "o-",
        color="#64748b",
        linewidth=2.2,
        label="Dane historyczne",
    )
    ax.plot(
        wynik["rok"],
        wynik["szacowana_calkowita_flota_samochodow_osobowych"],
        "o-",
        color="#334155",
        linewidth=2.5,
        label="Prognoza skumulowana",
    )
    ax.axvline(2024, color="#7c3aed", linestyle="--", linewidth=1.8, label="Czyszczenie CEPiK / punkt bazowy")
    ax.axvspan(2024.5, 2040.5, color="#334155", alpha=0.04)
    ax.set_title("Całkowita liczba samochodów osobowych w Polsce, dane GUS i prognoza")
    ax.set_xlabel("Rok")
    ax.set_ylabel("Liczba samochodów")
    ax.set_xlim(1999, 2040.5)
    ax.set_xticks(range(2000, 2041, 2))
    ax.yaxis.set_major_formatter(FuncFormatter(formatuj_tysiace))
    ax.grid(axis="y", linestyle=":", alpha=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(PLIK_WYKRESU, dpi=220)
    plt.close(fig)
    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(f"Zapisano wykres: {PLIK_WYKRESU}")
    print(wynik[wynik["rok"].isin([2024, 2030, 2035, 2040])].to_string(index=False))


if __name__ == "__main__":
    main()
