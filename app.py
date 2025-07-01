import ccxt
import pandas as pd
import csv
from datetime import datetime
from ta.trend import EMAIndicator
import time
import os

symbol = 'BTC/USD'
timeframe = '15m'
limit = 100
archivo_csv = 'trading_log.csv'

exchange = ccxt.coinbase({"enableRateLimit": True})

def analizar_mercado():
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        df['EMA9'] = EMAIndicator(close=df['close'], window=9).ema_indicator()
        df['EMA21'] = EMAIndicator(close=df['close'], window=21).ema_indicator()

        last = df.iloc[-1]
        if last['EMA9'] > last['EMA21']:
            signal = 'BUY'
        elif last['EMA9'] < last['EMA21']:
            signal = 'SELL'
        else:
            signal = 'WAIT'

        row = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'close': round(last['close'], 2),
            'EMA9': round(last['EMA9'], 2),
            'EMA21': round(last['EMA21'], 2),
            'Signal': signal
        }

        file_exists = os.path.isfile(archivo_csv)
        with open(archivo_csv, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

        print(f"✅ Guardado: {row['timestamp']} | Signal: {signal} | Close: {row['close']}")

    except Exception as e:
        print(f"❌ Error durante análisis: {e}")

def loop_bot():
    print("🔁 Iniciando análisis automático cada 15 minutos... (Ctrl+C para detener)")
    while True:
        analizar_mercado()
        time.sleep(900)

def analizar_estadisticas():
    try:
        df = pd.read_csv(archivo_csv).dropna()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)

        budget = 1000
        in_position = False
        buy_price = 0
        profits = []

        for _, row in df.iterrows():
            if row['Signal'] == 'BUY' and not in_position:
                buy_price = row['close']
                in_position = True
            elif row['Signal'] == 'SELL' and in_position:
                sell_price = row['close']
                btc_bought = budget / buy_price
                usd_received = btc_bought * sell_price
                profit = usd_received - budget
                profits.append(profit)
                in_position = False

        total_trades = len(profits)
        winning_trades = len([p for p in profits if p > 0])
        losing_trades = total_trades - winning_trades
        total_profit = sum(profits)
        accuracy = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        print("\n📊 RESULTADOS DEL TRADING:")
        print(f"🔢 Total de operaciones: {total_trades}")
        print(f"✅ Operaciones ganadoras: {winning_trades}")
        print(f"❌ Operaciones perdedoras: {losing_trades}")
        print(f"🎯 Precisión: {accuracy:.2f}%")
        print(f"💰 Ganancia/Pérdida total: ${total_profit:.2f}")

    except Exception as e:
        print(f"❌ Error analizando estadísticas: {e}")

def mostrar_menu():
    while True:
        print("\n📍 MENÚ PRINCIPAL")
        print("1. Ejecutar análisis 1 vez")
        print("2. Iniciar bot en loop (cada 15 min)")
        print("3. Ver estadísticas del trading_log.csv")
        print("4. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            analizar_mercado()
        elif opcion == '2':
            loop_bot()
        elif opcion == '3':
            analizar_estadisticas()
        elif opcion == '4':
            print("👋 Saliendo del bot...")
            break
        else:
            print("❌ Opción inválida. Intenta de nuevo.")

# ▶️ EJECUCIÓN
mostrar_menu()