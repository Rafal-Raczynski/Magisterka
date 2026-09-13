from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
PLIK_DANYCH = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "prognoza_liczby_ev_rocznie_scenariusze_2025_2040.csv"
PLIK_WYKRESU = KATALOG_PROJEKTU / "wyniki" / "wykresy" / "prognoza_liczby_ev_w_polsce_2025_2040.png"


def formatuj_tysiace(wartosc, _):
    return f"{wartosc:,.0f}".replace(",", " ")


def main() -> None:
    dane = pd.read_csv(PLIK_DANYCH)
    fig, ax = plt.subplots(figsize=(13, 7.5))
    kolory = {
        "realistyczny": "#176b87",
        "umiarkowanie_optymistyczny": "#d97706",
        "optymistyczny": "#15803d",
    }
    etykiety = {
        "realistyczny": "Realistyczny",
        "umiarkowanie_optymistyczny": "Umiarkowanie optymistyczny",
        "optymistyczny": "Optymistyczny",
    }
    for scenariusz in ["realistyczny", "umiarkowanie_optymistyczny", "optymistyczny"]:
        ax.plot(
            dane["rok"],
            dane[scenariusz],
            marker="o",
            linewidth=2.5,
            color=kolory[scenariusz],
            label=etykiety[scenariusz],
        )

    ax.axvspan(2025.5, 2040.5, color="#176b87", alpha=0.04)
    ax.axvline(2035, color="#7c3aed", linestyle="--", linewidth=1.8, label="Rok 2035")
    ax.scatter([2025], [dane.loc[dane["rok"] == 2025, "realistyczny"].iloc[0]], color="#374151", zorder=4)
    ax.set_title("Prognozowana liczba samochodów EV we flocie w Polsce", fontsize=16, pad=16)
    ax.set_xlabel("Rok")
    ax.set_ylabel("Liczba samochodów EV")
    ax.set_xlim(2025, 2040.5)
    ax.set_ylim(0, None)
    ax.set_xticks(range(2025, 2041, 2))
    ax.yaxis.set_major_formatter(FuncFormatter(formatuj_tysiace))
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
