from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_squared_error


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_PANELU = KATALOG_DANYCH / "panele_analityczne" / "panel_analityczny_rozszerzony.csv"
KATALOG_WYNIKOW = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu"
PLIK_SCENARIUSZA = KATALOG_DANYCH / "scenariusze" / "scenariusz_ev_2026_2040.csv"
PLIK_HISTORII = KATALOG_WYNIKOW / "wyniki_modelu_ev_z_ladowarkami_historyczne.csv"
PLIK_PARAMETROW = KATALOG_WYNIKOW / "parametry_modelu_ev_z_ladowarkami.csv"
PLIK_STATYSTYKI = KATALOG_WYNIKOW / "statystyki_modelu_ev_z_ladowarkami.csv"
PLIK_DOPASOWANIA = KATALOG_WYNIKOW / "miary_dopasowania_modelu_ev_z_ladowarkami.csv"
PLIK_PROGNOZY = KATALOG_WYNIKOW / "prognoza_udzialu_ev_z_ladowarkami_2026_2040.csv"


def logit(udzial: pd.Series) -> pd.Series:
    udzial = udzial.clip(1e-6, 1 - 1e-6)
    return np.log(udzial / (1 - udzial))


def sigmoid(wartosc: pd.Series) -> pd.Series:
    return 1 / (1 + np.exp(-wartosc))


def macierz_modelu(dane: pd.DataFrame, panstwa: list[str]) -> pd.DataFrame:
    zmienne = dane[
        [
            "pkb_per_capita_pps",
            "relacja_kosztu_ev_do_benzyny",
            "log_punkty_ladowania_na_100_tys_mieszkancow",
            "polityka_ue_etap",
        ]
    ].copy()
    zmienne = zmienne.rename(
        columns={
            "pkb_per_capita_pps": "pkb",
            "relacja_kosztu_ev_do_benzyny": "relacja_kosztu",
        }
    )
    efekty_panstw = pd.get_dummies(dane["panstwo"], prefix="panstwo", dtype=float)
    efekty_panstw = efekty_panstw.reindex(
        columns=[f"panstwo_{panstwo}" for panstwo in panstwa[1:]],
        fill_value=0,
    )
    return sm.add_constant(pd.concat([zmienne, efekty_panstw], axis=1), has_constant="add")


