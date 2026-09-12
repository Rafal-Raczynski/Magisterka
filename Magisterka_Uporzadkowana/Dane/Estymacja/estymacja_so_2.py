import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.optimize import curve_fit

def sigmoid(x, L, k, x0):
    return L / (1 + np.exp(-k * (x - x0)))

def estymacja_os():
    data = pd.read_csv("Dane/Uporzadkowane_dane/TRAN_1733_CREL_20260125154356.csv", sep=';')
    print(data.head())
    polska = data[(data['Rok'] >= 2005)  & (data['Rok'] <= 2023)]
    print(polska)

    X = polska['Rok'].values
    y = polska['Wartosc'].values

    # Dopasowanie krzywej logistycznej (sigmoidalnej)
    p0 = [max(y)*1.2, 0.1, np.median(X)]  # początkowe wartości parametrów
    popt, _ = curve_fit(sigmoid, X, y, p0, maxfev=10000)
    L, k, x0 = popt

    # Obliczanie błędów dopasowania na danych historycznych
    y_pred = sigmoid(X, L, k, x0)
    mse = mean_squared_error(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    print(f"Średni błąd kwadratowy (MSE): {mse:.2f}")
    print(f"Średni błąd bezwzględny (MAE): {mae:.2f}")

    # Przewidywanie do 2040
    lata = np.arange(X.min(), 2041)
    prognoza = sigmoid(lata, L, k, x0)

    plt.figure(figsize=(10, 5))
    plt.plot(X, y, marker='o', label='Dane historyczne')
    plt.plot(lata, prognoza, 'r--', label='Prognoza (krzywa S) do 2040')
    plt.title('Liczba samochodów osobowych w Polsce na przestrzeni lat')
    plt.xlabel('Rok')
    plt.ylabel('Liczba samochodów osobowych')
    plt.xticks(lata, rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Eksport do CSV
    df_prognoza = pd.DataFrame({
        'Kraj': ['Polska'] * len(lata),
        'Rok': lata,
        'Prognozowana liczba samochodów osobowych': prognoza
    })
    df_prognoza.to_csv('Dane/Estymacyjne_dane/prognoza_liczba_samochodow_osobowych_polska_sigmoid.csv', index=False)

if __name__ == "__main__":
    estymacja_os()