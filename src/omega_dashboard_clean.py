# omega_dashboard_clean.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from signal_engine import generate_daytrade_signal

# Setup
st.set_page_config(layout="wide", page_title="Omega Day Trading Dashboard")
st.title("📈 Omega Finance Dashboard")
st.markdown("Echtzeit Day-Trading-Signale mit T1–T4, Trefferquoten und News")

# Markt-Auswahl
markets = {
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Gold (GC=F)": "GC=F",
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA",
    "DAX (^GDAXI)": "^GDAXI",
    "EUR/USD (EURUSD=X)": "EURUSD=X"
}

choice = st.selectbox("📊 Markt auswählen:", options=list(markets.keys()))
symbol = markets[choice]

# Hole Signal & Daten
signal_data = generate_daytrade_signal(symbol)

if not signal_data["market_open"]:
    st.error("❌ Markt derzeit geschlossen – kein aktives Trading möglich")
else:
    st.success("✅ Markt ist offen – Signale aktiv")

    st.markdown(f"### 📢 Signal: `{signal_data['signal']}` bei {signal_data['entry_price']:.2f} USD")
    st.markdown(f"⏳ Gültig bis: `{signal_data['valid_until']}`")
    st.markdown(f"🔍 Strategie: `{signal_data['strategy']}` (Confidence: {signal_data['confidence']})")

    # Ziele
    st.markdown("### 🎯 Kursziele & Trefferquoten")
    targets = signal_data["targets"]
    hits = signal_data["hit_rates"]

    for tx in ["T1", "T2", "T3", "T4"]:
        st.markdown(f"- {tx}: {targets[tx]:.2f} USD ({hits[tx]} % Trefferquote)")

    # MACD Plot optional
    macd_fig = go.Figure()
    macd_fig.add_trace(go.Scatter(x=signal_data['history'].index, y=signal_data['history']['MACD'], name="MACD"))
    macd_fig.add_trace(go.Scatter(x=signal_data['history'].index, y=signal_data['history']['MACD_signal'], name="Signal-Linie"))
    macd_fig.update_layout(title="MACD-Indikator", xaxis_title="Zeit", yaxis_title="MACD")
    st.plotly_chart(macd_fig, use_container_width=True)

    # Beste Signalübersicht
    st.markdown("---")
    st.markdown("### 🔥 Bestes Signal aller Märkte")
    best = signal_data.get("top_signal")
    if best:
        st.markdown(f"**{best['symbol']}** → {best['signal']} bei {best['entry_price']} USD bis {best['valid_until']}")
        for tx in ["T1", "T2", "T3", "T4"]:
            st.markdown(f"- {tx}: {best['targets'][tx]} ({best['hit_rates'][tx]} %)")

    # News anzeigen
    st.markdown("---")
    st.markdown("### 📰 Relevante News & Social Buzz")
    for news in signal_data.get("news", []):
        st.markdown(f"**[{news['title']}]({news['url']})**")
        st.caption(news['summary'])