def main() -> None:
    dane = pd.read_csv(PLIK_PANELU)
    wymagane = [
        "panstwo",
        "rok",
        "procent_ev_w_nowych_rejestracjach",
        "pkb_per_capita_pps",
        "relacja_kosztu_ev_do_benzyny",
        "punkty_ladowania_na_100_tys_mieszkancow",
        "polityka_ue_etap",
    ]
    dane = dane.dropna(subset=wymagane).copy()
    dane["udzial_ev"] = dane["procent_ev_w_nowych_rejestracjach"] / 100
    dane["logit_ev"] = logit(dane["udzial_ev"])
    dane["log_punkty_ladowania_na_100_tys_mieszkancow"] = np.log1p(
        dane["punkty_ladowania_na_100_tys_mieszkancow"].clip(lower=0)
    )

    panstwa = sorted(dane["panstwo"].unique())
    x = macierz_modelu(dane, panstwa)
    model = sm.OLS(dane["logit_ev"], x).fit(
        cov_type="cluster",
        cov_kwds={"groups": dane["panstwo"]},
    )
    dane["udzial_ev_dopasowany_procent"] = sigmoid(model.predict(x)) * 100
    wynik = dane[
        ["panstwo", "rok", "procent_ev_w_nowych_rejestracjach", "udzial_ev_dopasowany_procent"]
    ].rename(columns={"procent_ev_w_nowych_rejestracjach": "udzial_ev_procent"})
    KATALOG_WYNIKOW.mkdir(parents=True, exist_ok=True)
    wynik.to_csv(PLIK_HISTORII, index=False, encoding="utf-8-sig")
    pd.DataFrame({"parametr": model.params.index, "wartosc": model.params.values}).to_csv(
        PLIK_PARAMETROW, index=False, encoding="utf-8-sig"
    )
    przedzialy = model.conf_int()
    statystyki = pd.DataFrame(
        {
            "parametr": model.params.index,
            "wspolczynnik": model.params.values,
            "blad_standardowy": model.bse.values,
            "statystyka_t": model.tvalues.values,
            "p_value": model.pvalues.values,
            "przedzial_ufnosci_95_lewy": przedzialy[0].values,
            "przedzial_ufnosci_95_prawy": przedzialy[1].values,
        }
    )
    statystyki.to_csv(PLIK_STATYSTYKI, index=False, encoding="utf-8-sig")

    y = wynik["udzial_ev_procent"]
    y_hat = wynik["udzial_ev_dopasowany_procent"]
    print(f"R2: {model.rsquared:.4f}")
    print(f"MAE: {mean_absolute_error(y, y_hat):.4f} punktu procentowego")
    print(f"RMSE: {mean_squared_error(y, y_hat) ** 0.5:.4f} punktu procentowego")
    pd.DataFrame(
        {
            "miara": ["r2", "mae", "rmse", "liczba_obserwacji", "liczba_panstw"],
            "wartosc": [
                model.rsquared,
                mean_absolute_error(y, y_hat),
                mean_squared_error(y, y_hat) ** 0.5,
                len(dane),
                len(panstwa),
            ],
        }
    ).to_csv(PLIK_DOPASOWANIA, index=False, encoding="utf-8-sig")
    print(f"Obserwacje: {len(dane)}")
    print(f"Państwa: {len(panstwa)}")
    print(f"Zapisano historię: {PLIK_HISTORII}")
    print(f"Zapisano parametry: {PLIK_PARAMETROW}")
    print(f"Zapisano statystyki: {PLIK_STATYSTYKI}")
    print(f"Zapisano miary dopasowania: {PLIK_DOPASOWANIA}")
    print("Polska:")
    print(wynik[wynik["panstwo"] == "Polska"].tail(3).to_string(index=False))

    if not PLIK_SCENARIUSZA.exists():
        print(f"Brak scenariusza przyszłego: {PLIK_SCENARIUSZA}")
        return
    scenariusz = pd.read_csv(PLIK_SCENARIUSZA)
    wymagane_przyszle = [
        "panstwo",
        "rok",
        "pkb_per_capita_pps",
        "relacja_kosztu_ev_do_benzyny",
        "punkty_ladowania_na_100_tys_mieszkancow",
    ]
    scenariusz = scenariusz.dropna(subset=wymagane_przyszle).copy()
    scenariusz["pkb"] = scenariusz["pkb_per_capita_pps"]
    scenariusz["relacja_kosztu"] = scenariusz["relacja_kosztu_ev_do_benzyny"]
    scenariusz["log_punkty_ladowania_na_100_tys_mieszkancow"] = np.log1p(
        scenariusz["punkty_ladowania_na_100_tys_mieszkancow"].clip(lower=0)
    )
    scenariusz["polityka_ue_etap"] = pd.cut(
        scenariusz["rok"],
        bins=[-float("inf"), 2019, 2024, 2034, float("inf")],
        labels=[0, 1, 2, 3],
    ).astype(int)
    panstwa = sorted(dane["panstwo"].unique())
    cechy_przyszle = macierz_modelu(scenariusz, panstwa)
    cechy_przyszle = cechy_przyszle.reindex(columns=x.columns, fill_value=0)
    scenariusz["prognozowany_udzial_ev_procent"] = (
        sigmoid(model.predict(cechy_przyszle)) * 100
    )
    scenariusz.to_csv(PLIK_PROGNOZY, index=False, encoding="utf-8-sig")
    print(f"Zapisano prognozę z ładowarkami: {PLIK_PROGNOZY}")


if __name__ == "__main__":
    main()
