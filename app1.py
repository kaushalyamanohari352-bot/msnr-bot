import streamlit as st
import ccxt
import pandas as pd
from lightweight_charts.widgets import StreamlitChart

# Streamlit Page Settings
st.set_page_config(page_title="MSNR Trading Dashboard", layout="wide")
st.title("📈 MSNR Trading Dashboard & AI Assistant")

# --- පින්තූරයෙන් ලබාගත් Coins ලැයිස්තුව ---
TARGET_COINS = [
    'DOGE/USDT', 'BULLA/USDT', 'RIVER/USDT', 'DENT/USDT', 'ARC/USDT', 
    'MYX/USDT', 'FIL/USDT', 'PUMP/USDT', 'NEAR/USDT', 'UNI/USDT', 
    'FOGO/USDT', 'GPS/USDT', 'WIF/USDT', 'FARTCOIN/USDT', 'VVV/USDT', 
    'TRUMP/USDT', 'DOGE/USDC', 'IP/USDT', 'FET/USDT', 'CAKE/USDT', 
    'SPX/USDT', 'DYDX/USDT', 'BERA/USDT'
]

# Sidebar - Settings
st.sidebar.header("Chart Settings")

# Text input එක වෙනුවට Dropdown (Selectbox) එකක් දැමීම
symbol = st.sidebar.selectbox("Coin Symbol", TARGET_COINS, index=0)

# Timeframe එකේ default අගය '1h' (index=3) ලෙස වෙනස් කිරීම
timeframe = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
limit = st.sidebar.slider("Number of Candles", 100, 1000, 500)

# Binance Connection (Futures Market එකෙන් දත්ත ගැනීමට සැකසීම)
@st.cache_data(ttl=60) # විනාඩියකට වරක් පමණක් දත්ත අලුත් කරයි
def fetch_data(symbol, timeframe, limit):
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'} # Futures Data
        })
        bars = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        
        # Lightweight Charts සඳහා time column එක string format එකට හැරවීම (Error එකෙන් බේරීමට)
        df['time'] = pd.to_datetime(df['time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
        return df
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

# Data Load
df = fetch_data(symbol, timeframe, limit)

# Main Dashboard Layout
col1, col2 = st.columns([3, 1]) # Chart එකට ඉඩ වැඩියෙනුත්, Panel එකට අඩුවෙනුත්

with col1:
    st.subheader(f"{symbol} Live Chart")
    if not df.empty:
        # Lightweight Chart Rendering
        chart = StreamlitChart(width=800, height=500)
        chart.set(df)
        chart.load()
    else:
        st.warning("No data available for the chart.")

with col2:
    st.subheader("🔔 Recent Signals")
    # දැනට සරලව Signals පෙන්වමු (පසුව Live Bot එකේ Data මෙතනට ගනිමු)
    st.info("🟢 DOGE/USDT - BUY @ 1h\nEntry: 0.0931")
    st.error("🔴 FIL/USDT - SELL @ 1h\nEntry: 0.912")
    st.info("🟢 BERA/USDT - BUY @ 1h\nEntry: 0.6190")

st.markdown("---")
st.subheader("🤖 Chat with MSNR AI Agent (Coming Soon...)")
st.text_input("Ask a question about MSNR strategy or current chart...", disabled=True)