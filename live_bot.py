import ccxt
import pandas as pd
import requests
from datetime import datetime

# Telegram Bot Details
TELEGRAM_BOT_TOKEN = '8522442591:AAGRkeE12_thVSxCTdDF-jDD9fx7QL-J-xE'
TELEGRAM_CHAT_ID = '1409591865'

exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'future'} 
})

TARGET_COINS = [
    'DOGE/USDT', 'BULLA/USDT', 'RIVER/USDT', 'DENT/USDT', 'ARC/USDT', 
    'MYX/USDT', 'FIL/USDT', 'PUMP/USDT', 'NEAR/USDT', 'UNI/USDT', 
    'FOGO/USDT', 'GPS/USDT', 'WIF/USDT', 'FARTCOIN/USDT', 'VVV/USDT', 
    'TRUMP/USDT', 'DOGE/USDC', 'IP/USDT', 'FET/USDT', 'CAKE/USDT', 
    'SPX/USDT', 'DYDX/USDT', 'BERA/USDT'
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

def check_hourly_signal(symbol, lookback=20, rr_ratio=3.0):
    try:
        bars = exchange.fetch_ohlcv(symbol, '1h', limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        df['recent_high'] = df['high'].shift(1).rolling(window=lookback).max()
        df['recent_low'] = df['low'].shift(1).rolling(window=lookback).min()
        
        df['prev_close'] = df['close'].shift(1)
        df['tr0'] = abs(df['high'] - df['low'])
        df['tr1'] = abs(df['high'] - df['prev_close'])
        df['tr2'] = abs(df['low'] - df['prev_close'])
        df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean()

        # අන්තිමට සම්පූර්ණයෙන්ම Close වුණු Candle එක (index -2)
        current = df.iloc[-2]
        prev = df.iloc[-3]

        trend = 0
        rbs_level = None
        sbr_level = None

        # BOS Logic
        for i in range(len(df)-12, len(df)-1): 
            row = df.iloc[i]
            p_row = df.iloc[i-1]
            if row['close'] > row['recent_high'] and p_row['close'] <= p_row['recent_high']:
                trend = 1
                rbs_level = row['recent_high']
                sbr_level = None
            elif row['close'] < row['recent_low'] and p_row['close'] >= p_row['recent_low']:
                trend = -1
                sbr_level = row['recent_low']
                rbs_level = None

        buy_setup = (trend == 1) and (rbs_level is not None) and (current['low'] <= rbs_level) and (current['close'] > rbs_level)
        sell_setup = (trend == -1) and (sbr_level is not None) and (current['high'] >= sbr_level) and (current['close'] < sbr_level)

        if buy_setup:
            sl = current['low'] - current['atr']
            risk = current['close'] - sl
            tp = current['close'] + (risk * rr_ratio)
            
            msg = (
                f"🟢 <b>MSNR BUY SIGNAL</b> 🟢\n\n"
                f"<b>Coin:</b> #{symbol.replace('/', '')}\n"
                f"<b>Timeframe:</b> 1 Hour (1h)\n"
                f"<b>Entry:</b> {current['close']}\n"
                f"<b>Stop Loss:</b> {sl:.4f}\n"
                f"<b>Take Profit:</b> {tp:.4f}\n"
                f"<b>RR:</b> 1:{rr_ratio}"
            )
            send_telegram_message(msg)
            print(f"BUY Signal sent for {symbol}")

        elif sell_setup:
            sl = current['high'] + current['atr']
            risk = sl - current['close']
            tp = current['close'] - (risk * rr_ratio)
            
            msg = (
                f"🔴 <b>MSNR SELL SIGNAL</b> 🔴\n\n"
                f"<b>Coin:</b> #{symbol.replace('/', '')}\n"
                f"<b>Timeframe:</b> 1 Hour (1h)\n"
                f"<b>Entry:</b> {current['close']}\n"
                f"<b>Stop Loss:</b> {sl:.4f}\n"
                f"<b>Take Profit:</b> {tp:.4f}\n"
                f"<b>RR:</b> 1:{rr_ratio}"
            )
            send_telegram_message(msg)
            print(f"SELL Signal sent for {symbol}")

    except Exception as e:
        pass

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running MSNR Hourly Check...")
for coin in TARGET_COINS:
    check_hourly_signal(coin)
print("Check Complete.")
