# 🦄 Unicorn Analytics Dashboard

An interactive Streamlit application to explore global unicorn (privately held startups valued over **$1 billion**) data.

## Features

1. Live dataset pulled from Maven Unicorn Challenge (March 2022).
2. Key metrics: total unicorns, aggregate and average valuations, average founding year.
3. Interactive filters by industry, country, and founding-year range.
4. Visual insights:
   • Valuations accumulated over time.
   • Top countries by unicorn count.
   • Industry distribution.

## Quickstart

```bash
# clone your fork or the repo
git clone https://github.com/1505-Ak/unicorn-analytics.git && cd unicorn-analytics

# create Python env (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# install dependencies
pip install -r requirements.txt

# launch the dashboard
streamlit run app.py
```

The app will open in your default browser at http://localhost:8501

## Tech Stack

• Python 3.9+
• Streamlit — UI layer and deployment
• Pandas — data manipulation
• Plotly Express — interactive visualizations

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

## Deployment

While Streamlit can be deployed on Streamlit Community Cloud, Render, Heroku, etc., this repo focuses on local exploration. Contributions welcome!

## License

Data © Maven Unicorn Challenge / CB Insights snapshot (March 2022). Code released under the MIT License. 