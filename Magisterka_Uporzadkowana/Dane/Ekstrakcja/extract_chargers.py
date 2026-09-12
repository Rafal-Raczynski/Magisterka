import pandas as pd

def extract_chargers(*countries):
    all_data = []
    for country in countries:
        df = pd.read_csv(f'Dane/Zrodla_danych/{country}/ladowarki.csv')
        df = df.rename(columns={'Category': 'Rok'})
        df["Rok"] = df["Rok"].astype(str).str[:4]
        df['Kraj'] = country
        grouped = df.groupby(['Kraj', 'Rok'])[['AC', 'DC']].sum().reset_index()
        grouped['Liczba Ładowarek'] = grouped['AC'] + grouped['DC']
        all_data.append(grouped[['Kraj', 'Rok', 'Liczba Ładowarek']])
    result = pd.concat(all_data, ignore_index=True)
    result.to_csv('Dane/Uporzadkowane_dane/roczne_ladowarki.csv', index=False)
    print(result)

