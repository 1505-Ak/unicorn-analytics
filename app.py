import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Unicorn Analytics Dashboard", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/katiehuangx/Maven-Unicorn-Challenge/main/unicorn_companies_clean.csv"

@st.cache_data(show_spinner=False)
def load_data(url: str) -> pd.DataFrame:
    """Load unicorn dataset from remote CSV."""
    df = pd.read_csv(url, parse_dates=["Date Joined"])
    df["Valuation ($B)"] = df["Valuation"] / 1e9
    df.dropna(subset=["Valuation"], inplace=True)
    return df

# Load data
with st.spinner("Loading unicorn dataset..."):
    df = load_data(DATA_URL)

st.title("🦄 Global Unicorn Companies — Analytics")

# Sidebar filters
st.sidebar.header("Filters")

industries = sorted(df["Industry"].unique())
selected_industries = st.sidebar.multiselect("Industry", industries, default=industries)

countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect("Country", countries, default=countries)

years = df["Year Founded"].sort_values().unique()
min_year, max_year = int(years.min()), int(years.max())
selected_year_range = st.sidebar.slider("Year Founded Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Apply filters
mask = (
    df["Industry"].isin(selected_industries)
    & df["Country"].isin(selected_countries)
    & df["Year Founded"].between(*selected_year_range)
)
filtered_df = df[mask]

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Unicorns", f"{filtered_df['Company'].nunique():,}")
with col2:
    total_valuation = filtered_df.drop_duplicates("Company")["Valuation ($B)"].sum()
    st.metric("Total Valuation ($B)", f"{total_valuation:,.1f}")
with col3:
    avg_year = filtered_df["Year Founded"].mean()
    st.metric("Avg. Year Founded", f"{avg_year:.0f}")
with col4:
    avg_valuation = filtered_df.drop_duplicates("Company")["Valuation ($B)"].mean()
    st.metric("Avg. Valuation per Unicorn ($B)", f"{avg_valuation:,.2f}")

st.markdown("---")

# Valuations over time
st.subheader("Valuations Over Time")
val_by_year = (
    filtered_df.drop_duplicates("Company")
    .groupby(filtered_df["Date Joined"].dt.year)["Valuation ($B)"].sum()
    .reset_index(name="Total Valuation ($B)")
)
fig_year = px.line(
    val_by_year,
    x="Date Joined",
    y="Total Valuation ($B)",
    markers=True,
    labels={"Date Joined": "Year Became Unicorn"},
)
fig_year.update_layout(height=400)
st.plotly_chart(fig_year, use_container_width=True)

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

st.markdown("---")

st.caption("Data source: Maven Unicorn Challenge (March 2022)") 