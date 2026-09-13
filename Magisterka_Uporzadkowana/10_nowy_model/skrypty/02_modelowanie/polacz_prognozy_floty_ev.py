from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu"
PLIK_EV = KATALOG_WYNIKOW / "prognoza_liczby_ev_rocznie_scenariusze_2025_2040.csv"
PLIK_SAMOCHODY = KATALOG_DANYCH / "tabele_panelowe" / "tabela_samochody_panel.csv"
PLIK_FLOTA = KATALOG_WYNIKOW / "prognoza_calkowitej_flota_samochodow_2025_2040.csv"
PLIK_WYNIKOWY = KATALOG_WYNIKOW / "prognoza_ev_i_calkowitej_floty_2024_2040.csv"
PLIK_WYKRESU = KATALOG_PROJEKTU / "wyniki" / "wykresy" / "prognoza_ev_i_udzialu_we_flocie_2024_2040.png"


def formatuj_tysiace(wartosc, _):
    return f"{wartosc:,.0f}".replace(",", " ")


def main() -> None:
    ev = pd.read_csv(PLIK_EV)
    flota = pd.read_csv(PLIK_FLOTA)[
        ["rok", "szacowana_calkowita_flota_samochodow_osobowych"]
    ]
    ev = ev.rename(
        columns={
            "realistyczny": "liczba_ev_realistyczny",
            "umiarkowanie_optymistyczny": "liczba_ev_umiarkowanie_optymistyczny",
            "optymistyczny": "liczba_ev_optymistyczny",
        }
    )
    ev = ev[[
        "rok",
        "liczba_ev_realistyczny",
        "liczba_ev_umiarkowanie_optymistyczny",
        "liczba_ev_optymistyczny",
    ]]
    samochody = pd.read_csv(PLIK_SAMOCHODY)
    ev_2024 = float(
        samochody.loc[
            (samochody["panstwo"] == "Polska") & (samochody["rok"] == 2024),
            "liczba_ev_we_flocie",
        ].iloc[0]
    )
    rekord_2024 = pd.DataFrame(
        {
            "rok": [2024],
            "liczba_ev_realistyczny": [ev_2024],
            "liczba_ev_umiarkowanie_optymistyczny": [ev_2024],
            "liczba_ev_optymistyczny": [ev_2024],
        }
    )
    ev = pd.concat([rekord_2024, ev], ignore_index=True).drop_duplicates("rok")
    wynik = flota.merge(ev, on="rok", how="inner", validate="one_to_one")
    for scenariusz in ["realistyczny", "umiarkowanie_optymistyczny", "optymistyczny"]:
        wynik[f"udzial_ev_we_flocie_{scenariusz}_procent"] = (
            wynik[f"liczba_ev_{scenariusz}"]
            / wynik["szacowana_calkowita_flota_samochodow_osobowych"]
            * 100
        )
    wynik.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")

    fig, axes = plt.subplots(2, 1, figsize=(13, 11), sharex=True)
    kolory = {"realistyczny": "#176b87", "umiarkowanie_optymistyczny": "#d97706", "optymistyczny": "#15803d"}
    etykiety = {"realistyczny": "Realistyczny", "umiarkowanie_optymistyczny": "Umiarkowanie optymistyczny", "optymistyczny": "Optymistyczny"}
    for scenariusz in kolory:
        axes[0].plot(wynik["rok"], wynik[f"liczba_ev_{scenariusz}"], "o-", color=kolory[scenariusz], label=etykiety[scenariusz])
        axes[1].plot(wynik["rok"], wynik[f"udzial_ev_we_flocie_{scenariusz}_procent"], "o-", color=kolory[scenariusz], label=etykiety[scenariusz])
    for ax in axes:
        ax.axvline(2024, color="#7c3aed", linestyle="--", linewidth=1.6, label="Punkt bazowy floty GUS" if ax is axes[0] else None)
        ax.grid(axis="y", linestyle=":", alpha=0.55)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[0].set_title("Prognozowana liczba EV we flocie")
    axes[0].set_ylabel("Liczba samochodów EV")
    axes[0].yaxis.set_major_formatter(FuncFormatter(formatuj_tysiace))
    axes[0].legend(loc="upper left")
    axes[1].set_title("Prognozowany udział EV w całej flocie samochodów")
    axes[1].set_ylabel("Udział EV (%)")
    axes[1].set_xlabel("Rok")
    axes[1].set_ylim(0, 25)
    axes[1].set_xticks(range(2024, 2041, 2))
    axes[1].legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(PLIK_WYKRESU, dpi=220)
    plt.close(fig)
    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(f"Zapisano wykres: {PLIK_WYKRESU}")
    print(wynik[wynik["rok"].isin([2024, 2030, 2035, 2040])].to_string(index=False))


if __name__ == "__main__":
    main()
