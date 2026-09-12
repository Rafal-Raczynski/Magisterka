import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def generuj_finalna_prognoze_magisterska():
    # 1. Zakres lat prognozy
    lata = np.arange(2025, 2041)
    
    # 2. Trendy zmiennych objaśniających dla Polski (pobierane z plików)
    # X2: PPS - z pliku prognoza_aic_per_capita_polska.csv
    df_aic = pd.read_csv("Dane/Estymacyjne_dane/prognoza_aic_per_capita_polska.csv")
    x2 = df_aic[df_aic['Rok'] >= 2025]['Prognozowany AIC per capita (PPS)'].values
    
    # X3: Relacja kosztów - z pliku prognoza_x3_koszt_100km.csv
    df_x3 = pd.read_csv("Dane/Estymacyjne_dane/prognoza_x3_koszt_100km.csv")
    x3 = df_x3[df_x3['Rok'] >= 2025]['X3_Wskaznik_Relatywny'].values

    # X4: Dotacje - z pliku prognoza_dotacje.csv
    df_dotacje = pd.read_csv("Dane/Estymacyjne_dane/prognoza_dotacje.csv")
    x4 = df_dotacje[df_dotacje['Rok'] >= 2025]['Dotacja'].values
    
    # X5: Infrastruktura - Ambitna rozbudowa (pozostaje z np.linspace)
    x5 = np.linspace(89.9, 1500, len(lata))

    # 3. Zaktualizowane parametry z modelu PanelOLS (Logit)
    stala_polska = -5.3058
    b1 = 0.00007794  # PKB per capita (PPS)
    b2 = -1.1886     # Wskaźnik cen energii/paliwa
    b3 = 0.2964      # Dotacje
    b4 = 0.0002      # Ładowarki na mieszkańców

    # Równanie logitowe (z)
    z = stala_polska + (b1 * x2) + (b2 * x3) + (b3 * x4) + (b4 * x5)
    
    # 4. Transformacja Sigmoidalna (czysta statystyka, zastępuje L, k, z_mid)
    y_frac = 1 / (1 + np.exp(-z))
    
    # Zamiana ułamka na procenty
    y_final = y_frac * 100
    
    # Logika zakazu 2035 pozostaje bez zmian
    y_final[lata >= 2035] = 100

    # 5. Przygotowanie danych wynikowych
    df = pd.DataFrame({
        'Rok': lata,
        'PPS_X2': x2.astype(int),
        'RelacjaKosztow_X3': x3.round(3),
        'Dotacje_X4': x4.round(2),
        'Infrastruktura_X5': x5.round(1),
        'Prognozowany_Udzial_EV_%': y_final.round(2)
    })

    # 6. Wizualizacja profesjonalna
    plt.figure(figsize=(14, 8))
    
    # Stylizacja wykresu
    plt.fill_between(df['Rok'], df['Prognozowany_Udzial_EV_%'], color='seagreen', alpha=0.1)
    plt.plot(df['Rok'], df['Prognozowany_Udzial_EV_%'], marker='o', color='#1b5e20', 
             linewidth=3, label='Prognozowany udział EV (Model Panel-Logit)')

    # Linia graniczna 2035
    plt.axvline(x=2035, color='#c62828', linestyle='--', linewidth=2, label='Zakaz rejestracji aut ICE w UE')
    plt.text(2035.2, 50, 'ZAKAZ SPRZEDAŻY ICE', color='#c62828', fontweight='bold', rotation=90)

    # Adnotacje dla kluczowych punktów
    kluczowe_lata = [2025, 2030, 2035, 2040]
    for r in kluczowe_lata:
        val = df.loc[df['Rok'] == r, 'Prognozowany_Udzial_EV_%'].values[0]
        plt.annotate(f'{val}%', xy=(r, val), xytext=(0, 12), 
                     textcoords='offset points', ha='center', fontweight='bold', color='#1b5e20')

    plt.title('Prognoza udziału samochodów elektrycznych w nowych rejestracjach (Polska 2025-2040)', fontsize=16, pad=20)
    plt.ylabel('Udział w rynku (%)', fontsize=12)
    plt.ylim(-5, 110)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    
    # Zapis wykresu
    # plt.savefig("Dane/Uporzadkowane_dane/wykres_prognozy_final.png", dpi=300)
    plt.show()

    return df

if __name__ == "__main__":
    prognoza = generuj_finalna_prognoze_magisterska()
    print(prognoza.to_string(index=False))
    # prognoza.to_csv("Dane/Uporzadkowane_dane/finalna_prognoza_EV_Polska.csv", index=False)