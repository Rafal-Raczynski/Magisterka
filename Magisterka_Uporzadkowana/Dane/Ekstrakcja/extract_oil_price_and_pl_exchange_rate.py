import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

COUNTRY_CODES = {
    "Poland": "PL",
    "Germany": "DE",
    "France": "FR",
    "Czechia": "CZ",
    "Slovakia": "SK",
    "Austria": "AT",
    "Hungary": "HU",
    "Lithuania": "LT",
    "Latvia": "LV",
    "Estonia": "EE",
    "Denmark": "DK",
    "Netherlands": "NL",
    "Spain": "ES",
    # Dodaj inne kraje według potrzeb
}

# Słownik tłumaczeń na polski
COUNTRY_PL = {
    "Poland": "Polska",
    "Germany": "Niemcy",
    "France": "Francja",
    "Czechia": "Czechy",
    "Slovakia": "Słowacja",
    "Austria": "Austria",
    "Hungary": "Węgry",
    "Lithuania": "Litwa",
    "Latvia": "Łotwa",
    "Estonia": "Estonia",
    "Denmark": "Dania",
    "Netherlands": "Holandia",
    "Spain": "Hiszpania",
    # Dodaj inne kraje według potrzeb
}

def extract_oil_price_and_pl_exchange_rate(*country_names):
    data = pd.read_excel('Dane/Zrodla_danych/Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx')
    all_countries = []

    for country_name in country_names:
        if country_name not in COUNTRY_CODES:
            print(f"Kraj '{country_name}' nie jest obsługiwany.")
            continue

        code = COUNTRY_CODES[country_name]
        df = pd.DataFrame(data.iloc[2:, 0], columns=[data.columns[0]])
        df.rename(columns={df.columns[0]: 'Data'}, inplace=True)
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.dropna(subset=['Data']).reset_index(drop=True)

        euro_col = f"{code}_price_with_tax_euro95"
        if euro_col not in data.columns:
            print(f"Brak kolumny z ceną paliwa w euro dla kraju {country_name} ({euro_col})")
            continue

        # Cena za 1 litr (dzielimy przez 1000)
        df['Cena paliwa (EUR/litr)'] = data[euro_col].iloc[2:2+len(df)].astype(float).values / 1000
        df['Rok'] = df['Data'].dt.year
        df['Kraj'] = COUNTRY_PL[country_name]

        roczne_ceny = df.groupby(['Rok', 'Kraj'])[['Cena paliwa (EUR/litr)']].mean().reset_index()
        all_countries.append(roczne_ceny)

        # Kurs PLN/EUR tylko dla Polski
        if country_name == "Poland":
            df['Kurs PLN/EUR'] = data['PL_exchange_rate'].iloc[2:2+len(df)].astype(float).values
            roczne_kursy = df.groupby('Rok')[['Kurs PLN/EUR']].mean().reset_index()
            roczne_kursy.to_csv('Dane/Uporzadkowane_dane/roczne_kursy_PLN.csv', index=False)

        print(f"Wyeksportowano roczne zestawienia dla {COUNTRY_PL[country_name]} ({code})")

    # Zbiorczy plik dla wszystkich krajów
    if all_countries:
        zbiorczy = pd.concat(all_countries, ignore_index=True)
        zbiorczy.to_csv('Dane/Uporzadkowane_dane/roczne_ceny_paliwa_euro_zbiorczo.csv', index=False)
        print("Zbiorczy plik utworzony: roczne_ceny_paliwa_euro_zbiorczo.csv")
  