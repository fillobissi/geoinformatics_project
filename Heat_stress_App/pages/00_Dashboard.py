from functions import (
    calculate_heat_index,
    calculate_humidex,
    calculate_wbt,
    calculate_wbgt,
    calculate_lethal_heat_stress_index,
    calculate_utci,
    calculate_relative_humidity
)
import streamlit as st
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime
import time
import seaborn as sns
from pyproj import Transformer
from matplotlib.colors import Normalize, TwoSlopeNorm
import os
import gdown
import urllib.request

# --- CONFIG PAGINA ---
st.set_page_config(layout="wide")
st.title("📊 Dashboard")
st.markdown("#### From 1981 to 2023 everyday heat stress indices and climatological indicators")

# === Funzione per caricare in modo sicuro i dataset ===
def load_nc_datasets():
    try:
        st.info("📂 Caricamento NetCDF dai file della repository...")

        # Percorsi relativi compatibili con Streamlit Cloud
        temp_path = os.path.join("Heat_stress_App", "data", "2m_air_temp_2023-04-01_2023-09-30.nc")
        dew_path  = os.path.join("Heat_stress_App", "data", "2m_dew_point_temp_2023-04-01_2023-09-30.nc")

        # Controllo esistenza
        if not os.path.exists(temp_path) or not os.path.exists(dew_path):
            st.error("❌ Uno o entrambi i file .nc non sono stati trovati nella directory 'data/'.")
            st.stop()

        # Caricamento
        ds_temp = xr.open_dataset(temp_path)
        ds_dew = xr.open_dataset(dew_path)

        st.success("✅ File NetCDF caricati correttamente.")
        return ds_temp, ds_dew

    except Exception as e:
        st.error("❌ Errore durante il caricamento dei NetCDF.")
        st.exception(e)
        st.stop()

# --- CARICAMENTO DATASET ---
dataset3, dataset2 = load_nc_datasets()

# --- 2. SELEZIONE DATA ---
all_times = pd.to_datetime(dataset3['T_2M'].time.values)
all_dates = np.unique(all_times.date)
st.write("THIS IS A DEMO VERSION OF THE APP AND THE AVAILABLE DATES RANGE FROM 23-4-1 TO 23-9-29")
selected_date = st.date_input("Date to be visualized:", all_dates[0], min_value=all_dates[0], max_value=all_dates[-1])
mask = (all_times.date == selected_date)
times_for_day = all_times[mask]
if len(times_for_day) == 0:
    st.error("No data available for the selected date!")
    st.stop()

available_times = [t.strftime("%H:%M") for t in times_for_day]
selected_time_str = st.selectbox("Time to be visualized:", available_times, index=0)
selected_time = datetime.combine(selected_date, datetime.strptime(selected_time_str, "%H:%M").time())

with st.spinner("Wait for it..."):
    time.sleep(2)
st.success("Done!")

# --- 3. ESTRAZIONE DATI ---
timestamp = pd.to_datetime(selected_time)
temperature_snapshot = dataset3['T_2M'].sel(time=timestamp)
dew_point_snapshot = dataset2['TD_2M'].sel(time=timestamp)
dew_point_filtered = dew_point_snapshot.where(dew_point_snapshot > 243.15)
dew_point_interpolated = dew_point_filtered.interpolate_na(dim='rlat', method='linear').interpolate_na(dim='rlon', method='linear')

RH = calculate_relative_humidity(temperature_snapshot - 273.15, dew_point_interpolated - 273.15)

heat_index_data = calculate_heat_index(temperature_snapshot - 273.15, RH)
humidex_data = calculate_humidex(temperature_snapshot, dew_point_interpolated)
wbt_data = calculate_wbt(temperature_snapshot - 273.15, RH)
wbgt_data = calculate_wbgt(temperature_snapshot - 273.15, wbt_data)
lhs_data = calculate_lethal_heat_stress_index(wbt_data, RH)
utci_data = calculate_utci(temperature_snapshot - 273.15, RH)
rh_data = RH

# --- 4. SOGLIE ---
thresholds = {
    "Humidex": "Danger above 45°C",
    "WBGT": "Danger above 30°C",
    "Lethal Heat Stress Index": "Danger above 27°C",
    "UTCI": "Danger above 46°C",
    "Relative Humidity": "Discomfort above 70%",
    "Temperature": "Reference at 2m height"
}

# --- 5. COLORMAP ---
cmaps = {
    "Humidex": "plasma",
    "WBGT": "viridis",
    "Lethal Heat Stress Index": "coolwarm",
    "UTCI": "cividis",
    "Relative Humidity": "Blues"
}

