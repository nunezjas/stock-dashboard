# Stock Market Research Dashboard — CPS*5745

Author: **Jassiris Nunez** · **Developed for CPS*5745**.

Built with Streamlit + Plotly + Yahoo Finance (`yfinance`). Inspired by the structure of the Kean Power BI dashboard: headline, shared filters, summary KPIs, and clearly arranged chart panels. 


## Visualizations

1. Indexed line chart (relative price performance)
2. Horizontal bar chart (adjusted-price total returns)
3. Donut chart (proportions of selected companies' total traded shares; not market share)
4. Monthly adjusted-price return heatmap (first to last trading close within each month)
5. Daily returns box plot (distribution and volatility)

Company multiselect (minimum three stocks) and start/end dates update all visuals together. Includes stock summary cards, key findings, CSV download, the author's name, and attribution.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

**Manual Render commands**

- Build: `pip install -r requirements.txt`
- Start: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true --browser.gatherUsageStats false`

Stock market requests require an outbound connection from Render to Yahoo Finance. If there is a temporary rate limit, retry later.
