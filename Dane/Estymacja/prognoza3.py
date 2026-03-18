import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def generuj_finalna_prognoze_magisterska():
    # 1. Zakres lat prognozy
    lata = np.arange(2025, 2041)
    
    # 2. Wczytanie zmiennych objaśniających (tutaj z ujednoliconych wektorów/plików)
    df_aic = pd.read_csv("Dane/Estymacyjne_dane/prognoza_aic_per_capita_polska.csv")
    x2 = df_aic[df_aic['Rok'] >= 2025]['Prognozowany AIC per capita (PPS)'].values
    
    df_x3 = pd.read_csv("Dane/Estymacyjne_dane/prognoza_x3_koszt_100km.csv")
    x3 = df_x3[df_x3['Rok'] >= 2025]['X3_Wskaznik_Relatywny'].values

    # Wygładzone dotacje (zgodnie z poprzednimi ustaleniami: liniowy spadek do 0 w 2035)
    x4_do_2035 = np.linspace(2.0, 0.0, 11) 
    x4_po_2035 = np.zeros(5) 
    x4 = np.concatenate([x4_do_2035, x4_po_2035])
    
    df_x5 = pd.read_csv("Dane/Estymacyjne_dane/prognoza_infrastruktura_x5.csv")
    x5 = df_x5[df_x5['Rok'] >= 2025]['X5_Ladowarki_100k'].values

    # 3. Zaktualizowane parametry z modelu PanelOLS (Logit)
    stala_polska = -5.3058
    b1 = 0.00007794  
    b2 = -1.1886     
    b3 = 0.2964      
    b4 = 0.0002      

    # Obliczenie surowego wskaźnika (z_raw)
    z_raw = stala_polska + (b1 * x2) + (b2 * x3) + (b3 * x4) + (b4 * x5)
    
    # --- 3a. NOWA KALIBRACJA (Uwzględniająca rewizję UE: cel 90% w 2035) ---
    # W 2025 (indeks 0) rynek startuje z realnych 5.7%.
    # W 2035 (indeks 10) osiągamy nowy unijny pułap 90% (zostawiając 10% dla ICE/PHEV).
    
    logit_2025_cel = -2.806 # ln(0.057 / (1 - 0.057))
    logit_2035_cel = 2.197  # ln(0.900 / (1 - 0.900))
    
    z_raw_2025 = z_raw[0]  
    z_raw_2035 = z_raw[10] 
    
    # Wyliczamy mnożnik (k) i przesunięcie (shift)
    k_idealne = (logit_2035_cel - logit_2025_cel) / (z_raw_2035 - z_raw_2025)
    shift_idealne = logit_2025_cel - (k_idealne * z_raw_2025)
    
    # Aplikujemy wygładzone parametry
    z_skalibrowane = (k_idealne * z_raw) + shift_idealne
    
    # 4. Transformacja Sigmoidalna (Model Dyfuzji)
    y_frac = 1 / (1 + np.exp(-z_skalibrowane))
    y_final = y_frac * 100
    
    # Brak wymuszenia 100% po 2035! Krzywa naturalnie asymptotycznie spłaszczy się nad 90%.

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
    
    plt.fill_between(df['Rok'], df['Prognozowany_Udzial_EV_%'], color='seagreen', alpha=0.1)
    plt.plot(df['Rok'], df['Prognozowany_Udzial_EV_%'], marker='o', color='#1b5e20', 
             linewidth=3, label='Prognoza EV (Skalibrowana pod nowy cel UE)')

    # Zaktualizowana linia graniczna 2035
    plt.axvline(x=2035, color='#e65100', linestyle='--', linewidth=2, label='Nowy cel UE (90% redukcji emisji)')
    plt.text(2035.2, 50, 'CEL UE: 90% EV / 10% ICE', color='#e65100', fontweight='bold', rotation=90)

    # Adnotacje
    kluczowe_lata = [2025, 2030, 2035, 2040]
    for r in kluczowe_lata:
        val = df.loc[df['Rok'] == r, 'Prognozowany_Udzial_EV_%'].values[0]
        plt.annotate(f'{val}%', xy=(r, val), xytext=(0, 12), 
                     textcoords='offset points', ha='center', fontweight='bold', color='#1b5e20')

    plt.title('Prognoza udziału aut elektrycznych po rewizji celów klimatycznych UE z 2025 r.', fontsize=16, pad=20)
    plt.ylabel('Udział w rynku (%)', fontsize=12)
    plt.ylim(-5, 110)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.show()

    return df

if __name__ == "__main__":
    prognoza = generuj_finalna_prognoze_magisterska()
    print(prognoza.to_string(index=False))