# --- 6. FUNZIONE MAPPA CON BASEMAP ---
def plot_map_with_basemap(data, title, cmap="inferno", size=6, title_size=14, alpha=0.6):
    lat = dataset3['lat'].values
    lon = dataset3['lon'].values

    fig, ax = plt.subplots(figsize=(size, size))
    vmin = np.nanmin(data.values)
    vmax = np.nanmax(data.values)

    lon1d = lon[0, :] if lon.ndim == 2 else lon
    lat1d = lat[:, 0] if lat.ndim == 2 else lat
    extent = [lon1d.min(), lon1d.max(), lat1d.min(), lat1d.max()]

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    xmin, ymin = transformer.transform(extent[0], extent[2])
    xmax, ymax = transformer.transform(extent[1], extent[3])
    extent_3857 = [xmin, xmax, ymin, ymax]

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ctx.add_basemap(ax, crs="EPSG:3857", source=ctx.providers.OpenStreetMap.Mapnik, attribution=False)

    im = ax.imshow(data.values, extent=extent_3857, origin="lower", cmap=cmap, alpha=alpha, vmin=vmin, vmax=vmax)
    ax.set_title(title, fontsize=title_size, fontweight='bold', pad=12)
    ax.axis("off")

    cbar = plt.colorbar(im, ax=ax, orientation="horizontal", pad=0.02, aspect=30, shrink=1.0)
    if "Humidity" in title:
        cbar.set_label("Relative Humidity [%]", fontsize=8)
        tick_locs = cbar.get_ticks()
        cbar.set_ticks(tick_locs)
        cbar.set_ticklabels([f"{int(t)}%" for t in tick_locs])
    else:
        cbar.set_label("Unit: °C", fontsize=8)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(labelsize=7)

    threshold_text = thresholds.get(title, "")
    ax.text(0.5, -0.25, threshold_text, ha='center', fontsize=9, transform=ax.transAxes)

    fig.tight_layout()
    return fig

# --- 7. VISUALIZZAZIONE ---
st.markdown("### 🌡️ Climatological indicators")
col_env = st.columns([1, 1])
with col_env[0]:
    st.pyplot(plot_map_with_basemap(temperature_snapshot - 273.15, "Temperature", cmap="inferno"))
with col_env[1]:
    st.pyplot(plot_map_with_basemap(rh_data, "Relative Humidity", cmap="Blues"))

st.markdown("---")
st.markdown("### 🔥 Heat Stress Indices")
col_ind1 = st.columns([1, 1])
with col_ind1[0]:
    st.pyplot(plot_map_with_basemap(humidex_data, "Humidex", cmap=cmaps["Humidex"]))
with col_ind1[1]:
    st.pyplot(plot_map_with_basemap(wbgt_data, "WBGT", cmap=cmaps["WBGT"]))
col_ind2 = st.columns([1, 1])
with col_ind2[0]:
    st.pyplot(plot_map_with_basemap(lhs_data, "Lethal Heat Stress Index", cmap=cmaps["Lethal Heat Stress Index"]))
with col_ind2[1]:
    st.pyplot(plot_map_with_basemap(utci_data, "UTCI", cmap=cmaps["UTCI"]))


# --- 8. STATISTICA ---
st.markdown("---")
st.markdown("### 📊 Indices Statistical Summary")
summary_matrix = {
    "Humidex (°C)": (humidex_data, 45),
    "WBGT (°C)": (wbgt_data, 30),
    "Lethal Heat Stress Index (°C)": (lhs_data, 27),
    "UTCI (°C)": (utci_data, 46)
}

matrix_values = {
    "Mean": [],
    "Median": [],
    "95th percentile": [],
    "99th percentile": [],
    "Maximum": []
}

thresholds_list = []

for key, (array, threshold) in summary_matrix.items():
    flat = array.values.flatten()
    clean = flat[~np.isnan(flat)]
    matrix_values["Mean"].append(np.mean(clean))
    matrix_values["Median"].append(np.median(clean))
    matrix_values["95th percentile"].append(np.percentile(clean, 95))
    matrix_values["99th percentile"].append(np.percentile(clean, 99))
    matrix_values["Maximum"].append(np.max(clean))
    thresholds_list.append(threshold)



matrix_df = pd.DataFrame(matrix_values).T
matrix_df.columns = list(summary_matrix.keys())

# --- NUOVA VISUALIZZAZIONE HEATMAP CON NORMALIZZAZIONE PER COLONNA ---
fig, ax = plt.subplots(figsize=(9, 3.2))
num_rows, num_cols = matrix_df.shape

# Disegna manualmente le celle
for row in range(num_rows):
    for col in range(num_cols):
        val = matrix_df.iloc[row, col]
        threshold = thresholds_list[col]
        norm = TwoSlopeNorm(vmin=0, vcenter=threshold, vmax=threshold * 2)
        color = plt.cm.seismic(norm(val))
        ax.add_patch(plt.Rectangle((col, row), 1, 1, color=color))
        ax.text(col + 0.5, row + 0.5, f"{val:.1f}",
                ha='center', va='center', fontsize=11, weight='bold', color='black')

# Imposta assi
ax.set_xlim(0, num_cols)
ax.set_ylim(0, num_rows)
ax.invert_yaxis()
ax.set_xticks(np.arange(num_cols) + 0.5)
ax.set_xticklabels(matrix_df.columns, fontsize=10, color='gray')
ax.set_yticks(np.arange(num_rows) + 0.5)
ax.set_yticklabels(matrix_df.index, fontsize=10, color='gray')
ax.tick_params(top=True, bottom=False, left=False, right=False)
ax.xaxis.set_ticks_position('top')

for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()
st.pyplot(fig)

# --- LEGENDA COLORI DELLA MATRICE ---
legend_fig, legend_ax = plt.subplots(figsize=(4, 0.1))
gradient = np.linspace(0, 1, 256).reshape(1, -1)
legend_ax.imshow(gradient, aspect='auto', cmap=plt.cm.seismic)
legend_ax.set_xticks([0, 127, 255])
legend_ax.set_xticklabels(["Below threshold", "On threshold", "Above threshold"], fontsize=4, color='gray')
legend_ax.set_yticks([])
for spine in legend_ax.spines.values():
    spine.set_visible(False)
st.pyplot(legend_fig)

st.markdown("---")
st.info("Use the menu on the left to explore how each indices performance time series!")