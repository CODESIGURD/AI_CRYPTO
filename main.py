import time
import csv
from datetime import datetime
from binance.client import Client

# -----------------------------
# KONFIG
# -----------------------------
api_key = '-'
api_secret = '-'

symbol = 'BTCEUR'
trade_amount = 0.0001

buy_threshold = -0.5     # Kjøp ved -0.5%
sell_threshold = 0.7     # Selg ved +0.7%

stop_loss = -2.0
take_profit = 3.0

check_interval = 15
log_file = 'btc_log.csv'

# -----------------------------
client = Client(api_key, api_secret)

in_position = False
entry_price = 0

# -----------------------------
def log_trade(action, price):
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), action, price])
    print(f"{datetime.now()} | {action} | {price:.2f} EUR")

# -----------------------------
def get_price():
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

# -----------------------------
start_price = get_price()
print(f"Starter bot. Pris: {start_price:.2f}")

# -----------------------------
while True:
    try:
        current_price = get_price()
        change_percent = (current_price - start_price) / start_price * 100

        print(f"Pris: {current_price:.2f} | Endring: {change_percent:.3f}%")

        # ---------------- BUY ----------------
        if not in_position and change_percent <= buy_threshold:
            quantity = round(trade_amount, 6)

            client.create_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=quantity
            )

            in_position = True
            entry_price = current_price
            log_trade("KJØPT", current_price)

        # ---------------- SELL ----------------
        elif in_position:
            profit_percent = (current_price - entry_price) / entry_price * 100

            # Take profit
            if profit_percent >= take_profit:
                client.create_order(
                    symbol=symbol,
                    side='SELL',
                    type='MARKET',
                    quantity=round(trade_amount, 6)
                )

                log_trade("TAKE PROFIT", current_price)
                in_position = False
                start_price = current_price

            # Stop loss
            elif profit_percent <= stop_loss:
                client.create_order(
                    symbol=symbol,
                    side='SELL',
                    type='MARKET',
                    quantity=round(trade_amount, 6)
                )

                log_trade("STOP LOSS", current_price)
                in_position = False
                start_price = current_price

            # Normal sell
            elif profit_percent >= sell_threshold:
                client.create_order(
                    symbol=symbol,
                    side='SELL',
                    type='MARKET',
                    quantity=round(trade_amount, 6)
                )

                log_trade("SOLGT", current_price)
                in_position = False
                start_price = current_price

    except Exception as e:
        print("Feil:", e)

    time.sleep(check_interval)
