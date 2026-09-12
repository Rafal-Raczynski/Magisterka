from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


KATALOG_PROJEKTU = Path(__file__).resolve().parent
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_PANELU = KATALOG_DANYCH / "panel_analityczny_podstawowy.csv"
PLIK_SCENARIUSZA = KATALOG_DANYCH / "scenariusz_ev_2026_2040.csv"
PLIK_HISTORII = KATALOG_DANYCH / "wyniki_modelu_ev_historyczne.csv"
PLIK_PROGNOZY = KATALOG_DANYCH / "prognoza_udzialu_ev_2026_2040.csv"
PLIK_PARAMETROW = KATALOG_DANYCH / "parametry_modelu_ev.csv"


def logit(udzial: pd.Series) -> pd.Series:
    udzial = udzial.clip(1e-6, 1 - 1e-6)
    return np.log(udzial / (1 - udzial))


def sigmoid(wartosc: pd.Series) -> pd.Series:
    return 1 / (1 + np.exp(-wartosc))


def przygotuj_dane_historyczne() -> pd.DataFrame:
    dane = pd.read_csv(PLIK_PANELU)
    dane = dane.rename(
        columns={
            "procent_ev_w_nowych_rejestracjach": "udzial_ev_procent",
            "pkb_per_capita_pps": "pkb",
            "relacja_kosztu_ev_do_benzyny": "relacja_kosztu",
        }
    )
    wymagane = [
        "panstwo",
        "rok",
        "udzial_ev_procent",
        "pkb",
        "relacja_kosztu",
        "polityka_ue_etap",
    ]
    dane = dane.dropna(subset=wymagane).copy()
    dane["udzial_ev"] = dane["udzial_ev_procent"] / 100
    dane["logit_ev"] = logit(dane["udzial_ev"])
    return dane


def macierz_modelu(dane: pd.DataFrame, panstwa: list[str], lata: list[int]) -> pd.DataFrame:
    zmienne = dane[["pkb", "relacja_kosztu", "polityka_ue_etap"]].copy()
    efekty_panstw = pd.get_dummies(dane["panstwo"], prefix="panstwo", dtype=float)
    efekty_panstw = efekty_panstw.reindex(columns=[f"panstwo_{x}" for x in panstwa[1:]], fill_value=0)
    zmienne = pd.concat([zmienne, efekty_panstw], axis=1)
    return sm.add_constant(zmienne, has_constant="add")


def main() -> None:
    dane = przygotuj_dane_historyczne()
    panstwa = sorted(dane["panstwo"].unique())
    lata = sorted(dane["rok"].unique())
    x = macierz_modelu(dane, panstwa, lata)
    y = dane["logit_ev"]

    model = sm.OLS(y, x).fit(
        cov_type="cluster",
        cov_kwds={"groups": dane["panstwo"]},
    )
    dane["logit_ev_dopasowany"] = model.predict(x)
    dane["udzial_ev_dopasowany_procent"] = sigmoid(dane["logit_ev_dopasowany"]) * 100
    dane[["panstwo", "rok", "udzial_ev_procent", "udzial_ev_dopasowany_procent"]].to_csv(
        PLIK_HISTORII, index=False, encoding="utf-8-sig"
    )

    parametry = pd.DataFrame({"parametr": model.params.index, "wartosc": model.params.values})
    parametry.to_csv(PLIK_PARAMETROW, index=False, encoding="utf-8-sig")
    print(f"R2: {model.rsquared:.4f}")
    print(f"Obserwacje estymacyjne: {len(dane)}")
    print(f"Państwa estymacyjne: {len(panstwa)}")
    print(f"Zapisano historię: {PLIK_HISTORII}")
    print(f"Zapisano parametry: {PLIK_PARAMETROW}")

    scenariusz = pd.read_csv(PLIK_SCENARIUSZA)
    if scenariusz.empty:
        print(f"Brak danych przyszłych. Uzupełnij plik: {PLIK_SCENARIUSZA}")
        return

    scenariusz = scenariusz.dropna(subset=["panstwo", "rok", "pkb_per_capita_pps", "relacja_kosztu_ev_do_benzyny"]).copy()
    scenariusz = scenariusz.rename(columns={"pkb_per_capita_pps": "pkb", "relacja_kosztu_ev_do_benzyny": "relacja_kosztu"})
    scenariusz["polityka_ue_etap"] = pd.cut(
        scenariusz["rok"],
        bins=[-float("inf"), 2019, 2024, 2034, float("inf")],
        labels=[0, 1, 2, 3],
    ).astype(int)
    scenariusz["po_2035"] = (scenariusz["rok"] >= 2035).astype(int)
    x_przyszlosc = macierz_modelu(scenariusz, panstwa, lata)
    x_przyszlosc = x_przyszlosc.reindex(columns=x.columns, fill_value=0)
    scenariusz["prognozowany_udzial_ev_procent"] = sigmoid(model.predict(x_przyszlosc)) * 100
    scenariusz.to_csv(PLIK_PROGNOZY, index=False, encoding="utf-8-sig")
    print(f"Zapisano prognozę: {PLIK_PROGNOZY}")


if __name__ == "__main__":
    main()