# Stock Market Research Dashboard — CPS*5745

Author: **Jassiris Nunez** · **Developed for CPS*5745**.

An interactive Streamlit/Plotly stock comparison dashboard with a white-and-navy institutional-research-inspired layout. Uses the latest available Yahoo Finance historical adjusted closing prices via yfinance. Data may be delayed.

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

## Deploy on Render (free tier if available)

1. Unzip this project and upload **the files inside** to your GitHub repository (not the ZIP).
2. If this repository already exists, choose **Add file → Upload files**, replace the old `app.py`, and commit the changes. Include `requirements.txt` and `render.yaml` in the repository root.
3. Visit https://dashboard.render.com/ and select **New → Blueprint** to deploy using `render.yaml`, or create a **Web Service** using the commands below.
4. Blueprint uses the Render `free` plan, where available; some accounts may not have free instances. Render free services may sleep when idle.
5. Verify the public `.onrender.com` URL works without logging in, and take screenshots of the five charts, filters, author name, and key findings.

**Manual Render commands**

- Build: `pip install -r requirements.txt`
- Start: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true --browser.gatherUsageStats false`

Stock market requests require an outbound connection from Render to Yahoo Finance. If there is a temporary rate limit, retry later.
