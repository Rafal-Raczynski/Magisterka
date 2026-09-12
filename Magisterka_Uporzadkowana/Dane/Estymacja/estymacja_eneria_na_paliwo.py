import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

def estymacja_x3_oficjalna_strategia():
    # 1. Załadowanie danych historycznych PALIWA (Polska)
    dane_paliwo = """Rok,Cena_Paliwa_EUR
2005,0.996
2006,1.019
2007,1.114
2008,1.246
2009,0.956
2010,1.135
2011,1.243
2012,1.364
2013,1.307
2014,1.264
2015,1.110
2016,0.996
2017,1.079
2018,1.159
2019,1.163
2020,1.000
2021,1.200
2022,1.421
2023,1.435
2024,1.479
2025,1.402"""

    # Załadowanie danych historycznych ENERGII (Polska)
    dane_energia = """Rok,Cena_Energii_EUR
2007,0.138
2008,0.128
2009,0.121
2010,0.136
2011,0.141
2012,0.147
2013,0.146
2014,0.141
2015,0.143
2016,0.134
2017,0.145
2018,0.140
2019,0.136
2020,0.149
2021,0.156
2022,0.153
2023,0.197
2024,0.228
2025,0.256"""

    df_p = pd.read_csv(io.StringIO(dane_paliwo))
    df_e = pd.read_csv(io.StringIO(dane_energia))

    # Połączenie danych historycznych (wspólne lata 2007-2025)
    df_hist = pd.merge(df_p, df_e, on='Rok', how='inner').sort_values('Rok')

    lata_hist = df_p['Rok'].values
    paliwo_hist = df_p['Cena_Paliwa_EUR'].values

    # 2. PROGNOZA PALIWA (Trend skotwiczony w 2025 r. + ETS2)
    wsp_paliwo = np.polyfit(lata_hist, paliwo_hist, 1)
    tempo_wzrostu_paliwo = wsp_paliwo[0]
    rzeczywiste_paliwo_2025 = paliwo_hist[-1]

    lata_prog = np.arange(2025, 2041)
    paliwo_prog_baza = np.array([rzeczywiste_paliwo_2025 + tempo_wzrostu_paliwo * i for i in range(len(lata_prog))])
    
    # Narzut ETS2 dla transportu
    ets2_impact_eur = np.linspace(0.00, 0.65, len(lata_prog))
    paliwo_prog_final = paliwo_prog_baza + ets2_impact_eur

    # 3. PROGNOZA ENERGII (Dane oficjalne KPEiK / MKIŚ - Scenariusz WAM dla gospodarstw domowych)
    kurs_eur_pln = 4.25 # Kurs przyjęty do ujednolicenia modelu
    
    # Punkty węzłowe odczytane z infografiki (w PLN/kWh)
    lata_mkis = [2025, 2030, 2035, 2040]
    ceny_pln_kwh = [1.18, 1.12, 0.97, 0.83] 
    
    # Przeliczenie na EUR/kWh
    ceny_eur_kwh = [cena / kurs_eur_pln for cena in ceny_pln_kwh]

    # Płynna interpolacja liniowa dla wszystkich brakujących lat
    energia_prog_final = np.interp(lata_prog, lata_mkis, ceny_eur_kwh)

    # 4. WYLICZENIE WSKAŹNIKA X3 (EV / ICE)
    zuzycie_ev = 18
    zuzycie_ice = 7
    
    # Wyliczenie X3 dla historii (2007-2025)
    x3_hist = (df_hist['Cena_Energii_EUR'].values * zuzycie_ev) / (df_hist['Cena_Paliwa_EUR'].values * zuzycie_ice)
    
    # Wyliczenie X3 dla prognozy (2025-2040)
    x3_prog = (energia_prog_final * zuzycie_ev) / (paliwo_prog_final * zuzycie_ice)

    # 5. DataFrame
    df_wyniki = pd.DataFrame({
        'Rok': lata_prog,
        'Cena_Paliwa_EUR': np.round(paliwo_prog_final, 3),
        'Cena_Pradu_EUR': np.round(energia_prog_final, 3),
        'Koszt_100km_EV_EUR': np.round(energia_prog_final * zuzycie_ev, 2),
        'Koszt_100km_ICE_EUR': np.round(paliwo_prog_final * zuzycie_ice, 2),
        'X3_Wskaznik_Relatywny': np.round(x3_prog, 4)
    })

    # 6. Wizualizacja
    plt.figure(figsize=(12, 6))
    
    # Rysowanie linii historycznej (szara)
    plt.plot(df_hist['Rok'], x3_hist, color='gray', marker='.', linestyle='-', label='Historia (Zanotowany X3 2007-2025)')
    
    # Rysowanie linii prognozy (zielona)
    plt.plot(df_wyniki['Rok'], df_wyniki['X3_Wskaznik_Relatywny'], 
             color='#1b5e20', marker='o', linewidth=3, label='Prognoza X3 (Paliwo z ETS2 vs Energia OZE/MKIŚ)')
    
    # Adnotacje dla punktów węzłowych MKIŚ (tylko na prognozie)
    for r in lata_mkis:
        val = df_wyniki.loc[df_wyniki['Rok'] == r, 'X3_Wskaznik_Relatywny'].values[0]
        plt.annotate(f'{val:.2f}', xy=(r, val), xytext=(0, -15), textcoords='offset points', ha='center', color='black')

    plt.axvline(x=2025, color='red', linestyle=':', label='Start prognozy (2025)')
    
    plt.title('Wskaźnik X3: Relacja kosztów ładowania EV do tankowania ICE na przestrzeni lat', pad=15)
    plt.xlabel('Rok')
    plt.ylabel('Koszt 100km EV / Koszt 100km ICE')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Ustawienie etykiet osi X co 2 lata dla lepszej czytelności
    plt.xticks(np.arange(2007, 2041, 2), rotation=45)
    
    plt.legend()
    plt.tight_layout()
    # plt.savefig("Dane/Estymacyjne_dane/wykres_x3_hybryda.png", dpi=300)
    plt.show()

    return df_wyniki

if __name__ == "__main__":
    wyniki_x3 = estymacja_x3_oficjalna_strategia()
    print(wyniki_x3.to_string(index=False))
    wyniki_x3.to_csv("Dane/Estymacyjne_dane/prognoza_x3_koszt_100km.csv", index=False)