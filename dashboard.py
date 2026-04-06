# dashboard.py — Air Quality Dashboard (Fixed)

import streamlit as st
import pandas as pd
import plotly.express as px
from azure.storage.blob import BlobServiceClient
import os
import io

# ─────────────────────────────
# PAGE CONFIG
# ─────────────────────────────
st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Air Quality Dashboard (Azure Pipeline) ✅ LIVE DEMO")

# ─────────────────────────────
# LOAD DATA FROM AZURE
# ─────────────────────────────
# Cache expires every 300 seconds (5 mins) — reloads fresh data from Azure automatically
@st.cache_data(ttl=300)
def load_data():
    conn_str = os.environ.get("AZURE_CONN_STR", "")

    if not conn_str:
        st.error("❌ AZURE_CONN_STR is not set")
        st.stop()

    client = BlobServiceClient.from_connection_string(conn_str)

    blob = client.get_blob_client(
        container="projectcontaineroutput",
        blob="results.csv"
    )

    data = blob.download_blob().readall()
    df = pd.read_csv(io.BytesIO(data))

    return df

df = load_data()

# ─────────────────────────────
# SIDEBAR FILTER
# ─────────────────────────────
st.sidebar.header("Filters")

countries = df["country"].unique()
selected_country = st.sidebar.multiselect(
    "Select countries",
    countries,
    default=countries
)

df_filtered = df[df["country"].isin(selected_country)]

# ─────────────────────────────
# KPI METRICS
# ─────────────────────────────
col1, col2, col3, col4 = st.columns(4)

col1.metric("Countries", len(df_filtered))
col2.metric("Avg Actual AQI",    f"{df_filtered['avg_actual_aqi'].mean():.1f}")
col3.metric("Avg Predicted (LR)", f"{df_filtered['avg_predicted_lr'].mean():.1f}")
col4.metric("Avg Predicted (DT)", f"{df_filtered['avg_predicted_dt'].mean():.1f}")

# ─────────────────────────────
# BAR CHART — ACTUAL AQI BY COUNTRY
# ─────────────────────────────
st.subheader("Actual AQI by Country")

fig_bar = px.bar(
    df_filtered.sort_values("avg_actual_aqi", ascending=False),
    x="country",
    y="avg_actual_aqi",
    color="avg_actual_aqi",
    color_continuous_scale="RdYlGn_r",
    labels={"avg_actual_aqi": "Actual AQI", "country": "Country"}
)

st.plotly_chart(fig_bar, use_container_width=True)

# ─────────────────────────────
# BAR CHART — ACTUAL vs PREDICTED AQI
# ─────────────────────────────
st.subheader("Actual vs Predicted AQI by Country")

df_melted = df_filtered.melt(
    id_vars="country",
    value_vars=["avg_actual_aqi", "avg_predicted_lr", "avg_predicted_dt"],
    var_name="Model",
    value_name="AQI"
)

df_melted["Model"] = df_melted["Model"].replace({
    "avg_actual_aqi":    "Actual",
    "avg_predicted_lr":  "Linear Regression",
    "avg_predicted_dt":  "Decision Tree"
})

fig_grouped = px.bar(
    df_melted.sort_values("AQI", ascending=False),
    x="country",
    y="AQI",
    color="Model",
    barmode="group",
    labels={"country": "Country"},
    color_discrete_map={
        "Actual":            "#636EFA",
        "Linear Regression": "#EF553B",
        "Decision Tree":     "#00CC96"
    }
)

st.plotly_chart(fig_grouped, use_container_width=True)

# ─────────────────────────────
# SCATTER — Linear Regression Predicted vs Actual
# ─────────────────────────────
st.subheader("Predicted (LR) vs Actual AQI")

fig_scatter = px.scatter(
    df_filtered,
    x="avg_actual_aqi",
    y="avg_predicted_lr",
    hover_name="country",
    size="avg_actual_aqi",
    color="avg_predicted_dt",
    color_continuous_scale="Turbo",
    labels={
        "avg_actual_aqi":   "Actual AQI",
        "avg_predicted_lr": "Predicted AQI (LR)",
        "avg_predicted_dt": "Predicted AQI (DT)"
    }
)

st.plotly_chart(fig_scatter, use_container_width=True)

# ─────────────────────────────
# MAP — Actual AQI
# ─────────────────────────────
st.subheader("World Map — Actual AQI")

fig_map = px.choropleth(
    df_filtered,
    locations="country",
    locationmode="country names",
    color="avg_actual_aqi",
    hover_name="country",
    color_continuous_scale="RdYlGn_r",
    labels={"avg_actual_aqi": "Actual AQI"}
)

st.plotly_chart(fig_map, use_container_width=True)

# ─────────────────────────────
# DATA TABLE
# ─────────────────────────────
st.subheader("Data Table")

st.dataframe(df_filtered, use_container_width=True)

# ─────────────────────────────
# FOOTER
# ─────────────────────────────
st.markdown("---")
st.caption("Pipeline: Azure → Docker → Kubernetes → Jenkins | Auto-refreshes every 5 minutes")
