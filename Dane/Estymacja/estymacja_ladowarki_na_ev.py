import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


lata = np.arange(2025, 2041)
# Startujemy od 0.25 w 2025 i kończymy na 0.55 w 2040
x5_prognoza = np.linspace(0.25, 0.55, len(lata))

df_x5 = pd.DataFrame({'Rok': lata, 'X5': x5_prognoza})

# Wyświetlenie wykresu
plt.figure(figsize=(8, 5))
plt.plot(df_x5['Rok'], df_x5['X5'], marker='o')
plt.title('Prognoza X5 na lata 2025-2040')
plt.xlabel('Rok')
plt.ylabel('X5')
plt.grid(True)
plt.tight_layout()
plt.show()

# Eksport do Estymacyjne_dane
output_path = '../Estymacyjne_dane/prognoza_x5.csv'
df_x5.to_csv(output_path, index=False)
print(f'Dane zapisano do {output_path}')
# ...existing code...