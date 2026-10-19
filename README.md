# CPS*5745 — Interactive Stock Comparison Dashboard

Built with Streamlit + Plotly + Yahoo Finance (`yfinance`). Inspired by the structure of the Kean Power BI dashboard: headline, shared filters, summary KPIs, and clearly arranged chart panels.

**Author:** Jassiris Nunez  
Developed for CPS*5745

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

## Assignment submission checklist

- Public URL works without signing in.
- Three or more companies selected.
- Five charts display data and respond to both filters.
- Your name and exact text `Developed for CPS*5745` appear.
- Add one or more readable screenshots clearly showing all charts, name, and selected filters. You may need two screenshots because of the dashboard height.
- Add the live Render URL to your Canvas answer and upload the screenshots separately.

*Note:* Financial data retrieved on demand; prices may be delayed and are not independently verified. The app requires network access to Yahoo Finance while running.
