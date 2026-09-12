from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
PLIK_PANELU = (
    KATALOG_PROJEKTU
    / "dane_przetworzone"
    / "panele_analityczne"
    / "panel_analityczny_rozszerzony.csv"
)
PLIK_WYNIKOWY = (
    KATALOG_PROJEKTU
    / "wyniki"
    / "wyniki_modelu"
    / "walidacja_historyczna_modeli_ev.csv"
)


def logit(udzial: pd.Series) -> pd.Series:
    udzial = udzial.clip(1e-6, 1 - 1e-6)
    return np.log(udzial / (1 - udzial))


def przygotuj(dane: pd.DataFrame, kolumny: list[str]) -> pd.DataFrame:
    dane = dane.dropna(subset=kolumny).copy()
    dane["logit_ev"] = logit(dane["procent_ev_w_nowych_rejestracjach"] / 100)
    dane["log_ladowarki"] = np.log1p(
        dane["punkty_ladowania_na_100_tys_mieszkancow"].clip(lower=0)
    )
    return dane


def macierz(dane: pd.DataFrame, panstwa: list[str], cechy: list[str]) -> pd.DataFrame:
    wynik = dane[cechy].copy()
    efekty = pd.get_dummies(dane["panstwo"], prefix="panstwo", dtype=float)
    efekty = efekty.reindex(
        columns=[f"panstwo_{panstwo}" for panstwo in panstwa[1:]],
        fill_value=0,
    )
    return sm.add_constant(pd.concat([wynik, efekty], axis=1), has_constant="add")


def ocen(model, x_test: pd.DataFrame, test: pd.DataFrame, nazwa: str) -> dict:
    przewidywany_logit = model.predict(x_test)
    przewidywany = 1 / (1 + np.exp(-przewidywany_logit)) * 100
    rzeczywisty = test["procent_ev_w_nowych_rejestracjach"]
    return {
        "model": nazwa,
        "r2_test": r2_score(rzeczywisty, przewidywany),
        "mae_test": mean_absolute_error(rzeczywisty, przewidywany),
        "rmse_test": mean_squared_error(rzeczywisty, przewidywany) ** 0.5,
        "obserwacje_test": len(test),
        "panstwa_test": test["panstwo"].nunique(),
    }


def main() -> None:
    panel = pd.read_csv(PLIK_PANELU)
    panel = panel[panel["rok"].between(2020, 2025)].copy()
    wyniki = []
    for nazwa, cechy, kolumny in [
        (
            "bazowy",
            ["pkb", "relacja"],
            ["panstwo", "rok", "procent_ev_w_nowych_rejestracjach", "pkb", "relacja"],
        ),
        (
            "z_ladowarkami",
            ["pkb", "relacja", "log_ladowarki"],
            [
                "panstwo",
                "rok",
                "procent_ev_w_nowych_rejestracjach",
                "pkb",
                "relacja",
                "punkty_ladowania_na_100_tys_mieszkancow",
            ],
        ),
    ]:
        dane = panel.rename(
            columns={
                "pkb_per_capita_pps": "pkb",
                "relacja_kosztu_ev_do_benzyny": "relacja",
            }
        )
        dane = przygotuj(dane, kolumny)
        train = dane[dane["rok"] <= 2023].copy()
        test = dane[dane["rok"] >= 2024].copy()
        panstwa = sorted(train["panstwo"].unique())
        x_train = macierz(train, panstwa, cechy)
        x_test = macierz(test, panstwa, cechy).reindex(columns=x_train.columns, fill_value=0)
        model = sm.OLS(train["logit_ev"], x_train).fit()
        wyniki.append(ocen(model, x_test, test, nazwa))

    wynik = pd.DataFrame(wyniki)
    PLIK_WYNIKOWY.parent.mkdir(parents=True, exist_ok=True)
    wynik.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")
    print(wynik.to_string(index=False))
    print(f"Zapisano: {PLIK_WYNIKOWY}")


if __name__ == "__main__":
    main()
