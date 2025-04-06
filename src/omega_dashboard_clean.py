# omega_dashboard_clean.py
import streamlit as st
import plotly.graph_objects as go
from signal_engine import generate_daytrade_signal

# Setup
st.set_page_config(layout="wide", page_title="Omega Day Trading Dashboard")
st.title("📈 Omega Finance Dashboard")
st.markdown("Echtzeit Day-Trading-Signale mit T1–T4, Trefferquoten und News")

# Märkte
markets = {
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Gold (GC=F)": "GC=F",
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA",
    "DAX (^GDAXI)": "^GDAXI",
    "EUR/USD (EURUSD=X)": "EURUSD=X"
}

choice = st.selectbox("📊 Markt auswählen:", list(markets.keys()))
symbol = markets[choice]

# Signal abrufen
signal_data = generate_daytrade_signal(symbol)

# Marktzustand anzeigen
if not signal_data.get("market_open", False):
    st.error("❌ Markt derzeit geschlossen – kein aktives Trading möglich")
else:
    st.success("✅ Markt ist offen – Signale aktiv")

    entry = signal_data.get("entry_price", "N/A")
    try:
        entry_price = f"{float(entry):.2f}"
    except:
        entry_price = str(entry)

    st.markdown(f"📢 **Signal:** `{signal_data.get('signal', 'N/A')}` bei `{entry_price}` USD")
    st.markdown(f"⏳ **Gültig bis:** `{signal_data.get('valid_until', 'N/A')}`")
    st.markdown(f"🔍 **Strategie:** `{signal_data.get('strategy', 'N/A')}` (Confidence: `{signal_data.get('confidence', '-')}`)")

    # Ziele
    st.markdown("### 🎯 Kursziele & Trefferquoten")
    targets = signal_data.get("targets", {})
    hits = signal_data.get("hit_rates", {})

    for tx in ["T1", "T2", "T3", "T4"]:
        target = targets.get(tx, "N/A")
        hit = hits.get(tx, "-")
        st.markdown(f"- **{tx}**: `{target}` USD ({hit} % Trefferquote)")

    # MACD Plot
    if "history" in signal_data:
        df = signal_data["history"]
        macd_fig = go.Figure()
        macd_fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"))
        macd_fig.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], name="Signal-Linie"))
        macd_fig.update_layout(title="MACD-Indikator", xaxis_title="Datum", yaxis_title="MACD")
        st.plotly_chart(macd_fig, use_container_width=True)

    # Top-Signal
    best = signal_data.get("top_signal")
    if best:
        st.markdown("### 🔥 Bestes Signal aller Märkte")
        st.markdown(f"**{best['symbol']}** → `{best['signal']}` bei `{best['entry_price']}` USD bis `{best['valid_until']}`")
        for tx in ["T1", "T2", "T3", "T4"]:
            st.markdown(f"- {tx}: {best['targets'][tx]} ({best['hit_rates'][tx]} %)")

    # News
    news_list = signal_data.get("news", [])
    if news_list:
        st.markdown("---")
        st.markdown("### 📰 Relevante News & Social Buzz")
        for news in news_list:
            st.markdown(f"**[{news['title']}]({news['url']})**")
            st.caption(news.get("summary", ""))
