# CPS*5745 — Interactive Stock Comparison Dashboard

Built with Streamlit + Plotly + Yahoo Finance (`yfinance`). Inspired by the structure of the Kean Power BI dashboard: headline, shared filters, summary KPIs, and clearly arranged chart panels. The Power BI visual cannot be inspected via the provided link in this environment, so this is not an exact clone.

**Author:** Jassiris Nunez  
**Required label:** Developed for CPS*5745

## Included visualizations
1. Adjusted closing prices (USD, line chart)
2. Indexed performance (first trading day = 100, line chart)
3. Period total returns (%, bar chart)
4. Average daily trading volume (millions of shares, bar chart)
5. Distribution of daily returns (%, box plot)

All five are controlled by the same company multi-select and date range inputs. Summary KPI cards do not count as visualizations. Key findings update based on the selected data.

## Run locally (Mac or Windows)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

For Windows PowerShell activate with `.venv\Scripts\Activate.ps1`.

## Deploy to Render (free plan where available)

1. Create a new public GitHub repository such as `cps5745-stock-dashboard`.
2. Upload `app.py`, `requirements.txt`, `render.yaml`, and `.gitignore` into the **repository root**. Do not upload only the ZIP file.
3. In Render at https://dashboard.render.com, choose **New > Blueprint** and select your repository. Render will read `render.yaml`. Confirm the free plan if offered, then deploy.
4. Alternatively, choose **New > Web Service** and set:
   - Language/runtime: `Python`
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true`
   - Environment variable: `PYTHON_VERSION` = `3.11.11`
   - Instance type: Free (if available for your account).
5. Wait until the service reports **Live**. Open the public `.onrender.com` URL in a private/incognito window to confirm no login is required. On a free Render plan, the service can sleep when idle, so the first load may take a while.

**Troubleshooting:** If Render says no port detected, verify the start command includes `--server.address 0.0.0.0 --server.port $PORT`. If module import fails, check `requirements.txt` is at the repo root and that the build succeeded. If Yahoo Finance does not return prices, try again or change the date range; the data source can rate-limit requests.

## Assignment submission checklist

- Public URL works without signing in.
- Three or more companies selected.
- Five charts display data and respond to both filters.
- Your name and exact text `Developed for CPS*5745` appear.
- Add one or more readable screenshots clearly showing all charts, name, and selected filters. You may need two screenshots because of the dashboard height.
- Add the live Render URL to your Canvas answer and upload the screenshots separately.

*Note:* Financial data retrieved on demand; prices may be delayed and are not independently verified. The app requires network access to Yahoo Finance while running.
