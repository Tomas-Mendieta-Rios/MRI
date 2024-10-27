import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Creación de dos DataFrames de ejemplo
df1 = pd.DataFrame({
    'x': np.linspace(0, 10, 100),
    'y': np.sin(np.linspace(0, 10, 100))
})

df2 = pd.DataFrame({
    'x': np.linspace(0, 10, 100),
    'y': np.cos(np.linspace(0, 10, 100))
})

# Gráfico
plt.figure(figsize=(10, 6))

# Primer DataFrame (sin transparencia)
sns.lineplot(data=df1, x='x', y='y', label='Seno', color="blue", alpha=1.0)

# Segundo DataFrame (con transparencia)
sns.lineplot(data=df2, x='x', y='y', label='Coseno', color="red", alpha=0.5)

# Personalización
plt.title('Gráfico Superpuesto de Dos DataFrames con Transparencia')
plt.xlabel('Eje X')
plt.ylabel('Eje Y')
plt.legend()
plt.show()
