from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "02_dane_przetworzone" / "Dane"
RAW_ROOT = PROJECT_ROOT / "01_dane_surowe"
RESULTS_ROOT = DATA_ROOT / "Estymacyjne_dane"
UPORZADKOWANE_ROOT = DATA_ROOT / "Uporzadkowane_dane"
ZRODLA_ROOT = DATA_ROOT / "Zrodla_danych"

for folder in [DATA_ROOT, RESULTS_ROOT, UPORZADKOWANE_ROOT, ZRODLA_ROOT]:
    folder.mkdir(parents=True, exist_ok=True)
