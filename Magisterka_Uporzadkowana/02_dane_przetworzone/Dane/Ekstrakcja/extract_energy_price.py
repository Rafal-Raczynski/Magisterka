import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

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

def extract_energy_price(*countries):
    # Wczytaj dane
    data = pd.read_csv('Dane/Zrodla_danych/nrg_pc_204__custom_19616155_linear.csv')

    # Filtrowanie po walucie i krajach
    filtered = data[(data['currency'] == 'Euro') & (data['geo'].isin(countries))]

    # Zmień nazwy kolumn na polskie i przemapuj kraje
    filtered = filtered.rename(columns={
        'TIME_PERIOD': 'Rok',
        'geo': 'Kraj',
        'OBS_VALUE': 'Cena energii (EUR/kWh)'
    })
    filtered['Kraj'] = filtered['Kraj'].map(COUNTRY_PL)

    # Wyodrębnij tylko rok z kolumny 'Rok' (np. z '2007-S1' -> '2007')
    filtered['Rok'] = filtered['Rok'].astype(str).str[:4]

    # Usuń wiersze z brakującą wartością ceny
    filtered = filtered.dropna(subset=['Cena energii (EUR/kWh)'])

    # Grupuj po roku i kraju, licz średnią
    srednie_roczne = filtered.groupby(['Kraj', 'Rok'], as_index=False)['Cena energii (EUR/kWh)'].mean()

    # Zapisz do pliku
    srednie_roczne.to_csv('Dane/Uporzadkowane_dane/roczne_ceny_energii.csv', index=False)
    print(srednie_roczne)


