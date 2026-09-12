import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def generuj_dynamiczna_prognoze_ev():
    # 1. Zakres lat
    lata = np.arange(2025, 2041)
    
    # 2. Zmienne wejściowe (Trendy prognostyczne)
    x2 = np.linspace(22500, 35000, len(lata)) # PPS_X2
    
    # X3: Relacja kosztów (Spadek - prąd staje się relatywnie tańszy przez ETS2)
    x3 = np.linspace(0.39, 0.20, len(lata)) 
    
    # X4: Dotacje (Płynne wygaszanie z 2.0 do 0, aby uniknąć nagłych załamań wykresu)
    x4 = np.linspace(2, 0, len(lata))
    
    # X5: Infrastruktura (Planowana rozbudowa: liczba ładowarek na 100k mieszkańców)
    # Zakładamy wzrost z obecnych ok. 15 do 120 w 2035 roku
    x5 = np.linspace(15, 120, len(lata))

    # 3. RÓWNANIE Z TWOJEJ REGRESJI PANELOWEJ
    # Y = 3.5992 + 0.0004*X2 - 17.965*X3 + 2.5078*X4 + 0.0129*X5
    # Obliczamy 'z' (linear predictor), który posłuży do transformacji logistycznej
    z = (3.5992 + 
         0.0004 * x2 - 
         17.965 * x3 + 
         2.5078 * x4 + 
         0.0129 * x5)
    
    # 4. TRANSFORMACJA LOGISTYCZNA (Krzywa S)
    # Pozwala uzyskać dynamikę rynkową i dojście do 100%
    L = 100  # Pułap 100%
    k = 0.3  # Tempo adaptacji
    z_mid = 25  # Punkt przegięcia
    
    y_logit = L / (1 + np.exp(-k * (z - z_mid)))
    
    # Startujemy od realnego poziomu ok. 6.3% i ograniczamy do 100%
    y_final = np.clip(y_logit, 6.3, 100)
    
    # Wymuszenie 100% od roku zakazu sprzedaży aut spalinowych
    y_final[lata >= 2035] = 100

    # 5. Tworzenie tabeli
    df = pd.DataFrame({
        'Rok': lata,
        'PPS_X2': x2.round(0),
        'RelacjaKosztow_X3': x3.round(3),
        'Dotacje_X4': x4.round(2),
        'Infrastruktura_X5': x5.round(1),
        'Udzial_EV_Y_procent': y_final.round(2)
    })

    # 6. Wykres
    plt.figure(figsize=(12, 7))
    plt.fill_between(df['Rok'], df['Udzial_EV_Y_procent'], alpha=0.15, color='#2e7d32')
    
    plt.plot(df['Rok'], df['Udzial_EV_Y_procent'], 
             marker='o', markersize=8, color='#1b5e20', 
             linewidth=3, label='Prognoza dyfuzji rynkowej EV')

    # Linia zakazu 2035
    plt.axvline(x=2035, color='#d32f2f', linestyle='--', linewidth=2)
    plt.text(2035.2, 50, 'ZAKAZ SPRZEDAŻY ICE (UE)', color='#d32f2f', rotation=90, fontweight='bold')

    # Adnotacje
    for r in [2025, 2030, 2035, 2040]:
        val = df.loc[df['Rok'] == r, 'Udzial_EV_Y_procent'].values[0]
        plt.annotate(f'{val}%', xy=(r, val), xytext=(0, 10), 
                     textcoords='offset points', ha='center', fontweight='bold')

    plt.title('Finalna prognoza udziału EV na podstawie modelu PanelOLS', fontsize=14, pad=20)
    plt.ylabel('Udział w nowych rejestracjach (%)', fontsize=12)
    plt.ylim(-5, 110)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

    return df

if __name__ == "__main__":
    wynik = generuj_dynamiczna_prognoze_ev()
    print(wynik.to_string(index=False))