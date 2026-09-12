import pandas as pd
from linearmodels.panel import PanelOLS
import statsmodels.api as sm

if __name__ == "__main__":
    folder = "Dane/Uporzadkowane_dane/"
    df = pd.read_csv(folder + "tabela_zbiorcza.csv")

    # 1. Mapowanie populacji dla krajów
    pop_map = {
        'Czechy': 10910000,
        'Dania': 5990000,
        'Hiszpania': 49130000,
        'Holandia': 18040000,
        'Niemcy': 83580000,
        'Polska': 36500000
    }
    df['Populacja_Ref'] = df['Kraj'].map(pop_map)

    # 2. Przygotowanie zmiennych (X1 - X5)
    df['Rok (X1)'] = df['Rok'].astype(int)

    # PKB per capita (PPS) (X2)
    if 'PKB per capita (PPS)' in df.columns:
        df['PKB per capita (PPS) (X2)'] = df['PKB per capita (PPS)']
    elif 'roczne_pkb_per_capita' in df.columns:
        df['PKB per capita (PPS) (X2)'] = df['roczne_pkb_per_capita']

    # Wskaźnik cen energii do paliwa (X3)
    if 'Cena energii (EUR/kWh)' in df.columns and 'Cena paliwa (EUR/litr)' in df.columns:
        df['Wskaźnik cen energii/paliwa (X3)'] = 18 * df['Cena energii (EUR/kWh)'] / (7 * df['Cena paliwa (EUR/litr)'])

    # Dotacje (X4)
    if 'Dotacja' in df.columns:
        df['Dotacje (X4)'] = df['Dotacja']
    elif 'dotacje' in df.columns:
        df['Dotacje (X4)'] = df['dotacje']

    # Ładowarki na 100k mieszkańców (X5) - Nowa definicja
    if 'Liczba Ładowarek' in df.columns:
        df['Ładowarki na mieszkańców (X5)'] = (df['Liczba Ładowarek'] / df['Populacja_Ref']) * 100000

    df['Procent nowych rejestracji EV (Y)'] = df['Procent nowych rejestracji EV']

    # 3. Wybór kolumn i czyszczenie danych
    kolumny = [
        'Kraj', 'Rok (X1)', 'PKB per capita (PPS) (X2)', 
        'Wskaźnik cen energii/paliwa (X3)', 'Dotacje (X4)', 
        'Ładowarki na mieszkańców (X5)', 'Procent nowych rejestracji EV (Y)'
    ]
    
    tabela_model = df[kolumny].dropna().copy()

    # Zapis tabeli modelowej
    tabela_model.to_csv(folder + "tabela_model.csv", index=False)
    print("Tabela modelowa zapisana.")

    # 4. Tabela korelacji
    corr_table = tabela_model.drop('Kraj', axis=1).corr()
    corr_table.to_csv(folder + "tabela_korelacji.csv")
    print("Tabela korelacji zapisana.")

    # 5. Regresja Panelowa (PanelOLS)
    # Ustawienie indeksu dla danych panelowych
    tabela_model = tabela_model.set_index(['Kraj', 'Rok (X1)'])
    
    y = tabela_model['Procent nowych rejestracji EV (Y)']
    X = tabela_model[['PKB per capita (PPS) (X2)', 'Wskaźnik cen energii/paliwa (X3)', 'Dotacje (X4)', 'Ładowarki na mieszkańców (X5)']]
    X = sm.add_constant(X)

    # Model z efektami stałymi (Entity Effects)
    model = PanelOLS(y, X, entity_effects=True)
    results = model.fit()

    print(results.summary)

    # 6. Zapis statystyk do CSV (dostosowane do formatu PanelOLS)
    summary_df = pd.DataFrame({
        'coef': results.params,
        'std err': results.std_errors,
        't': results.tstats,
        'p': results.pvalues,
        'ci_lower': results.conf_int().iloc[:, 0],
        'ci_upper': results.conf_int().iloc[:, 1]
    })

    summary_df.to_csv(folder + "statystyki_regresji_panelowej.csv")
    print(f"\nStatystyki zapisane w: {folder}statystyki_regresji_panelowej.csv")