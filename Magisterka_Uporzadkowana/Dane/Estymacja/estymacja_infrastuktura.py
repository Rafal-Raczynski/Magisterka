import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

def estymacja_infrastruktury_x5():
    # 1. Wczytanie danych historycznych
    dane_ladowarki = """Kraj,Rok,Liczba_Ladowarek
Polska,2020,3050
Polska,2021,10794
Polska,2022,11542
Polska,2023,20247
Polska,2024,32839
Polska,2025,52841"""

    df_hist = pd.read_csv(io.StringIO(dane_ladowarki))
    
    lata_hist = df_hist['Rok'].values
    ladowarki_hist = df_hist['Liczba_Ladowarek'].values
    
    # Populacja Polski (założenie stałe lub delikatnie spadające, tu dla uproszczenia stałe 36.5 mln)
    populacja_pl = 36500000
    
    # Przeliczenie historii na wskaźnik X5 (na 100k mieszkańców)
    x5_hist = (ladowarki_hist / populacja_pl) * 100000
    df_hist['X5_Ladowarki_100k'] = np.round(x5_hist, 1)

    # 2. STATYSTYKA: Regresja Wielomianowa 2. stopnia (Parabola)
    # Łapie ona "przyspieszenie" w budowie infrastruktury
    wsp_wielomianu = np.polyfit(lata_hist, ladowarki_hist, 2)
    
    # 3. PROGNOZA (2025 - 2040)
    lata_prog = np.arange(2025, 2041)
    
    # Wyliczenie surowych wartości z wielomianu
    ladowarki_prog_surowe = np.polyval(wsp_wielomianu, lata_prog)
    
    # KOTWICZENIE (aby usunąć mikroskopijny uskok statystyczny w 2025 r.)
    różnica_2025 = ladowarki_hist[-1] - ladowarki_prog_surowe[0]
    ladowarki_prog_final = ladowarki_prog_surowe + różnica_2025
    
    # Przeliczenie prognozy na wskaźnik X5
    x5_prog = (ladowarki_prog_final / populacja_pl) * 100000

    # 4. Złożenie wyników
    df_wyniki = pd.DataFrame({
        'Rok': lata_prog,
        'Prognozowana_Liczba_Ladowarek': np.round(ladowarki_prog_final).astype(int),
        'X5_Ladowarki_100k': np.round(x5_prog, 1)
    })

    # 5. Wizualizacja profesjonalna
    plt.figure(figsize=(12, 6))
    
    # Rysowanie historii (X5)
    plt.plot(df_hist['Rok'], df_hist['X5_Ladowarki_100k'], 
             color='gray', marker='s', linestyle='-', label='Historia (Wskaźnik X5)')
    
    # Rysowanie prognozy (X5)
    plt.plot(df_wyniki['Rok'], df_wyniki['X5_Ladowarki_100k'], 
             color='#0277bd', marker='o', linewidth=3, label='Prognoza (Regresja Wielomianowa 2. stopnia)')
    
    plt.axvline(x=2025, color='red', linestyle=':', label='Start prognozy (2025)')
    
    # Dodanie adnotacji w kluczowych latach na wykresie
    kluczowe_lata = [2025, 2030, 2035, 2040]
    for r in kluczowe_lata:
        val = df_wyniki.loc[df_wyniki['Rok'] == r, 'X5_Ladowarki_100k'].values[0]
        plt.annotate(f'{val:.1f}', xy=(r, val), xytext=(-15, 10), 
                     textcoords='offset points', ha='center', color='black', fontweight='bold')

    plt.title('Prognoza wskaźnika X5 (Liczba ładowarek na 100 tys. mieszkańców w Polsce)', pad=15)
    plt.xlabel('Rok')
    plt.ylabel('Ładowarki na 100k mieszkańców')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(np.arange(2020, 2041, 2), rotation=45)
    plt.legend()
    plt.tight_layout()
    # plt.savefig("Dane/Estymacyjne_dane/wykres_x5_infrastruktura.png", dpi=300)
    plt.show()

    return df_wyniki

if __name__ == "__main__":
    wyniki_x5 = estymacja_infrastruktury_x5()
    print(wyniki_x5.to_string(index=False))
    wyniki_x5.to_csv("Dane/Estymacyjne_dane/prognoza_infrastruktura_x5.csv", index=False)