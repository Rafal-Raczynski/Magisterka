from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parent
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_PROGNOZY = KATALOG_DANYCH / "prognoza_udzialu_ev_2026_2040.csv"
PLIK_HISTORII = KATALOG_DANYCH / "wyniki_modelu_ev_historyczne.csv"
PLIK_WYKRESU = KATALOG_DANYCH / "wykres_prognozy_udzialu_ev_2026_2040.png"


def main() -> None:
    historia = pd.read_csv(PLIK_HISTORII)
    historia = historia[historia["panstwo"] == "Polska"].sort_values("rok")
    prognoza = pd.read_csv(PLIK_PROGNOZY)
    prognoza = prognoza[prognoza["panstwo"] == "Polska"].sort_values("rok")

    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.axvspan(2025.5, 2040.5, color="#176b87", alpha=0.05, zorder=0)
    plt.plot(
        historia["rok"],
        historia["udzial_ev_procent"],
        marker="o",
        linewidth=2.2,
        markersize=5,
        color="#374151",
        label="Rzeczywisty udział EV",
    )
    plt.plot(
        prognoza["rok"],
        prognoza["prognozowany_udzial_ev_procent"],
        marker="o",
        linewidth=2.5,
        markersize=5,
        color="#176b87",
        label="Prognozowany udział EV",
    )
    ostatnia_historia = historia.iloc[-1]
    pierwsza_prognoza = prognoza.iloc[0]
    ax.plot(
        [ostatnia_historia["rok"], pierwsza_prognoza["rok"]],
        [ostatnia_historia["udzial_ev_procent"], pierwsza_prognoza["prognozowany_udzial_ev_procent"]],
        color="#176b87",
        linestyle=":",
        linewidth=1.5,
        alpha=0.8,
    )
    plt.axvline(
        2035,
        color="#d97706",
        linestyle="--",
        linewidth=1.8,
        label="Rok 2035 - etap polityki UE",
    )
    plt.scatter(
        [2035],
        prognoza.loc[prognoza["rok"] == 2035, "prognozowany_udzial_ev_procent"],
        color="#d97706",
        zorder=3,
    )
    ax.set_title("Udział EV w nowych rejestracjach w Polsce", fontsize=16, pad=16)
    ax.set_xlabel("Rok")
    ax.set_ylabel("Udział EV w nowych rejestracjach (%)")
    ax.set_ylim(0, 105)
    ax.set_xlim(historia["rok"].min() - 0.5, 2040.5)
    ax.set_xticks(range(int(historia["rok"].min()), 2041, 2))
    ax.grid(axis="y", linestyle=":", alpha=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", frameon=True, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(PLIK_WYKRESU, dpi=220)
    plt.close(fig)
    print(f"Zapisano wykres: {PLIK_WYKRESU}")


if __name__ == "__main__":
    main()
