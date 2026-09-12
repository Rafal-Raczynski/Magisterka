from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_PANELU = KATALOG_DANYCH / "panele_analityczne" / "panel_analityczny_rozszerzony.csv"
PLIK_WYNIKOWY = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "porownanie_modeli_relacja_kosztu.csv"


def logit(udzial: pd.Series) -> pd.Series:
    udzial = udzial.clip(1e-6, 1 - 1e-6)
    return np.log(udzial / (1 - udzial))


def macierz(dane: pd.DataFrame, panstwa: list[str], cechy: list[str]) -> pd.DataFrame:
    efekty = pd.get_dummies(dane["panstwo"], prefix="panstwo", dtype=float)
    efekty = efekty.reindex(columns=[f"panstwo_{x}" for x in panstwa[1:]], fill_value=0)
    return sm.add_constant(pd.concat([dane[cechy], efekty], axis=1), has_constant="add")


def main() -> None:
    panel = pd.read_csv(PLIK_PANELU).rename(
        columns={
            "pkb_per_capita_pps": "pkb",
            "relacja_kosztu_ev_do_benzyny": "relacja",
        }
    )
    panel = panel[panel["rok"].between(2020, 2025)].copy()
    panel["log_ladowarki"] = np.log1p(panel["punkty_ladowania_na_100_tys_mieszkancow"].clip(lower=0))
    panel["logit_ev"] = logit(panel["procent_ev_w_nowych_rejestracjach"] / 100)
    wyniki = []

    for nazwa, cechy in {
        "z_relacja_kosztu": ["pkb", "relacja", "log_ladowarki"],
        "bez_relacji_kosztu": ["pkb", "log_ladowarki"],
    }.items():
        dane = panel.dropna(subset=["panstwo", "rok", "logit_ev", *cechy]).copy()
        train = dane[dane["rok"] <= 2023]
        test = dane[dane["rok"] >= 2024]
        panstwa = sorted(train["panstwo"].unique())
        x_train = macierz(train, panstwa, cechy)
        x_test = macierz(test, panstwa, cechy).reindex(columns=x_train.columns, fill_value=0)
        model = sm.OLS(train["logit_ev"], x_train).fit(cov_type="cluster", cov_kwds={"groups": train["panstwo"]})
        przewidywany = 1 / (1 + np.exp(-model.predict(x_test))) * 100
        rzeczywisty = test["procent_ev_w_nowych_rejestracjach"]
        wyniki.append({
            "model": nazwa,
            "r2_estymacja": model.rsquared,
            "r2_test": r2_score(rzeczywisty, przewidywany),
            "mae_test": mean_absolute_error(rzeczywisty, przewidywany),
            "rmse_test": mean_squared_error(rzeczywisty, przewidywany) ** 0.5,
            "p_value_relacja": model.pvalues.get("relacja", np.nan),
            "obserwacje_estymacja": len(train),
            "obserwacje_test": len(test),
        })

    wynik = pd.DataFrame(wyniki)
    PLIK_WYNIKOWY.parent.mkdir(parents=True, exist_ok=True)
    wynik.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")
    print(wynik.to_string(index=False))
    print(f"Zapisano: {PLIK_WYNIKOWY}")


if __name__ == "__main__":
    main()
