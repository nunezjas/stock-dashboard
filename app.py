import datetime as dt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="CPS*5745 | Stock Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")
COMPANIES = {
    "Apple (AAPL)": "AAPL", "Microsoft (MSFT)": "MSFT", "NVIDIA (NVDA)": "NVDA",
    "Alphabet (GOOGL)": "GOOGL", "Amazon (AMZN)": "AMZN", "Tesla (TSLA)": "TSLA", "Meta (META)": "META",
}
PALETTE = ["#163d70", "#3d79b9", "#58a2dc", "#9bcce7", "#e5ae37", "#588a86", "#b15d76"]
COLORS = dict(zip(COMPANIES.values(), PALETTE))

st.markdown("""<style>
.stApp {background:#ffffff; color:#142640;}
.block-container {max-width:1530px; padding-top:0.7rem; padding-bottom:2rem;}
#MainMenu, footer {visibility:hidden;}
[data-testid="stMetric"] {background:#f3f6fb; border-left:4px solid #356da9; padding:0.9rem 1.1rem; min-height:118px;}
[data-testid="stPlotlyChart"] {border:1px solid #e7ecf2; padding:0.2rem; border-radius:4px;}
[data-testid="stHorizontalBlock"] {align-items:stretch;}
.stMarkdown h3 {font-size:1.25rem; color:#142b50; border-bottom:1px solid #e5eaf1; padding-bottom:0.4rem;}
div[data-testid="stCaptionContainer"] {font-size:.82rem;}
</style>""", unsafe_allow_html=True)

st.markdown("""<div style="background:#1d3154; color:white; padding:21px 27px; margin-bottom:13px; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:12px">
<div><span style="font-family:Georgia,serif;font-size:34px;font-weight:bold">KEAN</span><span style="margin-left:18px;font-size:14px;color:#bbd1ec">CPS*5745 • DATA VISUALIZATION</span></div>
<div style="font-family:Georgia,serif;font-size:26px">Stock Market Research Dashboard</div>
</div>""", unsafe_allow_html=True)
st.markdown("**Stock Performance — At a Glance**")
st.caption("Created by Jassiris Nunez · Developed for CPS*5745 · Historical adjusted stock prices: Yahoo Finance / yfinance (may be delayed)")

with st.container(border=True):
    st.markdown("**Dashboard filters** — all visualizations update together")
    c1, c2, c3 = st.columns([3, 1.2, 1.2])
    with c1:
        selected_names = st.multiselect("Companies (select 3 or more)", list(COMPANIES), default=list(COMPANIES)[:3])
    today = dt.date.today()
    with c2:
        start = st.date_input("From", today - dt.timedelta(days=365), max_value=today)
    with c3:
        end = st.date_input("To", today, max_value=today)

if len(selected_names) < 3:
    st.warning("Select at least three companies to meet the course requirement.")
    st.stop()
if start >= end:
    st.error("'From' must be earlier than 'To'.")
    st.stop()
symbols = [COMPANIES[n] for n in selected_names]

@st.cache_data(ttl=1800, show_spinner=False)
def get_history(tickers, start_date, end_date):
    raw = yf.download(list(tickers), start=str(start_date), end=str(end_date + dt.timedelta(days=1)),
                      auto_adjust=True, progress=False, group_by="ticker", threads=False)
    if raw.empty:
        return pd.DataFrame()
    frames = []
    for sym in tickers:
        try:
            block = raw[sym] if isinstance(raw.columns, pd.MultiIndex) else raw
            block = block[["Close", "Volume"]].dropna(subset=["Close"]).copy()
            dates = pd.to_datetime(block.index)
            if dates.tz is not None:
                dates = dates.tz_localize(None)
            block["Date"] = dates
            block["Ticker"] = sym
            frames.append(block.reset_index(drop=True))
        except (KeyError, TypeError, ValueError):
            continue
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

