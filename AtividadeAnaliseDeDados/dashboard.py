import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import gdown


@st.cache_data
def download_data():
    file_id = "1hHf_s19PneIyR4mFgFUhboKlEce3B5Po"  # Substitua pelo ID do seu arquivo
    url = f"https://drive.google.com/uc?id={file_id}"
    output = "yellow_tripdata_2016-03.csv"
    gdown.download(url, output, quiet=False)
    return output


@st.cache_data
def load_data():
    csv_file = download_data()
    df = pd.read_csv(
        csv_file,
        usecols=[
            "tpep_pickup_datetime", "tpep_dropoff_datetime", 
            "passenger_count", "trip_distance", "total_amount", 
            "tip_amount", "payment_type", "pickup_latitude", "pickup_longitude"
        ],
        parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"]
    )
    
    
    df["payment_type"] = df["payment_type"].astype("category")
    
    return df

df = load_data()


st.title("🚖 NYC Yellow Taxi Dashboard")
st.markdown("Uma análise dos padrões de viagens de táxi em Nova York.")


total_trips = df.shape[0]
total_revenue = df["total_amount"].sum()
avg_passengers = df["passenger_count"].mean()

st.metric("Total de Viagens", total_trips)
st.metric("Receita Total ($)", f"{total_revenue:,.2f}")
st.metric("Média de Passageiros por Viagem", f"{avg_passengers:.2f}")


st.subheader("📅 Viagens ao longo do tempo")
df["date"] = df["tpep_pickup_datetime"].dt.date
daily_trips = df.groupby("date").size().reset_index(name="viagens")

fig_time = px.line(
    daily_trips, x="date", y="viagens", 
    title="Número de Viagens por Dia",
    markers=True
)
st.plotly_chart(fig_time, use_container_width=True)


st.subheader("🗺️ Mapa de Pickups")
lat_min, lat_max = 40.5, 41.0
lon_min, lon_max = -74.3, -73.7

df = df[
    (df["pickup_latitude"].between(lat_min, lat_max)) &
    (df["pickup_longitude"].between(lon_min, lon_max))
]

if not df[["pickup_latitude", "pickup_longitude"]].dropna().empty:
    map_data = df[["pickup_latitude", "pickup_longitude"]].dropna().sample(min(1000, len(df)))
    map_data = map_data.rename(columns={'pickup_latitude': 'latitude', 'pickup_longitude': 'longitude'})
    st.map(map_data)
else:
    st.write("Sem dados de localização para exibição.")


st.subheader("💳 Métodos de Pagamento")
if not df["payment_type"].dropna().empty:
    payment_map = {
        1: "Cartão de Crédito",
        2: "Dinheiro",
        3: "Sem Cobrança",
        4: "Disputa"
    }
    df["payment_type"] = df["payment_type"].map(payment_map)
    
    payment_counts = df["payment_type"].value_counts().reset_index()
    payment_counts.columns = ["Método", "Contagem"]

    fig_payment = px.pie(
        payment_counts, names="Método", values="Contagem", 
        title="Distribuição dos Métodos de Pagamento"
    )
    st.plotly_chart(fig_payment, use_container_width=True)
else:
    st.write("Sem dados de pagamento disponíveis.")

st.subheader("💵 Tarifa e Gorjeta por Distância")
df_sample = df[["trip_distance", "total_amount", "tip_amount"]].dropna().sample(min(5000, len(df)))  

fig_fare = px.scatter(
    df_sample, x="trip_distance", y="total_amount", 
    color="tip_amount", title="Tarifa Total e Gorjeta por Distância", 
    opacity=0.6, render_mode="webgl"
)
st.plotly_chart(fig_fare, use_container_width=True)

st.markdown("Feito para análise de padrões de táxi em NYC 🚖")
