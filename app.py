import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import networkx as nx
from pyvis.network import Network
import os
import tempfile
import itertools
import base64

st.set_page_config(page_title="Unicorn Analytics Dashboard", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/katiehuangx/Maven-Unicorn-Challenge/main/unicorn_companies_clean.csv"

def format_billions(value: float) -> str:
    """Return value formatted in billions with commas."""
    return f"{value:,.1f}B"

def download_link(df: pd.DataFrame, filename: str = "filtered_unicorns.csv") -> str:
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download filtered data</a>'

@st.cache_data(show_spinner=False)
def load_data(url: str) -> pd.DataFrame:
    """Load unicorn dataset from remote CSV."""
    df = pd.read_csv(url, parse_dates=["Date Joined"])
    df["Valuation ($B)"] = df["Valuation"] / 1e9
    df["Funding ($B)"] = pd.to_numeric(df["Funding"], errors="coerce") / 1e9
    df.dropna(subset=["Valuation"], inplace=True)
    return df

# Load data
with st.spinner("Loading unicorn dataset..."):
    df = load_data(DATA_URL)

st.title("🦄 Global Unicorn Companies — Analytics")

# Sidebar filters
st.sidebar.header("Filters")

industries = sorted(df["Industry"].unique())
countries = sorted(df["Country"].unique())
companies = sorted(df["Company"].drop_duplicates())
years = df["Year Founded"].sort_values().unique()
min_year, max_year = int(years.min()), int(years.max())

# Sidebar: optional reset button
st.sidebar.markdown("### Controls")
if st.sidebar.button("🔄 Reset filters"):
    st.session_state["industry_filter"] = industries
    st.session_state["country_filter"] = countries
    st.session_state["company_filter"] = companies
    st.session_state["year_range"] = (min_year, max_year)

selected_industries = st.sidebar.multiselect(
    "Industry",
    industries,
    default=st.session_state.get("industry_filter", industries),
    key="industry_filter",
)

selected_countries = st.sidebar.multiselect(
    "Country",
    countries,
    default=st.session_state.get("country_filter", countries),
    key="country_filter",
)

selected_companies = st.sidebar.multiselect(
    "Company (optional)",
    companies,
    default=st.session_state.get("company_filter", companies),
    key="company_filter",
)

selected_year_range = st.sidebar.slider(
    "Year Founded Range",
    min_value=min_year,
    max_value=max_year,
    value=st.session_state.get("year_range", (min_year, max_year)),
    key="year_range",
)

# If nothing selected in any multiselect, treat it as 'select all'
if len(selected_industries) == 0:
    selected_industries = industries
if len(selected_countries) == 0:
    selected_countries = countries
if len(selected_companies) == 0:
    selected_companies = companies

# Apply filters
mask = (
    df["Industry"].isin(selected_industries)
    & df["Country"].isin(selected_countries)
    & df["Year Founded"].between(*selected_year_range)
    & df["Company"].isin(selected_companies)
)
filtered_df = df[mask]

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Unicorns", f"{filtered_df['Company'].drop_duplicates().nunique():,}")
with col2:
    total_valuation = filtered_df.drop_duplicates("Company")["Valuation ($B)"].sum()
    st.metric("Total Valuation", format_billions(total_valuation))
with col3:
    avg_year = filtered_df["Year Founded"].mean()
    st.metric("Avg. Year Founded", f"{avg_year:.0f}")
with col4:
    avg_valuation = filtered_df.drop_duplicates("Company")["Valuation ($B)"].mean()
    st.metric("Avg. Valuation / Unicorn", format_billions(avg_valuation))

st.markdown(download_link(filtered_df.drop_duplicates("Company")[[
    "Company", "Valuation ($B)", "Funding ($B)", "Industry", "Country", "Year Founded"
]]), unsafe_allow_html=True)

st.markdown("---")

# Valuation Accumulation Over Time
st.subheader("Valuation Accumulation Over Time")
val_by_year = (
    filtered_df.drop_duplicates("Company")
    .assign(Year=lambda d: d["Date Joined"].dt.year)
    .groupby("Year")["Valuation ($B)"].sum()
    .reset_index()
)
if val_by_year.empty:
    st.warning("No data for current filters – showing global trend instead.")
    val_by_year = (
        df.drop_duplicates("Company")
        .assign(Year=lambda d: d["Date Joined"].dt.year)
        .groupby("Year")["Valuation ($B)"].sum()
        .reset_index()
    )
    fig_year = px.line(
        val_by_year,
        x="Year",
        y="Valuation ($B)",
        markers=True,
        labels={"Valuation ($B)": "Total Valuation ($B)"},
    )
    fig_year.update_traces(line_color="#636EFA")
    fig_year.update_layout(height=400, xaxis_title="Year Became Unicorn", yaxis_title="Total Valuation ($B)")
    st.plotly_chart(fig_year, use_container_width=True)
    st.caption(f"Showing {len(val_by_year)} years")
else:
    fig_year = px.line(
        val_by_year,
        x="Year",
        y="Valuation ($B)",
        markers=True,
        labels={"Valuation ($B)": "Total Valuation ($B)"},
    )
    fig_year.update_traces(line_color="#636EFA")
    fig_year.update_layout(height=400, xaxis_title="Year Became Unicorn", yaxis_title="Total Valuation ($B)")
    st.plotly_chart(fig_year, use_container_width=True)
    st.caption(f"Showing {len(val_by_year)} years")

# Top Countries by Number of Unicorns
st.subheader("Top Countries by Number of Unicorns")
country_counts = (
    filtered_df.drop_duplicates("Company")["Country"].value_counts().head(15).reset_index()
)
country_counts.columns = ["Country", "Unicorn Count"]
fig_country = px.bar(country_counts, x="Country", y="Unicorn Count", text="Unicorn Count")
fig_country.update_layout(height=400)
st.plotly_chart(fig_country, use_container_width=True)

# Industry distribution
st.subheader("Industry Distribution")
industry_counts = (
    filtered_df.drop_duplicates("Company")["Industry"].value_counts().reset_index()
)
industry_counts.columns = ["Industry", "Unicorn Count"]
fig_industry = px.bar(industry_counts, x="Industry", y="Unicorn Count", text="Unicorn Count")
fig_industry.update_layout(height=400)
st.plotly_chart(fig_industry, use_container_width=True)

# Funding vs. Valuation scatterplot
st.subheader("Funding vs. Valuation (per Unicorn)")
scatter_df = (
    filtered_df.drop_duplicates("Company")
    .dropna(subset=["Funding ($B)"])
)
if scatter_df.empty:
    st.warning("No data for current filters – showing all companies instead.")
    scatter_df = df.drop_duplicates("Company").dropna(subset=["Funding ($B)"])
    fig_scatter = px.scatter(
        scatter_df,
        x="Funding ($B)",
        y="Valuation ($B)",
        color="Industry",
        hover_data=["Company", "Country"],
        labels={"Funding ($B)": "Funding ($B)", "Valuation ($B)": "Valuation ($B)"},
    )
    fig_scatter.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=0.5, color="DarkSlateGrey")))
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption(f"{len(scatter_df)} companies plotted")
else:
    fig_scatter = px.scatter(
        scatter_df,
        x="Funding ($B)",
        y="Valuation ($B)",
        color="Industry",
        hover_data=["Company", "Country"],
        labels={"Funding ($B)": "Funding ($B)", "Valuation ($B)": "Valuation ($B)"},
    )
    fig_scatter.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=0.5, color="DarkSlateGrey")))
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption(f"{len(scatter_df)} companies plotted")

