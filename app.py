import streamlit as st
import pandas as pd
from datetime import datetime
import ccxt
from ta.trend import EMAIndicator
import os

# Título principal
st.title("🤖 Trading Bot 1.5")

# Menú desplegable
option = st.selectbox("Selecciona una opción:", [
    "Ejecutar análisis 1 vez",
    "Iniciar bot en loop (cada 15 min)",
    "Ver estadísticas del trading_log.csv",
    "Salir"
])

# Función para cargar datos y calcular EMAs
def analizar_mercado():
    exchange = ccxt.coinbase()
    bars = exchange.fetch_ohlcv('BTC/USD', timeframe='15m', limit=100)

    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    df['EMA9'] = EMAIndicator(df['close'], window=9).ema_indicator()
    df['EMA21'] = EMAIndicator(df['close'], window=21).ema_indicator()

    df['Signal'] = df.apply(lambda row:
                            'BUY' if row['EMA9'] > row['EMA21'] else
                            'SELL' if row['EMA9'] < row['EMA21'] else 'WAIT', axis=1)

    df.to_csv("trading_log.csv", mode='a', header=not os.path.exists("trading_log.csv"), index=False)
    return df

# Opción 1: Ejecutar análisis una vez
if option == "Ejecutar análisis 1 vez":
    st.subheader("🔍 Ejecutando análisis...")
    df = analizar_mercado()
    st.write(df.tail(10))

# Opción 2: Modo loop (demostración)
elif option == "Iniciar bot en loop (cada 15 min)":
    st.warning("Este modo aún no está habilitado en Streamlit. Debe ejecutarse desde consola con programación asincrónica.")

# Opción 3: Ver estadísticas del CSV
elif option == "Ver estadísticas del trading_log.csv":
    if os.path.exists("trading_log.csv"):
        df = pd.read_csv("trading_log.csv")
        st.subheader("📊 Estadísticas del Log")
        st.write(df.tail(10))
        st.line_chart(df[['close', 'EMA9', 'EMA21']].tail(50))
    else:
        st.error("El archivo trading_log.csv no existe todavía.")

# Opción 4: Salir
elif option == "Salir":
    st.info("Gracias por usar el bot 🚀")
