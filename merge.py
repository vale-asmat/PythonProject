import pandas as pd

df1 = pd.read_csv('fichierscsv/app_2022_3.csv',encoding='cp1252',delimiter=';',decimal=',')
df2 = pd.read_csv('fichierscsv/app_2022_12.csv',encoding='cp1252',delimiter=';',decimal=',')
df3 = pd.read_csv('fichierscsv/app_2022.csv',encoding='cp1252',delimiter=';',decimal=',')

merged_df = pd.merge(df1, df2, how='outer')
final_merged_df = pd.merge(merged_df, df3, how='outer')

final_merged_df.to_csv('merged_file.csv', index=False)