st.markdown("---")

# Investor – Company Network (interactive)
with st.expander("Investor – Company Network (Interactive)"):
    top_n_investors = st.slider("Max investors to display", min_value=10, max_value=100, value=30, step=5)
    try:
        net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", directed=False)
        net.barnes_hut()

        inv_counts = (
            filtered_df[["Company", "Select Investors"]]
            .drop_duplicates()
            .groupby("Select Investors")["Company"].nunique()
            .sort_values(ascending=False)
        )
        top_investors = inv_counts.head(top_n_investors).index.tolist()
        sub_df = filtered_df[filtered_df["Select Investors"].isin(top_investors)].drop_duplicates(["Company", "Select Investors"])

        # Add nodes and edges
        for investor in top_investors:
            net.add_node(investor, label=investor, color="#1f77b4", shape="square", size=20)
        for company in sub_df["Company"].unique():
            net.add_node(company, label=company, color="#ff7f0e", shape="dot", size=12)
        for _, row in sub_df.iterrows():
            net.add_edge(row["Select Investors"], row["Company"])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            net.write_html(tmp_file.name, notebook=False, open_browser=False)
            html_content = open(tmp_file.name, "r", encoding="utf-8").read()
        components.html(html_content, height=650, scrolling=True)
        os.unlink(tmp_file.name)
    except Exception as e:
        st.error(f"Unable to render investor network: {e}")

st.caption("Data source: Maven Unicorn Challenge (March 2022)")

with st.expander("View data (first 100 rows)"):
    st.dataframe(filtered_df.head(100)) 