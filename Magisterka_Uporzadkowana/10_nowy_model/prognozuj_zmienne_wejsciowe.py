from pathlib import Path

import numpy as np
import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parent
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_PANELU = KATALOG_DANYCH / "panel_analityczny_podstawowy.csv"
PLIK_PKB = KATALOG_DANYCH / "prognoza_pkb_polska_2026_2040.csv"
PLIK_RELACJI = KATALOG_DANYCH / "prognoza_relacji_kosztu_polska_2026_2040.csv"
PLIK_SCENARIUSZA = KATALOG_DANYCH / "scenariusz_ev_2026_2040.csv"


def prognozuj_trendem(dane: pd.DataFrame, kolumna: str, lata_przyszle: np.ndarray) -> pd.DataFrame:
    dane = dane.dropna(subset=["rok", kolumna])
    wspolczynniki = np.polyfit(dane["rok"], dane[kolumna], 1)
    wartosci = np.polyval(wspolczynniki, lata_przyszle)
    return pd.DataFrame({"panstwo": "Polska", "rok": lata_przyszle, kolumna: wartosci})


def main() -> None:
    panel = pd.read_csv(PLIK_PANELU)
    polska = panel[panel["panstwo"] == "Polska"].copy()
    lata = np.arange(2026, 2041)

    prognoza_pkb = prognozuj_trendem(polska, "pkb_per_capita_pps", lata)
    prognoza_relacji = prognozuj_trendem(
        polska, "relacja_kosztu_ev_do_benzyny", lata
    )
    prognoza_relacji["relacja_kosztu_ev_do_benzyny"] = (
        prognoza_relacji["relacja_kosztu_ev_do_benzyny"].clip(lower=0.01)
    )

    prognoza_pkb.to_csv(PLIK_PKB, index=False, encoding="utf-8-sig")
    prognoza_relacji.to_csv(PLIK_RELACJI, index=False, encoding="utf-8-sig")

    scenariusz = prognoza_pkb.merge(prognoza_relacji, on=["panstwo", "rok"])
    scenariusz.to_csv(PLIK_SCENARIUSZA, index=False, encoding="utf-8-sig")

    print(f"Zapisano: {PLIK_PKB}")
    print(f"Zapisano: {PLIK_RELACJI}")
    print(f"Zapisano połączony scenariusz: {PLIK_SCENARIUSZA}")
    print(scenariusz.head(3).to_string(index=False))
    print(scenariusz.tail(3).to_string(index=False))


if __name__ == "__main__":
    main()