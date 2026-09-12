from pathlib import Path
import shutil

root = Path("c:/Users/Rafał/Desktop/Magisterka")
base_name = "Magisterka_Uporzadkowana"
index = 1
while True:
    target = root / base_name if index == 1 else root / f"{base_name}_{index}"
    if not target.exists():
        break
    index += 1

folders = [
    "00_oryginalne",
    "01_dane_surowe",
    "02_dane_przetworzone",
    "03_notebooki",
    "04_skrypty",
    "05_modelowanie",
    "06_wyniki",
    "07_wykresy",
    "08_raporty_i_dokumentacja",
    "09_archiwum",
]

for folder in folders:
    (target / folder).mkdir(parents=True, exist_ok=True)

for item in root.iterdir():
    if item.name.startswith(".") or item.name == target.name:
        continue
    if item.name == "organizuj_kopie.py":
        continue

    if item.is_dir():
        if item.name == "Dane":
            shutil.copytree(item, target / "02_dane_przetworzone" / item.name, dirs_exist_ok=True)
        elif item.name in {"EE", "EE-dyplom-main", "Praca", "Obrazy"}:
            shutil.copytree(item, target / "08_raporty_i_dokumentacja" / item.name, dirs_exist_ok=True)
        elif item.name == "Wykresy":
            shutil.copytree(item, target / "07_wykresy" / item.name, dirs_exist_ok=True)
        elif item.name in {"Kod", "MatIO.NET", "Źródła"}:
            shutil.copytree(item, target / "04_skrypty" / item.name, dirs_exist_ok=True)
        else:
            shutil.copytree(item, target / "09_archiwum" / item.name, dirs_exist_ok=True)
    else:
        if item.suffix.lower() in {".csv", ".xlsx", ".xls", ".xlsm", ".parquet", ".txt"}:
            shutil.copy2(item, target / "01_dane_surowe" / item.name)
        elif item.suffix.lower() == ".ipynb":
            shutil.copy2(item, target / "03_notebooki" / item.name)
        else:
            shutil.copy2(item, target / "00_oryginalne" / item.name)

if (root / "Dane").exists():
    dane_root = target / "04_skrypty" / "Dane"
    dane_root.mkdir(parents=True, exist_ok=True)
    for child in (root / "Dane").iterdir():
        dst = dane_root / child.name
        if child.is_dir():
            shutil.copytree(child, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(child, dst)

print(f"Utworzono nowy katalog: {target}")
for child in sorted(target.iterdir()):
    print(f" - {child.name}")
