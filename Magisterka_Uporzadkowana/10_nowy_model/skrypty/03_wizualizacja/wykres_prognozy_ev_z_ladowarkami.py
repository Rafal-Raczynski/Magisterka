from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_HISTORII_EV = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "wyniki_modelu_ev_z_ladowarkami_historyczne.csv"
PLIK_PROGNOZY_EV = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "prognoza_udzialu_ev_z_ladowarkami_2026_2040.csv"
PLIK_LADOWARKI = KATALOG_DANYCH / "tabele_panelowe" / "tabela_ladowarki_panel.csv"
PLIK_PROGNOZY_LADOWAREK = KATALOG_DANYCH / "scenariusze" / "prognoza_ladowarek_polska_2026_2040.csv"
KATALOG_WYKRESOW = KATALOG_PROJEKTU / "wyniki" / "wykresy"
PLIK_WYKRESU_EV = KATALOG_WYKRESOW / "wykres_prognozy_ev_z_ladowarkami_2026_2040.png"
PLIK_WYKRESU_LADOWAREK = KATALOG_WYKRESOW / "wykres_prognozy_ladowarek_2020_2040.png"


def main() -> None:
    KATALOG_WYKRESOW.mkdir(parents=True, exist_ok=True)
    historia_ev = pd.read_csv(PLIK_HISTORII_EV)
    historia_ev = historia_ev[historia_ev["panstwo"] == "Polska"].sort_values("rok")
    prognoza_ev = pd.read_csv(PLIK_PROGNOZY_EV)
    prognoza_ev = prognoza_ev[prognoza_ev["panstwo"] == "Polska"].sort_values("rok")

    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.axvspan(2025.5, 2040.5, color="#176b87", alpha=0.05)
    ax.plot(historia_ev["rok"], historia_ev["udzial_ev_procent"], "o-", color="#374151", label="Dane faktyczne")
    ax.plot(historia_ev["rok"], historia_ev["udzial_ev_dopasowany_procent"], "--", color="#9ca3af", label="Dopasowanie modelu")
    ax.plot(prognoza_ev["rok"], prognoza_ev["prognozowany_udzial_ev_procent"], "o-", color="#176b87", label="Prognoza z ładowarkami")
    ax.axvline(2035, color="#d97706", linestyle="--", linewidth=1.8, label="Rok 2035 - etap polityki UE")
    ax.set_title("Prognoza udziału EV z uwzględnieniem ładowarek")
    ax.set_xlabel("Rok")
    ax.set_ylabel("Udział EV w nowych rejestracjach (%)")
    ax.set_xlim(historia_ev["rok"].min() - 0.5, 2040.5)
    ax.set_ylim(0, 105)
    ax.set_xticks(range(int(historia_ev["rok"].min()), 2041, 2))
    ax.grid(axis="y", linestyle=":", alpha=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(PLIK_WYKRESU_EV, dpi=220)
    plt.close(fig)

    historia_ladowarek = pd.read_csv(PLIK_LADOWARKI)
    historia_ladowarek = historia_ladowarek[historia_ladowarek["panstwo"] == "Polska"].sort_values("rok")
    prognoza_ladowarek = pd.read_csv(PLIK_PROGNOZY_LADOWAREK).sort_values("rok")

    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.axvspan(2025.5, 2040.5, color="#16a34a", alpha=0.05)
    ax.plot(
        historia_ladowarek["rok"],
        historia_ladowarek["punkty_ladowania_na_100_tys_mieszkancow"],
        "o-",
        color="#374151",
        label="Dane faktyczne",
    )
    ax.plot(
        prognoza_ladowarek["rok"],
        prognoza_ladowarek["punkty_ladowania_na_100_tys_mieszkancow"],
        "o-",
        color="#16a34a",
        label="Prognoza logistyczna",
    )
    ax.axvline(2035, color="#d97706", linestyle="--", linewidth=1.8, label="Rok 2035")
    ax.set_title("Rozwój publicznych punktów ładowania w Polsce")
    ax.set_xlabel("Rok")
    ax.set_ylabel("Punkty ładowania na 100 tys. mieszkańców")
    ax.set_xlim(historia_ladowarek["rok"].min() - 0.5, 2040.5)
    ax.set_xticks(range(int(historia_ladowarek["rok"].min()), 2041, 1))
    ax.grid(axis="y", linestyle=":", alpha=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(PLIK_WYKRESU_LADOWAREK, dpi=220)
    plt.close(fig)

    print(f"Zapisano: {PLIK_WYKRESU_EV}")
    print(f"Zapisano: {PLIK_WYKRESU_LADOWAREK}")


if __name__ == "__main__":
    main()
