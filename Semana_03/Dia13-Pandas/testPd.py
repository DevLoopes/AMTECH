import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({'Ano':[2020,2021,2022], 'Vendas':[100,200,300]})
df.plot(x='Ano', y = 'Vendas', kind='bar')
plt.show()