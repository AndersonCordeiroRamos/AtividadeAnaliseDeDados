import pandas as pd
import streamlit as st


# Certifique-se de que o arquivo CSV está na mesma pasta que este código
df = pd.read_csv("yellow_tripdata_2016-03.csv")

st.write(df.columns)  # Isso vai mostrar os nomes das colunas
