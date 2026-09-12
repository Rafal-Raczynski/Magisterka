from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_SAMOCHODY = KATALOG_DANYCH / "tabele_panelowe" / "tabela_samochody_panel.csv"
PLIK_SCENARIUSZE = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "prognoza_scenariusze_impuls_ue_ev_2026_2040.csv"
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu"
PLIK_WYNIKOWY = KATALOG_WYNIKOW / "prognoza_liczby_ev_we_flocie_2026_2040.csv"
PLIK_WYKRESU = KATALOG_PROJEKTU / "wyniki" / "wykresy" / "prognoza_liczby_ev_we_flocie_2025_2040.png"
PLIK_PODSUMOWANIA = KATALOG_WYNIKOW / "prognoza_liczby_ev_rocznie_scenariusze_2025_2040.csv"
def main() -> None:
    samochody = pd.read_csv(PLIK_SAMOCHODY)
    polska = samochody[samochody["panstwo"] == "Polska"].copy()
    polska = polska.dropna(subset=["rok", "szacowana_liczba_wszystkich_nowych_rejestracji"])
    polska = polska[polska["rok"].between(2018, 2025)]
    wspolczynniki = np.polyfit(
        polska["rok"], polska["szacowana_liczba_wszystkich_nowych_rejestracji"], 1
    )

    scenariusze = pd.read_csv(PLIK_SCENARIUSZE)
    scenariusze = scenariusze[scenariusze["panstwo"] == "Polska"].copy()
    lata = sorted(scenariusze["rok"].unique())
    wyniki = []
    stan_poczatkowy = float(
        samochody.loc[
            (samochody["panstwo"] == "Polska") & (samochody["rok"] == 2025),
            "liczba_ev_we_flocie",
        ].iloc[0]
    )

    for nazwa, scenariusz in scenariusze.groupby("scenariusz"):
        scenariusz = scenariusz.sort_values("rok").copy()
        poprzednia_flota = stan_poczatkowy
        for _, rekord in scenariusz.iterrows():
            rok = int(rekord["rok"])
            nowe_rejestracje = float(np.polyval(wspolczynniki, rok))
            nowe_rejestracje = max(nowe_rejestracje, 0)
            nowe_ev = nowe_rejestracje * rekord["prognozowany_udzial_ev_procent"] / 100
            flota_ev = poprzednia_flota + nowe_ev
            wyniki.append(
                {
                    "panstwo": "Polska",
                    "rok": rok,
                    "scenariusz": nazwa,
                    "prognozowany_udzial_ev_procent": rekord["prognozowany_udzial_ev_procent"],
                    "szacowane_wszystkie_nowe_rejestracje": nowe_rejestracje,
                    "szacowane_nowe_ev": nowe_ev,
                    "szacowana_flota_ev": flota_ev,
                }
            )
            poprzednia_flota = flota_ev

    wynik = pd.DataFrame(wyniki)
    KATALOG_WYNIKOW.mkdir(parents=True, exist_ok=True)
    wynik.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")
    podsumowanie = wynik.pivot(
        index="rok", columns="scenariusz", values="szacowana_flota_ev"
    ).reset_index()
    rzeczywisty_2025 = pd.DataFrame(
        {
            "rok": [2025],
            "realistyczny": [stan_poczatkowy],
            "umiarkowanie_optymistyczny": [stan_poczatkowy],
            "optymistyczny": [stan_poczatkowy],
        }
    )
    podsumowanie = pd.concat([rzeczywisty_2025, podsumowanie], ignore_index=True)
    podsumowanie = podsumowanie.sort_values("rok").reset_index(drop=True)
    podsumowanie.to_csv(PLIK_PODSUMOWANIA, index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(13, 7.5))
    kolory = {"realistyczny": "#176b87", "umiarkowanie_optymistyczny": "#d97706", "optymistyczny": "#15803d"}
    etykiety = {"realistyczny": "Realistyczny", "umiarkowanie_optymistyczny": "Umiarkowanie optymistyczny", "optymistyczny": "Optymistyczny"}
    for nazwa, grupa in wynik.groupby("scenariusz"):
        ax.plot(grupa["rok"], grupa["szacowana_flota_ev"], "o-", linewidth=2.5, color=kolory[nazwa], label=etykiety[nazwa])
    ax.axvline(2035, color="#7c3aed", linestyle="--", linewidth=1.8, label="Rok 2035")
    ax.set_title("Szacowana liczba samochodów EV we flocie w Polsce")
    ax.set_xlabel("Rok")
    ax.set_ylabel("Liczba samochodów EV")
    ax.set_xlim(2025, 2040.5)
    ax.grid(axis="y", linestyle=":", alpha=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(PLIK_WYKRESU, dpi=220)
    plt.close(fig)

    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(f"Zapisano podsumowanie roczne: {PLIK_PODSUMOWANIA}")
    print(f"Zapisano wykres: {PLIK_WYKRESU}")
    print(wynik[wynik["rok"].isin([2026, 2030, 2035, 2040])].groupby("scenariusz").tail(1)[["scenariusz", "rok", "szacowana_flota_ev"]].to_string(index=False))


if __name__ == "__main__":
    main()
