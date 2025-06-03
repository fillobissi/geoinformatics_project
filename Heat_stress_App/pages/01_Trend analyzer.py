import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb
import requests
import io
import gdown
import os


st.set_page_config(layout="wide")
st.title("📈 Trend Analyzer")
st.markdown("#### Heat stress indices throughout time")

@st.cache_data
def load_data():
    # === [COMMENTATO] SCARICAMENTO DA GOOGLE DRIVE ===
    # file_id = "1JhXcQK3YoCJQvgrD7u9CY407_AwaYKdF"
    # url = f"https://drive.google.com/uc?id={file_id}"
    # output = "heatstress.csv"
    #
    # if not os.path.exists(output):
    #     gdown.download(url, output, quiet=False)

    # === [ATTIVO] PERCORSO LOCALE ===
    output = "data/heatstress_all_timestamps_year_reduced.csv"

    # === CARICAMENTO DEL FILE ===
    df = pd.read_csv(output)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Date"] = df["Timestamp"].dt.date
    df["Year"] = df["Timestamp"].dt.year
    df["DayOfYear"] = df["Timestamp"].dt.dayofyear
    return df

df = load_data()

# === CONFIG ===
stat_column = "99° Perc. (°C)"
method_label = "99th percentile"
UTCI_FAKE_THRESHOLD = 42
UTCI_INDEX = "UTCI"
stat_thresholds = {
    "Humidex": 45,
    "Lethal Heat Stress Index": 27,
    "UTCI": UTCI_FAKE_THRESHOLD,
    "WBGT": 30
}

index_colors = {
    "Humidex": "#B6E2D3",
    "Lethal Heat Stress Index": "#E2C6F3",
    "UTCI": "#C3CBEF",
    "WBGT": "#FFD8A8"
}

indices = list(stat_thresholds.keys())

st.subheader("Select an index:")
cols = st.columns(len(indices))
selected_index = st.session_state.get("selected_index")

for i, index in enumerate(indices):
    with cols[i]:
        if st.button(index):
            st.session_state.selected_index = index
            selected_index = index

st.markdown("---")

# === HISTORICAL ANNUAL PERFORMANCE ===
title_placeholder = st.empty()
plot_placeholder = st.empty()

if not selected_index:
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('lightgray')
    ax.spines['bottom'].set_color('lightgray')
    ax.tick_params(axis='x', colors='lightgray', labelsize=8, length=0)
    ax.tick_params(axis='y', colors='lightgray', labelsize=8, length=0)
    ax.set_xlabel("Year", fontsize=9, color='lightgray')
    ax.set_ylabel("Number of exceedances", fontsize=9, color='lightgray')
    ax.set_title("Waiting for index selection", fontsize=10, color='lightgray')
    ax.grid(False)
    plot_placeholder.pyplot(fig)
else:
    df_index = df[df["Indice"] == selected_index]
    threshold = stat_thresholds[selected_index]
    grouped = df_index.groupby(["Year", "DayOfYear"])[stat_column].max().reset_index()
    grouped["Exceed"] = grouped[stat_column] > threshold
    annual_counts = grouped.groupby("Year")["Exceed"].sum()

    title_placeholder.markdown(f"### 📌 How many times **{selected_index}** overpassed its threshold in the years")
    fig, ax = plt.subplots(figsize=(10, 3))
    color = index_colors.get(selected_index, "#FFA573")
    annual_counts.plot(kind="bar", ax=ax, color=color, edgecolor="none", width=0.65)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('gray')
    ax.spines['bottom'].set_color('gray')
    ax.tick_params(axis='x', colors='gray', labelsize=8, length=0)
    ax.tick_params(axis='y', colors='gray', labelsize=8, length=0)
    ax.set_xlabel("Year", fontsize=9, color='gray')
    ax.set_ylabel("Number of exceedances", fontsize=9, color='gray')
    ax.grid(False)
    plot_placeholder.pyplot(fig)

    # === PER-YEAR DETAILED CURVE ===
    st.markdown("### 🗓️ Explore a specific year")
    st.write("THIS IS A DEMO VERSION OF THE APP AND THE AVAILABLE DATES RANGE FROM 1986 TO 2023")
    years = df_index["Year"].sort_values().unique()
    selected_year = st.selectbox("", years, key="year_selector")

    df_year = df_index[df_index["Year"] == selected_year]
    daily_max = df_year.groupby("Date")[stat_column].max()

    fig2, ax2 = plt.subplots(figsize=(10, 3))
    ax2.plot(daily_max.index, daily_max.values, color=color, alpha=0.5)

    base_rgb = np.array(to_rgb(color))
    darker_rgb = (base_rgb * 0.85).clip(0, 1)

    ax2.axhline(threshold, linestyle="--", color=darker_rgb, linewidth=1.5)
    ax2.text(daily_max.index[int(len(daily_max) * 0.8)], threshold + 0.5, "Threshold",
             color=darker_rgb, fontsize=8, va='bottom', ha='left')

    ax2.set_title(f"{selected_index} – {selected_year}", fontsize=11)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('gray')
    ax2.spines['bottom'].set_color('gray')
    ax2.tick_params(axis='x', colors='gray', labelsize=8, length=0)
    ax2.tick_params(axis='y', colors='gray', labelsize=8, length=0)
    ax2.set_xlabel("Month", fontsize=9, color='gray')
    ax2.set_ylabel("Daily max value (°C)", fontsize=9, color='gray')

    xticks = pd.date_range(start=f"{selected_year}-01-01", end=f"{selected_year}-12-31", freq="MS")
    ax2.set_xticks(xticks)
    ax2.set_xticklabels([date.strftime('%b') for date in xticks], rotation=0, fontsize=8, color='gray')

    ax2.grid(False)
    st.pyplot(fig2)

st.markdown("---")

st.info("Use the menu on the left to go back to the previous pages!")
