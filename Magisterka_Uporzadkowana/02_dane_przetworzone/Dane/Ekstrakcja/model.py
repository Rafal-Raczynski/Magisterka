import pandas as pd

if __name__ == "__main__":
    folder = "Dane/Uporzadkowane_dane/"
    files = [
        "dotacje.csv",
        "pojazdy_wszystkie_kraje.csv",
        "roczne_aic_per_capita_real.csv",
        "roczne_ceny_energii.csv",
        "roczne_ceny_paliwa_euro_zbiorczo.csv",
        "roczne_pkb_per_capita.csv",
        "roczne_ladowarki.csv"
    ]
    dfs = [pd.read_csv(folder + f) for f in files]

    # Usuń duplikaty
    for i, df in enumerate(dfs):
        dfs[i] = df.drop_duplicates(subset=['Rok', 'Kraj'])
        dfs[i]['Rok'] = dfs[i]['Rok'].astype(str)
        dfs[i]['Kraj'] = dfs[i]['Kraj'].astype(str)

    # Joinuj po 'Rok' i 'Kraj'
    df_join = dfs[0]
    for df in dfs[1:]:
        df_join = df_join.merge(df, on=['Rok', 'Kraj'], how='outer')

    # Posortuj i ustaw kolejność kolumn
    df_join = df_join.sort_values(['Kraj', 'Rok']).reset_index(drop=True)
    cols = ['Kraj', 'Rok'] + [c for c in df_join.columns if c not in ['Kraj', 'Rok']]
    df_join = df_join[cols]

    print(df_join.head())
    df_join.to_csv(folder + "tabela_zbiorcza.csv", index=False)