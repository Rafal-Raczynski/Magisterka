from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_PANELU = KATALOG_DANYCH / "panele_analityczne" / "panel_analityczny_rozszerzony.csv"
PLIK_WYNIKOWY = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "test_odpornosc_modelu_ev.csv"
SKRYPT_WALIDACJI = Path(__file__).resolve().parent / "walidacja_historyczna_modeli_ev.py"

spec = importlib.util.spec_from_file_location("walidacja", SKRYPT_WALIDACJI)
walidacja = importlib.util.module_from_spec(spec)
spec.loader.exec_module(walidacja)


def main() -> None:
    panel = pd.read_csv(PLIK_PANELU).rename(
        columns={
            "pkb_per_capita_pps": "pkb",
            "relacja_kosztu_ev_do_benzyny": "relacja",
        }
    )
    panel = panel[panel["rok"].between(2020, 2025)]
    liderzy = ["Norwegia", "Holandia", "Dania", "Szwecja"]
    scenariusze = {"pelna_proba": None}
    scenariusze.update({f"bez_{kraj}": kraj for kraj in liderzy})
    wyniki = []

    for nazwa, usun_kraj in scenariusze.items():
        dane = panel if usun_kraj is None else panel[panel["panstwo"] != usun_kraj]
        kolumny = [
            "panstwo", "rok", "procent_ev_w_nowych_rejestracjach",
            "pkb", "relacja", "punkty_ladowania_na_100_tys_mieszkancow",
        ]
        dane = walidacja.przygotuj(dane, kolumny)
        train = dane[dane["rok"] <= 2023]
        test = dane[dane["rok"] >= 2024]
        panstwa = sorted(train["panstwo"].unique())
        cechy = ["pkb", "relacja", "log_ladowarki"]
        x_train = walidacja.macierz(train, panstwa, cechy)
        x_test = walidacja.macierz(test, panstwa, cechy).reindex(columns=x_train.columns, fill_value=0)
        model = sm.OLS(train["logit_ev"], x_train).fit()
        przewidywany = 1 / (1 + np.exp(-model.predict(x_test))) * 100
        rzeczywisty = test["procent_ev_w_nowych_rejestracjach"]
        wyniki.append(
            {
                "wariant": nazwa,
                "usuniete_panstwo": usun_kraj or "brak",
                "r2_test": r2_score(rzeczywisty, przewidywany),
                "mae_test": mean_absolute_error(rzeczywisty, przewidywany),
                "rmse_test": mean_squared_error(rzeczywisty, przewidywany) ** 0.5,
                "obserwacje_test": len(test),
                "panstwa_test": test["panstwo"].nunique(),
            }
        )

    wynik = pd.DataFrame(wyniki)
    PLIK_WYNIKOWY.parent.mkdir(parents=True, exist_ok=True)
    wynik.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")
    print(wynik.to_string(index=False))
    print(f"Zapisano: {PLIK_WYNIKOWY}")


if __name__ == "__main__":
    main()
