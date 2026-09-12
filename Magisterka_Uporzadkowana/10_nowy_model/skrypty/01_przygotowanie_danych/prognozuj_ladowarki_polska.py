from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_PANELU = KATALOG_DANYCH / "tabele_panelowe" / "tabela_ladowarki_panel.csv"
PLIK_SCENARIUSZA = KATALOG_DANYCH / "scenariusze" / "scenariusz_ev_2026_2040.csv"
PLIK_WYNIKOWY = KATALOG_DANYCH / "scenariusze" / "prognoza_ladowarek_polska_2026_2040.csv"
LATA_PRZYSZLE = np.arange(2026, 2041)


def funkcja_logistyczna(rok: np.ndarray, maksimum: float, tempo: float, punkt_przegiecia: float) -> np.ndarray:
    return maksimum / (1 + np.exp(-tempo * (rok - punkt_przegiecia)))


def main() -> None:
    panel = pd.read_csv(PLIK_PANELU)
    historia = panel[panel["panstwo"] == "Polska"].dropna(
        subset=["rok", "punkty_ladowania_na_100_tys_mieszkancow"]
    )
    parametry, _ = curve_fit(
        funkcja_logistyczna,
        historia["rok"],
        historia["punkty_ladowania_na_100_tys_mieszkancow"],
        p0=[300, 0.5, 2028],
        bounds=([50, 0.01, 2010], [10_000, 3, 2050]),
        maxfev=100_000,
    )
    prognoza = funkcja_logistyczna(LATA_PRZYSZLE, *parametry)
    prognoza = np.maximum(prognoza, historia["punkty_ladowania_na_100_tys_mieszkancow"].iloc[-1])

    wynik = pd.DataFrame(
        {
            "panstwo": "Polska",
            "rok": LATA_PRZYSZLE,
            "punkty_ladowania_na_100_tys_mieszkancow": prognoza,
        }
    )
    wynik.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")

    scenariusz = pd.read_csv(PLIK_SCENARIUSZA)
    scenariusz = scenariusz.drop(columns=["punkty_ladowania_na_100_tys_mieszkancow"], errors="ignore")
    scenariusz = scenariusz.merge(wynik, on=["panstwo", "rok"], how="left", validate="one_to_one")
    scenariusz.to_csv(PLIK_SCENARIUSZA, index=False, encoding="utf-8-sig")

    print(f"Zapisano prognozę ładowarek: {PLIK_WYNIKOWY}")
    print(f"Zaktualizowano scenariusz: {PLIK_SCENARIUSZA}")
    print(f"Parametry krzywej logistycznej: maksimum={parametry[0]:.2f}, tempo={parametry[1]:.4f}, punkt_przegiecia={parametry[2]:.2f}")
    print(wynik.head(2).to_string(index=False))
    print(wynik.tail(2).to_string(index=False))


if __name__ == "__main__":
    main()
