from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


KATALOG_PROJEKTU = Path(__file__).resolve().parents[2]
KATALOG_DANYCH = KATALOG_PROJEKTU / "dane_przetworzone"
PLIK_BAZY = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "prognoza_udzialu_ev_z_ladowarkami_2026_2040.csv"
PLIK_HISTORII_MODELU = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "wyniki_modelu_ev_z_ladowarkami_historyczne.csv"
PLIK_WYNIKOWY = KATALOG_PROJEKTU / "wyniki" / "wyniki_modelu" / "prognoza_scenariusze_impuls_ue_ev_2026_2040.csv"
PLIK_WYKRESU = KATALOG_PROJEKTU / "wyniki" / "wykresy" / "porownanie_scenariuszy_impuls_ue_ev_2025_2040.png"

SCENARIUSZE = {
    "realistyczny": 0.0,
    "umiarkowanie_optymistyczny": 1.5,
    "optymistyczny": 3.5,
}


def main() -> None:
    baza = pd.read_csv(PLIK_BAZY)
    baza = baza[baza["panstwo"] == "Polska"].sort_values("rok").copy()
    historia_modelu = pd.read_csv(PLIK_HISTORII_MODELU)
    dopasowanie_2025 = float(
        historia_modelu.loc[
            (historia_modelu["panstwo"] == "Polska")
            & (historia_modelu["rok"] == 2025),
            "udzial_ev_dopasowany_procent",
        ].iloc[0]
    ) / 100
    historia = pd.read_csv(
        KATALOG_DANYCH / "panele_analityczne" / "panel_analityczny_rozszerzony.csv"
    )
    udzial_2025 = float(
        historia.loc[
            (historia["panstwo"] == "Polska") & (historia["rok"] == 2025),
            "procent_ev_w_nowych_rejestracjach",
        ].iloc[0]
    )
    lata_prognozy = baza["rok"].to_numpy()
    postep = np.clip((lata_prognozy - 2025) / 15, 0, 1)
    udzial_bazowy = np.clip(baza["prognozowany_udzial_ev_procent"] / 100, 1e-6, 1 - 1e-6)
    logit_bazowy = np.log(udzial_bazowy / (1 - udzial_bazowy))
    logit_start = np.log((udzial_2025 / 100) / (1 - udzial_2025 / 100))
    logit_delta = logit_bazowy - np.log(dopasowanie_2025 / (1 - dopasowanie_2025))

    wyniki = []
    for nazwa, maksymalny_impuls in SCENARIUSZE.items():
        impuls = maksymalny_impuls * postep
        udzial = 1 / (1 + np.exp(-(logit_start + logit_delta + impuls))) * 100
        dane = baza[["panstwo", "rok"]].copy()
        dane["scenariusz"] = nazwa
        dane["impuls_regulacji_ue_logit"] = impuls
        dane["prognozowany_udzial_ev_procent"] = udzial
        wyniki.append(dane)

    wynik = pd.concat(wyniki, ignore_index=True)
    wynik.to_csv(PLIK_WYNIKOWY, index=False, encoding="utf-8-sig")

    historia = historia[
        (historia["panstwo"] == "Polska")
        & historia["rok"].between(2008, 2025)
    ].dropna(subset=["procent_ev_w_nowych_rejestracjach"])

    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.plot(
        historia["rok"],
        historia["procent_ev_w_nowych_rejestracjach"],
        "o-",
        color="#374151",
        label="Dane historyczne",
    )
    kolory = {
        "realistyczny": "#176b87",
        "umiarkowanie_optymistyczny": "#d97706",
        "optymistyczny": "#15803d",
    }
    etykiety = {
        "realistyczny": "Realistyczny",
        "umiarkowanie_optymistyczny": "Umiarkowanie optymistyczny",
        "optymistyczny": "Optymistyczny",
    }
    for nazwa, grupa in wynik.groupby("scenariusz"):
        grupa_wykres = pd.concat(
            [
                pd.DataFrame(
                    {
                        "rok": [2025],
                        "prognozowany_udzial_ev_procent": [udzial_2025],
                    }
                ),
                grupa[["rok", "prognozowany_udzial_ev_procent"]],
            ],
            ignore_index=True,
        )
        ax.plot(
            grupa_wykres["rok"],
            grupa_wykres["prognozowany_udzial_ev_procent"],
            "o-",
            color=kolory[nazwa],
            linewidth=2.5,
            label=etykiety[nazwa],
        )
    ax.axvline(2035, color="#7c3aed", linestyle="--", linewidth=1.8, label="Rok 2035")
    ax.axvspan(2025.5, 2040.5, color="#176b87", alpha=0.04)
    ax.set_title("Scenariusze EV z dodatkowym impulsem regulacji UE")
    ax.set_xlabel("Rok")
    ax.set_ylabel("Udział EV w nowych rejestracjach (%)")
    ax.set_ylim(0, 105)
    ax.set_xlim(2008, 2040.5)
    ax.set_xticks(range(2008, 2041, 2))
    ax.grid(axis="y", linestyle=":", alpha=0.55)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(PLIK_WYKRESU, dpi=220)
    plt.close(fig)

    print(f"Zapisano: {PLIK_WYNIKOWY}")
    print(f"Zapisano wykres: {PLIK_WYKRESU}")
    print(
        wynik[wynik["rok"].isin([2026, 2030, 2035, 2040])]
        .groupby("scenariusz")
        .tail(1)[["scenariusz", "rok", "impuls_regulacji_ue_logit", "prognozowany_udzial_ev_procent"]]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
