import pandas as pd
import os

COUNTRY_PL = {
    "Polska": "Polska",
    "Dania": "Dania",
    "Czechy": "Czechy",
    "Niemcy": "Niemcy",
    "Holandia": "Holandia",
    "Hiszpania": "Hiszpania"
}

CATEGORY_TO_EV = {
    "wszystkie": "EV w flocie",
    "procent_wszystkich": "Procent EV w flocie",
    "nowe": "Nowe rejestracje EV",
    "procent_nowych": "Procent nowych rejestracji EV"
}

def process_file(country, filename, ev_col_name):
    df = pd.read_csv(f'Dane/Zrodla_danych/{country}/{filename}.csv')
    if 'Category' in df.columns:
        df = df.rename(columns={'Category': 'Rok'})
    if 'BEV' in df.columns and 'PHEV' in df.columns:
        df[ev_col_name] = df['BEV'] + df['PHEV']
    df['Kraj'] = COUNTRY_PL[country]
    return df[['Rok', 'Kraj', ev_col_name]]

def extract_vehicles_number_new_regestration_and_percentage(*countries):
    all_data = []
    for country in countries:
        for file_key, ev_col_name in CATEGORY_TO_EV.items():
            df = process_file(country, file_key, ev_col_name)
            all_data.append(df)
    zbiorczy = pd.concat(all_data, ignore_index=True)

    # Pivot: jeden wiersz dla każdego roku i kraju, kategorie jako kolumny
    zbiorczy_pivot = zbiorczy.pivot_table(
        index=['Rok', 'Kraj'],
        values=list(CATEGORY_TO_EV.values()),
        aggfunc='first'
    ).reset_index()

    zbiorczy_pivot.to_csv('Dane/Uporzadkowane_dane/pojazdy_wszystkie_kraje.csv', index=False)
    print("Zbiorczy plik utworzony: pojazdy_wszystkie_kraje.csv")