with st.spinner("Retrieving the latest available historical stock data..."):
    try:
        data = get_history(tuple(symbols), start, end)
    except Exception as exc:
        st.error(f"Unable to download prices: {exc}. Please try again.")
        st.stop()
if data.empty:
    st.error("No stock data returned for these dates. Try a wider date range.")
    st.stop()
missing = set(symbols) - set(data.Ticker.unique())
if missing:
    st.warning("Missing data for: " + ", ".join(sorted(missing)))
if data.Ticker.nunique() < 3:
    st.error("Data for at least three companies is required. Choose another range or companies.")
    st.stop()

data = data.sort_values(["Ticker", "Date"]).copy()
data["Indexed"] = data.groupby("Ticker").Close.transform(lambda s: s / s.iloc[0] * 100)
data["DailyReturn"] = data.groupby("Ticker").Close.pct_change() * 100
data["Volume"] = pd.to_numeric(data.Volume, errors="coerce").fillna(0)
stats = data.groupby("Ticker").agg(first=("Close", "first"), last=("Close", "last"), volume=("Volume", "sum"), avg_volume=("Volume", "mean"))
stats["return_pct"] = (stats["last"] / stats["first"] - 1) * 100
stats["volatility"] = data.groupby("Ticker").DailyReturn.std()
stats = stats.reset_index()
actual_from, actual_to = data.Date.min().date(), data.Date.max().date()
st.caption(f"Observed trading sessions: {actual_from} — {actual_to}. Prices are adjusted for corporate actions supported by the provider; data freshness depends on Yahoo Finance.")

st.markdown("### Stock Snapshot")
metrics = st.columns(len(stats))
for col, rec in zip(metrics, stats.itertuples(index=False)):
    col.metric(rec.Ticker + " · adjusted close", f"${rec.last:,.2f}", f"{rec.return_pct:+.2f}% over selected period")
st.caption("Stock snapshot cards are summary indicators and do not count toward the five different charts.")

def style(fig, height=340, legend=True):
    fig.update_layout(height=height, margin=dict(l=15, r=16, t=24, b=25), font=dict(family="Arial", color="#1e3250", size=12),
                      paper_bgcolor="white", plot_bgcolor="white", legend_title_text="Company", showlegend=legend,
                      legend=dict(orientation="h", y=1.14, x=0), hoverlabel=dict(bgcolor="white"))
    fig.update_xaxes(showgrid=False, linecolor="#d2dbe7")
    fig.update_yaxes(gridcolor="#edf0f5", zerolinecolor="#c7d1df")
    return fig

left, right = st.columns([1.65, 1])
with left:
    st.markdown("### 1 · Performance Trend — Indexed Line")
    st.caption("Comparative growth: each stock begins at 100 on its first available trading day.")
    fig = px.line(data, x="Date", y="Indexed", color="Ticker", color_discrete_map=COLORS,
                  labels={"Indexed": "Indexed price (start = 100)", "Date": "Trading date"})
    fig.add_hline(y=100, line_dash="dot", line_color="#abb7c7")
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(style(fig, 360), use_container_width=True)
with right:
    st.markdown("### 2 · Total Returns — Horizontal Bars")
    st.caption("Adjusted-price return (%) from first to last available close.")
    rank = stats.sort_values("return_pct", ascending=True)
    fig = px.bar(rank, x="return_pct", y="Ticker", orientation="h", color="Ticker", color_discrete_map=COLORS,
                 text="return_pct", labels={"return_pct": "Total return (%)", "Ticker": "Company"})
    fig.update_traces(texttemplate="%{text:+.1f}%", textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis_range=[min(-5, rank.return_pct.min() * 1.22), max(5, rank.return_pct.max() * 1.28)])
    st.plotly_chart(style(fig, 360, False), use_container_width=True)

