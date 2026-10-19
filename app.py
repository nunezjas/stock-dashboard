import datetime as dt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Comparison Dashboard", page_icon="📈", layout="wide")

COMPANIES = {"Apple (AAPL)": "AAPL", "Microsoft (MSFT)": "MSFT", "NVIDIA (NVDA)": "NVDA", "Alphabet (GOOGL)": "GOOGL", "Amazon (AMZN)": "AMZN", "Tesla (TSLA)": "TSLA", "Meta (META)": "META"}
COLORS = {"AAPL": "#2563eb", "MSFT": "#16a34a", "NVDA": "#ea580c", "GOOGL": "#9333ea", "AMZN": "#dc2626", "TSLA": "#0891b2", "META": "#a16207"}

st.markdown("""<style>
.stApp {background: #f2f5fb; color: #1c2940;}
.block-container {padding-top: 1.6rem; max-width: 1450px;}
[data-testid="stSidebar"] {background: #12233d;}
[data-testid="stSidebar"] * {color: #f1f5fb !important;}
[data-testid="stMetric"] {background: white; border: 1px solid #dfe5ee; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 6px #15243c09;}
[data-testid="stPlotlyChart"] {background: white; border-radius: 12px; border: 1px solid #e0e7f0; padding: 0.45rem;}
h3 {color: #152945; font-size: 1.25rem !important;}
</style>""", unsafe_allow_html=True)
st.markdown("""<div style="background:linear-gradient(110deg,#152945,#22538e); padding:28px 34px; border-radius:14px; color:white; margin-bottom:16px">
<div style="font-size:12px;letter-spacing:2px;color:#b8d4f8">CPS*5745 • DATA VISUALIZATION</div>
<div style="font-size:32px;font-weight:750;margin-top:7px">Stock Market Comparison Dashboard</div>
<div style="margin-top:7px;color:#e3ecf9">Jassiris Nunez &nbsp; | &nbsp; Developed for CPS*5745</div>
</div>""", unsafe_allow_html=True)
st.caption("Compare companies using the latest available Yahoo Finance data. Prices may be delayed; this is not a live trading terminal.")

with st.sidebar:
    st.header("Dashboard filters")
    st.caption("Select at least three companies and a time period. Every chart updates together.")
    selected_names = st.multiselect("Companies (select at least 3)", list(COMPANIES), default=list(COMPANIES)[:3])
    today = dt.date.today()
    start = st.date_input("Start date", value=today - dt.timedelta(days=365), max_value=today)
    end = st.date_input("End date", value=today, max_value=today)
    st.caption("All five charts use the selected companies and date range.")

if len(selected_names) < 3:
    st.warning("Choose at least three companies to meet the assignment requirement.")
    st.stop()
if start >= end:
    st.error("The start date must be before the end date.")
    st.stop()

symbols = [COMPANIES[n] for n in selected_names]

@st.cache_data(ttl=1800, show_spinner=False)
def get_history(symbols_tuple, start_date, end_date):
    # End date is exclusive for yfinance, so add a day.
    raw = yf.download(list(symbols_tuple), start=str(start_date), end=str(end_date + dt.timedelta(days=1)),
                      auto_adjust=True, progress=False, group_by="ticker", threads=False)
    if raw.empty:
        return pd.DataFrame()
    frames = []
    for sym in symbols_tuple:
        try:
            h = raw[sym] if isinstance(raw.columns, pd.MultiIndex) else raw
            h = h[["Close", "Volume"]].dropna(subset=["Close"]).copy()
            h["Ticker"] = sym
            h["Date"] = pd.to_datetime(h.index).tz_localize(None) if h.index.tz is not None else pd.to_datetime(h.index)
            frames.append(h.reset_index(drop=True))
        except (KeyError, TypeError):
            continue
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

with st.spinner("Loading stock prices..."):
    try:
        data = get_history(tuple(symbols), start, end)
    except Exception as exc:
        st.error(f"Market data could not be retrieved: {exc}. Try again in a moment.")
        st.stop()

if data.empty:
    st.error("No market data is available for this selection. Choose a longer or more recent date range.")
    st.stop()

available = sorted(data["Ticker"].unique())
missing = set(symbols) - set(available)
if missing:
    st.warning("No prices returned for: " + ", ".join(sorted(missing)))
if len(available) < 3:
    st.error("Less than three stocks returned data. Please change the selection or date range.")
    st.stop()

data = data.sort_values(["Ticker", "Date"]).copy()
data["Normalized"] = data.groupby("Ticker")["Close"].transform(lambda x: 100 * x / x.iloc[0])
data["DailyReturn"] = data.groupby("Ticker")["Close"].pct_change() * 100
stats = data.groupby("Ticker").agg(First=("Close", "first"), Last=("Close", "last"), AverageVolume=("Volume", "mean"), TradingDays=("Close", "size"))
stats["TotalReturn"] = (stats["Last"] / stats["First"] - 1) * 100
stats["DailyVolatility"] = data.groupby("Ticker")["DailyReturn"].std()
stats = stats.reset_index()
actual_start = data["Date"].min().date()
actual_end = data["Date"].max().date()
st.caption(f"Observed trading dates: {actual_start} to {actual_end} · Data source: Yahoo Finance via yfinance · Adjusted historical prices")

