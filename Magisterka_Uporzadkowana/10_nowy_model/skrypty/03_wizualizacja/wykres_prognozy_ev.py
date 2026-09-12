from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_PROGNOZY = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "prognoza_udzialu_ev_2026_2040.csv"
PLIK_HISTORII = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "wyniki_modelu_ev_historyczne.csv"
PLIK_PANELU = KATALOG_DANYCH / "panele_analityczne" / "panel_analityczny_podstawowy.csv"
PLIK_WYKRESU = KATALOG_PROJEKTU / "wyniki" / "wykresy" / "wykres_prognozy_udzialu_ev_2026_2040.png"
PLIK_WYKRESU_ZMIENNYCH = KATALOG_PROJEKTU / "wyniki" / "wykresy" / "wykres_zmiennych_prognozy_ev_2026_2040.png"


def main() -> None:
    KATALOG_PROJEKTU.joinpath("wyniki", "wykresy").mkdir(parents=True, exist_ok=True)
    historia = pd.read_csv(PLIK_HISTORII)
    historia = historia[historia["panstwo"] == "Polska"].sort_values("rok")
    panel = pd.read_csv(PLIK_PANELU)
    panel = panel[panel["panstwo"] == "Polska"].sort_values("rok")
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
        historia["rok"],
        historia["udzial_ev_dopasowany_procent"],
        linestyle="--",
        linewidth=1.8,
        color="#9ca3af",
        label="Dopasowanie modelu do historii",
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

    fig, axes = plt.subplots(4, 1, figsize=(13, 13), sharex=True)
    lata = prognoza["rok"]
    pkb_historyczne = panel.dropna(subset=["pkb_per_capita_pps"])
    relacja_historyczna = panel.dropna(subset=["relacja_kosztu_ev_do_benzyny"])
    pkb_trend = np.polyval(
        np.polyfit(pkb_historyczne["rok"], pkb_historyczne["pkb_per_capita_pps"], 1),
        pkb_historyczne["rok"],
    )
    relacja_trend = np.polyval(
        np.polyfit(
            relacja_historyczna["rok"],
            relacja_historyczna["relacja_kosztu_ev_do_benzyny"],
            1,
        ),
        relacja_historyczna["rok"],
    )

    axes[0].plot(panel["rok"], panel["pkb_per_capita_pps"], marker="o", color="#64748b", label="Dane faktyczne")
    axes[0].plot(
        pkb_historyczne["rok"],
        pkb_trend,
        linestyle="--",
        linewidth=1.8,
        color="#94a3b8",
        label="Trend historyczny",
    )
    axes[0].plot(lata, prognoza["pkb_per_capita_pps"], marker="o", color="#2563eb", label="Prognoza")
    axes[0].set_ylabel("PPS/osobę")
    axes[0].set_title("Prognozowane zmienne wejściowe i udział EV")
    axes[0].grid(axis="y", linestyle=":", alpha=0.55)

    axes[1].plot(panel["rok"], panel["relacja_kosztu_ev_do_benzyny"], marker="o", color="#64748b")
    axes[1].plot(
        relacja_historyczna["rok"],
        relacja_trend,
        linestyle="--",
        linewidth=1.8,
        color="#94a3b8",
        label="Trend historyczny",
    )
    axes[1].plot(
        lata,
        prognoza["relacja_kosztu_ev_do_benzyny"],
        marker="o",
        color="#16a34a",
    )
    axes[1].set_ylabel("EV / benzyna")
    axes[1].grid(axis="y", linestyle=":", alpha=0.55)

    axes[2].step(panel["rok"], panel["polityka_ue_etap"], where="mid", color="#64748b")
    axes[2].step(
        lata,
        prognoza["polityka_ue_etap"],
        where="mid",
        linewidth=2.5,
        color="#d97706",
    )
    axes[2].set_ylabel("Etap UE")
    axes[2].set_yticks(sorted(prognoza["polityka_ue_etap"].unique()))
    axes[2].grid(axis="y", linestyle=":", alpha=0.55)

    axes[3].plot(historia["rok"], historia["udzial_ev_procent"], marker="o", color="#64748b", label="Dane faktyczne")
    axes[3].plot(
        historia["rok"],
        historia["udzial_ev_dopasowany_procent"],
        linestyle="--",
        linewidth=1.8,
        color="#9ca3af",
        label="Dopasowanie modelu",
    )
    axes[3].plot(
        lata,
        prognoza["prognozowany_udzial_ev_procent"],
        marker="o",
        linewidth=2.5,
        color="#176b87",
    )
    axes[3].set_ylabel("EV (%)")
    axes[3].set_xlabel("Rok")
    axes[3].set_ylim(0, 105)
    axes[3].grid(axis="y", linestyle=":", alpha=0.55)
    axes[0].legend(loc="upper left")
    axes[1].legend(loc="upper left")
    axes[3].legend(loc="upper left")

    for ax in axes:
        ax.axvline(2035, color="#d97706", linestyle="--", linewidth=1.3, alpha=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[3].set_xticks(range(2026, 2041, 2))
    fig.tight_layout()
    fig.savefig(PLIK_WYKRESU_ZMIENNYCH, dpi=220)
    plt.close(fig)
    print(f"Zapisano wykres: {PLIK_WYKRESU}")
    print(f"Zapisano wykres zmiennych: {PLIK_WYKRESU_ZMIENNYCH}")


if __name__ == "__main__":
    main()