mid1, mid2 = st.columns([1.1, 1.5])
with mid1:
    st.markdown("### 3 · Traded Shares — Donut")
    st.caption("Share of total shares traded among the selected stocks during this period; not company market share.")
    fig = px.pie(stats, names="Ticker", values="volume", hole=0.62, color="Ticker", color_discrete_map=COLORS)
    fig.update_traces(textinfo="label+percent", hovertemplate="%{label}<br>%{value:,.0f} shares<br>%{percent}<extra></extra>")
    st.plotly_chart(style(fig, 355, False), use_container_width=True)
with mid2:
    st.markdown("### 4 · Monthly Price Change — Heatmap")
    st.caption("Monthly adjusted-price change (%), first to last trading close within each calendar month.")
    data["Month"] = data.Date.dt.to_period("M").astype(str)
    monthly = data.groupby(["Ticker", "Month"]).Close.agg(["first", "last", "count"]).reset_index()
    monthly["MonthlyPct"] = np.where(monthly["count"] >= 2, (monthly["last"] / monthly["first"] - 1) * 100, np.nan)
    pivot = monthly.pivot(index="Ticker", columns="Month", values="MonthlyPct").reindex(symbols)
    heat = px.imshow(pivot, aspect="auto", color_continuous_scale="RdBu", color_continuous_midpoint=0,
                     labels={"x": "Month", "y": "Company", "color": "Return (%)"}, text_auto=".1f")
    heat.update_traces(hovertemplate="%{y} · %{x}<br>%{z:.2f}%<extra></extra>")
    heat.update_xaxes(tickangle=-45)
    st.plotly_chart(style(heat, 355, False), use_container_width=True)

st.markdown("### 5 · Daily Price Movement — Box Plot")
st.caption("Daily adjusted-price returns (%) for each company. The center line is the median; the box shows the middle 50% of daily returns. Outliers are displayed as points.")
returns = data.dropna(subset=["DailyReturn"])
if returns.empty:
    st.info("Select a date range with at least two trading days to see the distribution.")
else:
    fig = px.box(returns, x="Ticker", y="DailyReturn", color="Ticker", color_discrete_map=COLORS, points="outliers",
                 labels={"Ticker": "Company", "DailyReturn": "Daily adjusted-price return (%)"})
    st.plotly_chart(style(fig, 320, False), use_container_width=True)

st.markdown("### Key Findings")
best = stats.loc[stats.return_pct.idxmax()]
worst = stats.loc[stats.return_pct.idxmin()]
message = (f"From {actual_from} to {actual_to}, **{best.Ticker}** had the strongest adjusted-price return "
           f"(**{best.return_pct:+.2f}%**), while **{worst.Ticker}** had the lowest (**{worst.return_pct:+.2f}%**). "
           "The indexed line chart highlights the trend, the bars compare total growth, the donut summarizes traded share counts, "
           "and the heatmap and box plot reveal how performance varies by month and by day. ")
vol_stats = stats.dropna(subset=["volatility"])
if not vol_stats.empty:
    most = vol_stats.loc[vol_stats.volatility.idxmax()]
    message += f"**{most.Ticker}** had the largest standard deviation of daily returns ({most.volatility:.2f} percentage points)."
st.markdown(message)
st.info("**Interpretation note:** Comparing traded share counts across companies does not compare their total dollar trading value. Stock prices and returns are historical and are not investment advice.")
with st.expander("Explore filtered data / download CSV"):
    st.dataframe(data[["Date", "Ticker", "Close", "Volume", "Indexed", "DailyReturn"]], hide_index=True, use_container_width=True)
    st.download_button("Download filtered data (CSV)", data.to_csv(index=False).encode(), "filtered_stock_data.csv", "text/csv")
st.markdown("<div style='border-top:1px solid #e5eaf1; padding-top:12px; color:#60748a; font-size:13px'>Jassiris Nunez · Developed for CPS*5745 · Data: Yahoo Finance via yfinance</div>", unsafe_allow_html=True)