st.subheader("Market overview")
cols = st.columns(len(available))
for i, sym in enumerate(available):
    s = stats[stats["Ticker"] == sym].iloc[0]
    cols[i].metric(sym, f"${s['Last']:,.2f}", f"{s['TotalReturn']:+.1f}% period return")
st.caption("Summary indicators above do not count toward the five required visualizations.")

def format_fig(fig, y_label=None, percent=False):
    fig.update_layout(legend_title_text="Company", margin=dict(l=25, r=20, t=35, b=35), hovermode="x unified", paper_bgcolor="white", plot_bgcolor="white", font=dict(color="#334155"), legend=dict(orientation="h", y=1.12, x=0), xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#e8edf5"))
    if y_label: fig.update_yaxes(title_text=y_label, ticksuffix="%" if percent else None)
    return fig

st.markdown("### Performance over time")
st.markdown("### 1. Adjusted closing price over time")
st.caption("Compare share price in USD. Share prices alone do not indicate which stock performed best.")
fig1 = px.line(data, x="Date", y="Close", color="Ticker", color_discrete_map=COLORS, labels={"Close": "Adjusted close (USD)", "Date": "Trading date"})
st.plotly_chart(format_fig(fig1, "Adjusted close (USD)"), use_container_width=True)

st.markdown("### 2. Indexed performance (starting value = 100)")
st.caption("All stocks begin at 100 at their first available trading day; higher values indicate stronger percentage growth.")
fig2 = px.line(data, x="Date", y="Normalized", color="Ticker", color_discrete_map=COLORS, labels={"Normalized": "Indexed value (base = 100)", "Date": "Trading date"})
fig2.add_hline(y=100, line_dash="dash", line_color="gray")
st.plotly_chart(format_fig(fig2, "Indexed value (base = 100)"), use_container_width=True)

left, right = st.columns(2)
with left:
    st.markdown("### 3. Total return by company")
    st.caption("Percentage change between each company's first and last available adjusted closing price.")
    fig3 = px.bar(stats.sort_values("TotalReturn"), x="Ticker", y="TotalReturn", color="Ticker", color_discrete_map=COLORS, text="TotalReturn")
    fig3.update_traces(texttemplate="%{text:+.1f}%", textposition="outside")
    st.plotly_chart(format_fig(fig3, "Total return (%)", True), use_container_width=True)
with right:
    st.markdown("### 4. Average daily trading volume")
    st.caption("Average number of shares traded on each recorded trading day, in millions of shares.")
    vol = stats.copy()
    vol["VolumeMillions"] = vol["AverageVolume"] / 1_000_000
    fig4 = px.bar(vol.sort_values("VolumeMillions"), x="Ticker", y="VolumeMillions", color="Ticker", color_discrete_map=COLORS, text="VolumeMillions")
    fig4.update_traces(texttemplate="%{text:.1f}M", textposition="outside")
    st.plotly_chart(format_fig(fig4, "Shares per day (millions)"), use_container_width=True)

st.markdown("### 5. Daily return distribution")
st.caption("Compare day-to-day variability. Wider distributions indicate larger daily percentage price changes. Values are daily returns, not annual returns.")
returns = data.dropna(subset=["DailyReturn"])
if not returns.empty:
    fig5 = px.box(returns, x="Ticker", y="DailyReturn", color="Ticker", color_discrete_map=COLORS, points="outliers")
    st.plotly_chart(format_fig(fig5, "Daily return (%)", True), use_container_width=True)
else:
    st.info("The selected range needs at least two trading days to show daily returns.")

st.subheader("Key findings and interpretation")
best = stats.loc[stats["TotalReturn"].idxmax()]
worst = stats.loc[stats["TotalReturn"].idxmin()]
most_volatile = stats.loc[stats["DailyVolatility"].idxmax()] if stats["DailyVolatility"].notna().any() else None
comment = (f"Between {actual_start} and {actual_end}, {best['Ticker']} had the highest adjusted-price return "
           f"({best['TotalReturn']:+.1f}%), while {worst['Ticker']} had the lowest ({worst['TotalReturn']:+.1f}%). "
           "The indexed chart makes these differences easier to compare than raw stock prices. ")
if most_volatile is not None:
    comment += f"{most_volatile['Ticker']} had the highest standard deviation of daily returns ({most_volatile['DailyVolatility']:.2f} percentage points), suggesting more short-term price variation."
st.write(comment)
st.caption("Historical returns do not predict future results. Adjusted closing prices reflect adjustments available from the data provider; the latest trading session may be delayed.")

with st.expander("See data table and download CSV"):
    st.dataframe(data[["Date", "Ticker", "Close", "Volume", "Normalized", "DailyReturn"]], hide_index=True, use_container_width=True)
    st.download_button("Download filtered dataset", data.to_csv(index=False).encode("utf-8"), "stock_comparison.csv", "text/csv")
