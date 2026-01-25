import pandas as pd
import statsmodels.api as sm

if __name__ == "__main__":
    folder = "Dane/Uporzadkowane_dane/"
    df = pd.read_csv(folder + "tabela_zbiorcza.csv")

    # Rok
    df['Rok (X1)'] = df['Rok'].astype(int)

    # PKB per capita (PPS)
    if 'PKB per capita (PPS)' in df.columns:
        df['PKB per capita (PPS) (X2)'] = df['PKB per capita (PPS)']
    elif 'roczne_pkb_per_capita' in df.columns:
        df['PKB per capita (PPS) (X2)'] = df['roczne_pkb_per_capita']
    else:
        df['PKB per capita (PPS) (X2)'] = None

    # Wskaźnik cen energii do paliwa
    if 'Cena energii (EUR/kWh)' in df.columns and 'Cena paliwa (EUR/litr)' in df.columns:
        df['Wskaźnik cen energii/paliwa (X3)'] = 18 * df['Cena energii (EUR/kWh)'] / (7 * df['Cena paliwa (EUR/litr)'])
    else:
        df['Wskaźnik cen energii/paliwa (X3)'] = None

    # Dotacje
    if 'Dotacja' in df.columns:
        df['Dotacje (X4)'] = df['Dotacja']
    elif 'dotacje' in df.columns:
        df['Dotacje (X4)'] = df['dotacje']
    else:
        df['Dotacje (X4)'] = None

    # Liczba ładowarek / liczba samochodów EV we flocie
    if 'Liczba Ładowarek' in df.columns and 'EV w flocie' in df.columns:
        df['Ładowarki na EV (X5)'] = df['Liczba Ładowarek'] / df['EV w flocie']
    else:
        df['Ładowarki na EV (X5)'] = None

    df['Procent nowych rejestracji EV (Y)'] = df['Procent nowych rejestracji EV']

    # Wybierz tylko potrzebne kolumny
    tabela_model = df[['Kraj',
                       'Rok (X1)',
                       'PKB per capita (PPS) (X2)',
                       'Wskaźnik cen energii/paliwa (X3)',
                       'Dotacje (X4)',
                       'Ładowarki na EV (X5)',
                       'Procent nowych rejestracji EV (Y)']].copy()

    # Usuń wiersze z brakującymi danymi
    tabela_model = tabela_model.dropna(subset=[
        'Rok (X1)',
        'PKB per capita (PPS) (X2)',
        'Wskaźnik cen energii/paliwa (X3)',
        'Dotacje (X4)',
        'Ładowarki na EV (X5)',
        'Procent nowych rejestracji EV (Y)'
    ])

    print(tabela_model.head())

    # Zapisz do pliku
    tabela_model.to_csv(folder + "tabela_model.csv", index=False)
    print("Tabela modelowa zapisana jako tabela_model.csv")

    # Tabela korelacji
    corr_table = tabela_model[
        ['Rok (X1)',
         'PKB per capita (PPS) (X2)',
         'Wskaźnik cen energii/paliwa (X3)',
         'Dotacje (X4)',
         'Ładowarki na EV (X5)',
         'Procent nowych rejestracji EV (Y)']
    ].corr()
    print("\nTabela korelacji:")
    print(corr_table)
    corr_table.to_csv(folder + "tabela_korelacji.csv")

    # Regresja liniowa Y ~ X1 + X2 + X3 + X4 + X5
    X = tabela_model[
        ['Rok (X1)',
         'PKB per capita (PPS) (X2)',
         'Wskaźnik cen energii/paliwa (X3)',
         'Dotacje (X4)',
         'Ładowarki na EV (X5)']
    ]
    X = sm.add_constant(X)
    y = tabela_model['Procent nowych rejestracji EV (Y)']
    model = sm.OLS(y, X).fit()

    print("\nOpis zależności Y od X1, X2, X3, X4, X5:")
    print(model.summary())

    # Wszystkie statystyki regresji do DataFrame
    summary_df = pd.DataFrame({
        'coef': model.params,
        'std err': model.bse,
        't': model.tvalues,
        'p': model.pvalues,
        'ci_lower': model.conf_int()[0],
        'ci_upper': model.conf_int()[1]
    })
    print("\nStatystyki regresji (coef, std err, t, p, ci_lower, ci_upper):")
    print(summary_df)

    # Zapisz statystyki do pliku
    summary_df.to_csv(folder + "statystyki_regresji.csv")