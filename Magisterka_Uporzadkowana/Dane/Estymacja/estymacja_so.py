import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error



def estymacja_os():
    data = pd.read_csv("Dane/Uporzadkowane_dane/TRAN_1733_CREL_20260125154356.csv", sep=';')
    print(data.head())
    polska = data[(data['Rok'] >= 2005)  & (data['Rok'] <= 2023)]
    print(polska)

    # Regresja liniowa
    X = polska['Rok'].values.reshape(-1, 1)
    y = polska['Wartosc'].values
    model = LinearRegression()
    model.fit(X, y)

    # Obliczanie błędów
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    print(f"Średni błąd kwadratowy (MSE): {mse:.2f}")
    print(f"Średni błąd bezwzględny (MAE): {mae:.2f}")

    # Przewidywanie do 2040
    lata = np.arange(polska['Rok'].min(), 2041).reshape(-1, 1)
    prognoza = model.predict(lata)

    plt.figure(figsize=(10, 5))
    plt.plot(polska['Rok'], polska['Wartosc'], marker='o', label='Dane historyczne')
    plt.plot(lata, prognoza, 'r--', label='Prognoza do 2040')
    plt.title('Liczba samochodów osobowych w Polsce na przestrzeni lat')
    plt.xlabel('Rok')
    plt.ylabel('Liczba samochodów osobowych')
    plt.xticks(lata.flatten(), rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

     # Eksport do CSV
    df_prognoza = pd.DataFrame({
        'Kraj': ['Polska'] * len(lata),
        'Rok': lata.flatten(),
        'Prognozowana liczba samochodów osobowych': prognoza
    })
    df_prognoza.to_csv('Dane/Estymacyjne_dane/prognoza_liczba_samochodow_osobowych_polska.csv', index=False)


if __name__ == "__main__":
    estymacja_os()