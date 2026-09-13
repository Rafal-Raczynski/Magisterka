from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_FLOTA_EV = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "prognoza_liczby_ev_rocznie_scenariusze_2025_2040.csv"
PLIK_ZALOZEN = KATALOG_DANYCH / "scenariusze" / "zalozenia_zuzycia_energii_ev.csv"
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "wyniki" / "zuzycie_energii"
PLIK_WYNIKOWY = KATALOG_WYNIKOW / "prognoza_zuzycia_energii_ev_2025_2040.csv"
PLIK_WYKRESU = KATALOG_PROJEKTU / "wyniki" / "wykresy" / "prognoza_zuzycia_energii_ev_2025_2040.png"


def formatuj_twh(wartosc, _):
    return f"{wartosc:.1f}"


def main() -> None:
    flota = pd.read_csv(PLIK_FLOTA_EV)
    zalozenia = pd.read_csv(PLIK_ZALOZEN).set_index("parametr")["wartosc"]
    przebieg = float(zalozenia["przebieg_roczny_na_samochod"])
    zuzycie = float(zalozenia["zuzycie_energii_ev"])
    straty = float(zalozenia["straty_ladowania"])
    kwh_na_samochod = przebieg / 100 * zuzycie * (1 + straty)

    scenariusze = ["realistyczny", "umiarkowanie_optymistyczny", "optymistyczny"]
    wynik = flota[["rok"]].copy()
    for scenariusz in scenariusze:
        wynik[f"liczba_ev_{scenariusz}"] = flota[scenariusz]
        wynik[f"zuzycie_energii_twh_{scenariusz}"] = (
            flota[scenariusz] * kwh_na_samochod / 1_000_000_000
        )

    wynik["przebieg_roczny_km"] = przebieg
    wynik["zuzycie_ev_kwh_na_100_km"] = zuzycie
    wynik["straty_ladowania"] = straty
    wynik["zuzycie_jednego_ev_kwh_rocznie"] = kwh_na_samochod
    KATALOG_WYNIKOW.mkdir(parents=True, exist_ok=True)
    wynik.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(13, 7.5))
    kolory = {"realistyczny": "#176b87", "umiarkowanie_optymistyczny": "#d97706", "optymistyczny": "#15803d"}
    etykiety = {"realistyczny": "Realistyczny", "umiarkowanie_optymistyczny": "Umiarkowanie optymistyczny", "optymistyczny": "Optymistyczny"}
    for scenariusz in scenariusze:
        ax.plot(
            wynik["rok"],
            wynik[f"zuzycie_energii_twh_{scenariusz}"],
            "o-",
            linewidth=2.5,
            color=kolory[scenariusz],
            label=etykiety[scenariusz],
        )
    ax.axvline(2025, color="#7c3aed", linestyle="--", linewidth=1.8, label="Punkt bazowy 2025")
    ax.set_title("Szacowane dodatkowe zużycie energii przez samochody EV w Polsce")
    ax.set_xlabel("Rok")
    ax.set_ylabel("Zużycie energii (TWh rocznie)")
    ax.set_xlim(2025, 2040.5)
    ax.yaxis.set_major_formatter(FuncFormatter(formatuj_twh))
    ax.grid(axis="y", linestyle=":", alpha=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(PLIK_WYKRESU, dpi=220)
    plt.close(fig)

    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(f"Zapisano wykres: {PLIK_WYKRESU}")
    print(f"Zużycie jednego EV rocznie: {kwh_na_samochod:.0f} kWh")
    print(wynik[wynik["rok"].isin([2025, 2030, 2035, 2040])].to_string(index=False))


if __name__ == "__main__":
    main()
