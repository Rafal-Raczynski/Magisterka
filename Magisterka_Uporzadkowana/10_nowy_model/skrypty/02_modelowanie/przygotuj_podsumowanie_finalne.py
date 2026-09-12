from pathlib import Path

import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_SCENARIUSZY = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "prognoza_scenariusze_impuls_ue_ev_2026_2040.csv"
PLIK_PANELU = KATALOG_DANYCH / "panele_analityczne" / "panel_analityczny_rozszerzony.csv"
PLIK_WYNIKOWY = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "podsumowanie_finalne_prognozy_ev.csv"


def main() -> None:
    scenariusze = pd.read_csv(PLIK_SCENARIUSZY)
    scenariusze = scenariusze[
        scenariusze["rok"].isin([2026, 2030, 2035, 2040])
    ][["rok", "scenariusz", "impuls_regulacji_ue_logit", "prognozowany_udzial_ev_procent"]]

    panel = pd.read_csv(PLIK_PANELU)
    rzeczywisty_2025 = panel.loc[
        (panel["panstwo"] == "Polska") & (panel["rok"] == 2025),
        "procent_ev_w_nowych_rejestracjach",
    ]
    if rzeczywisty_2025.empty:
        raise ValueError("Brak rzeczywistego udziału EV dla Polski w 2025 roku.")

    rekord_2025 = pd.DataFrame(
        {
            "rok": [2025],
            "scenariusz": ["dane_rzeczywiste"],
            "impuls_regulacji_ue_logit": [0.0],
            "prognozowany_udzial_ev_procent": [float(rzeczywisty_2025.iloc[0])],
        }
    )
    wynik = pd.concat([rekord_2025, scenariusze], ignore_index=True)
    wynik = wynik.sort_values(["rok", "scenariusz"]).reset_index(drop=True)
    PLIK_WYNIKOWY.parent.mkdir(parents=True, exist_ok=True)
    wynik.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")
    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(wynik.to_string(index=False))


if __name__ == "__main__":
    main()
