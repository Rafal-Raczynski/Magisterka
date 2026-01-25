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

def extract_aic_per_capita(*countries):
    # Wczytaj dane
    data = pd.read_csv('Dane/Zrodla_danych/prc_ppp_ind__custom_19617759_linear.csv')
    
    # Filtrowanie po walucie i krajach
    filtered = data[(data['na_item'] != 'Volume indices of real expenditure per capita (in PPS_EU27_2020=100)') & (data['geo'].isin(countries))]

    # Zmień nazwy kolumn na polskie i przemapuj kraje
    filtered = filtered.rename(columns={
        'TIME_PERIOD': 'Rok',
        'geo': 'Kraj',
        'OBS_VALUE': 'AIC per capita (PPS)'
    })
    filtered['Kraj'] = filtered['Kraj'].map(COUNTRY_PL)

    # Wyodrębnij tylko rok z kolumny 'Rok' (np. z '2007-S1' -> '2007')
    filtered['Rok'] = filtered['Rok'].astype(str).str[:4]

    # Usuń wiersze z brakującą wartością AIC per capita
    filtered = filtered.dropna(subset=['AIC per capita (PPS)'])

    # Grupuj po roku i kraju, licz średnią
    srednie_roczne = filtered.groupby(['Kraj', 'Rok'], as_index=False)['AIC per capita (PPS)'].mean()
    # Zapisz do pliku
    srednie_roczne.to_csv('Dane/Uporzadkowane_dane/roczne_aic_per_capita_real.csv', index=False)
    print(srednie_roczne)


   