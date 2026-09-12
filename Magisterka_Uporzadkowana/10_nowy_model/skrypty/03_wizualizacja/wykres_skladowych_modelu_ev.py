from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_PANELU = KATALOG_DANYCH / "panele_analityczne" / "panel_analityczny_rozszerzony.csv"
PLIK_SCENARIUSZA = KATALOG_DANYCH / "scenariusze" / "scenariusz_ev_2026_2040.csv"
PLIK_PROGNOZY_EV = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "prognoza_udzialu_ev_z_ladowarkami_2026_2040.csv"
PLIK_WYKRESU = KATALOG_PROJEKTU / "wyniki" / "wykresy" / "zmiany_zmiennych_wejsciowych_modelu_ev_2020_2040.png"


def main() -> None:
    panel = pd.read_csv(PLIK_PANELU)
    panel = panel[panel["panstwo"] == "Polska"].copy()
    panel = panel[panel["rok"].between(2020, 2025)]
    scenariusz = pd.read_csv(PLIK_SCENARIUSZA)
    prognoza_ev = pd.read_csv(PLIK_PROGNOZY_EV)
    prognoza_ev = prognoza_ev[prognoza_ev["panstwo"] == "Polska"]

    historia = panel[
        [
            "rok",
            "pkb_per_capita_pps",
            "relacja_kosztu_ev_do_benzyny",
            "punkty_ladowania_na_100_tys_mieszkancow",
        ]
    ]
    przyszlosc = scenariusz.merge(
        prognoza_ev[["panstwo", "rok", "prognozowany_udzial_ev_procent"]],
        on=["panstwo", "rok"],
        how="inner",
    )
    przyszlosc = przyszlosc[
        [
            "rok",
            "pkb_per_capita_pps",
            "relacja_kosztu_ev_do_benzyny",
            "punkty_ladowania_na_100_tys_mieszkancow",
        ]
    ]
    dane = pd.concat([historia, przyszlosc], ignore_index=True).sort_values("rok")

    kolumny = {
        "pkb_per_capita_pps": "PKB per capita PPS",
        "relacja_kosztu_ev_do_benzyny": "Relacja kosztu EV/benzyna",
        "punkty_ladowania_na_100_tys_mieszkancow": "Ładowarki na 100 tys. mieszkańców",
    }
    indeks = dane.copy()
    for kolumna in kolumny:
        wartosc_2025 = indeks.loc[indeks["rok"] == 2025, kolumna].iloc[0]
        indeks[kolumna] = indeks[kolumna] / wartosc_2025 * 100

    fig, ax = plt.subplots(figsize=(13, 7.5))
    kolory = ["#2563eb", "#dc2626", "#16a34a", "#176b87"]
    style = ["-", "--", "-", "-"]
    for (kolumna, etykieta), kolor, linia in zip(kolumny.items(), kolory, style):
        ax.plot(
            indeks["rok"],
            indeks[kolumna],
            marker="o",
            linewidth=2.2,
            linestyle=linia,
            color=kolor,
            label=etykieta,
        )
    ax.axvspan(2025.5, 2040.5, color="#176b87", alpha=0.04)
    ax.axvline(2035, color="#7c3aed", linestyle="--", linewidth=1.7, label="Rok 2035")
    ax.axhline(100, color="#9ca3af", linewidth=1, alpha=0.8)
    ax.set_title("Zmiana składowych modelu EV względem 2025 roku")
    ax.set_xlabel("Rok")
    ax.set_ylabel("Indeks, 2025 = 100")
    ax.set_xlim(2020, 2040.5)
    ax.set_xticks(range(2020, 2041, 2))
    ax.grid(axis="y", linestyle=":", alpha=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", framealpha=0.95)
    fig.tight_layout()
    fig.savefig(PLIK_WYKRESU, dpi=220)
    plt.close(fig)
    print(f"Zapisano wykres: {PLIK_WYKRESU}")


if __name__ == "__main__":
    main()
