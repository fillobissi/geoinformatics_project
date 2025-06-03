import streamlit as st
import xarray as xr
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urlencode
from pyproj import CRS, Transformer
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import os

st.set_page_config(page_title="Heat Stress", page_icon="🏠", layout="wide")
st.title("☀️ Welcome in Heat Stress!")
st.markdown("#### Explore how climate and heat stress evolve over time in **Lombardy**")
st.write("Let's visualize a temperature map")
st.write("THIS IS A DEMO VERSION OF THE APP AND THE AVAILABLE DATES RANGE FROM 23-4-1 TO 23-9-29")

# === PARAMETRO Z EXAGGERATION ===
z_exaggeration = 0.05

# === Caricamento dati ===
dataset_path = os.path.join("Heat_stress_App", "data", "2m_air_temp_2023-04-01_2023-09-30.nc")

try:
    ds = xr.open_dataset(dataset_path)

    time_values = [pd.to_datetime(t).to_pydatetime() for t in ds["T_2M"].time.values]
    selected_time = st.slider("**Select a date**", min_value=time_values[0], max_value=time_values[-1], value=time_values[0])
    st.markdown(f"**Selected date:** {selected_time.strftime('%#d %b %y')}")
    st.markdown("Pan with your mouse to **move the map**!")
    time_index = time_values.index(selected_time)

except Exception as e:
    st.error(f"❌ Failed to load dataset: {e}")
    st.stop()

time0 = selected_time
temp_data = ds["T_2M"].sel(time=selected_time)
tempK = temp_data.values
tempC_raw = tempK - 273.15  # temperatura in °C

# === Coordinate geografiche ===
rlat = ds["rlat"].values
rlon = ds["rlon"].values
rlon2d, rlat2d = np.meshgrid(rlon, rlat)

rotated_attrs = ds["crs_rotated_latitude_longitude"].attrs
pole_lat = rotated_attrs.get("grid_north_pole_latitude", 43.0)
pole_lon = rotated_attrs.get("grid_north_pole_longitude", -170.0)

crs_rot = CRS.from_cf({
    "grid_mapping_name": "rotated_latitude_longitude",
    "grid_north_pole_latitude": pole_lat,
    "grid_north_pole_longitude": pole_lon
})
crs_target = CRS.from_epsg(4326)
transformer = Transformer.from_crs(crs_rot, crs_target, always_xy=True)
lon, lat = transformer.transform(rlon2d, rlat2d)

# Bounding box per la mappa
lat_min, lat_max = np.nanmin(lat), np.nanmax(lat)
lon_min, lon_max = np.nanmin(lon), np.nanmax(lon)
padding = 1.5
lat_min -= padding
lat_max += padding
lon_min -= padding
lon_max += padding

# Scarica mappa WMS
wms_base = "https://ows.terrestris.de/osm/service?"
params = {
    "SERVICE": "WMS",
    "VERSION": "1.1.1",
    "REQUEST": "GetMap",
    "FORMAT": "image/png",
    "TRANSPARENT": "TRUE",
    "LAYERS": "OSM-WMS",
    "STYLES": "",
    "SRS": "EPSG:4326",
    "BBOX": f"{lon_min},{lat_min},{lon_max},{lat_max}",
    "WIDTH": "512",
    "HEIGHT": "512"
}
response = requests.get(wms_base + urlencode(params))
image = Image.open(BytesIO(response.content)).convert("RGB")
map_img = np.array(image) / 255.0

# Griglia per immagine WMS
img_lat = np.linspace(lat_min, lat_max, map_img.shape[0])
img_lon = np.linspace(lon_min, lon_max, map_img.shape[1])
img_lon_grid, img_lat_grid = np.meshgrid(img_lon, img_lat)

# Calcolo superficie
base = np.nanmin(tempC_raw)
range_ = np.nanmax(tempC_raw) - base
z_surface = ((np.nanmax(tempC_raw) - tempC_raw) / range_) * z_exaggeration
surface_color = tempC_raw
custom_temp = np.expand_dims(surface_color, axis=2)

# === Plot 3D ===
fig = go.Figure()

map_gray = np.flipud(map_img.mean(axis=2))
fig.add_trace(go.Surface(
    z=np.zeros_like(img_lon_grid),
    x=img_lon_grid,
    y=img_lat_grid,
    surfacecolor=map_gray,
    colorscale="gray",
    cmin=0,
    cmax=1,
    showscale=False,
    opacity=1.0,
    hoverinfo='skip'
))

fig.add_trace(go.Surface(
    z=z_surface,
    x=lon,
    y=lat,
    surfacecolor=surface_color,
    customdata=custom_temp,
    colorscale='turbo',
    cmin=np.nanmin(tempC_raw),
    cmax=np.nanmax(tempC_raw),
    showscale=False,
    opacity=0.5,
    hovertemplate=
        "Lon: %{x:.4f}<br>" +
        "Lat: %{y:.4f}<br>" +
        "Temp: %{customdata[0]:.2f} °C<br>" +
        "<extra></extra>"
))

fig.update_layout(
    # title=f"Temperatura (°C) - {time0.strftime('%Y-%m-%d %H:%M')}",
    autosize=True,
    margin=dict(l=0, r=0, b=0, t=30),
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='manual',
        aspectratio=dict(x=1, y=1, z=z_exaggeration),
        camera=dict(
            eye=dict(x=0, y=-0.2, z=0.35),
            center=dict(x=0, y=0, z=0)
        )
    )
)

st.plotly_chart(fig, use_container_width=True)


# === Colorbar senza bordi ma con tacche e valori piccoli e grigi ===
fig_colorbar, ax = plt.subplots(figsize=(2.5, 0.05))
norm = mcolors.Normalize(vmin=np.nanmin(tempC_raw), vmax=np.nanmax(tempC_raw))
turbo = cm.get_cmap("turbo")

cb1 = plt.colorbar(
    cm.ScalarMappable(norm=norm, cmap=turbo),
    cax=ax,
    orientation='horizontal'
)

# Etichetta in piccolo e grigio
cb1.set_label("Temperature °C", fontsize=6, color="gray", labelpad=4)

# Tacche numeriche: più piccole, grigie
ax.tick_params(
    axis='x',
    colors='gray',    # colore dei numeri e tacche
    labelsize=5,      # dimensione numeri
    length=1,         # lunghezza delle tacchette (default ~6)
    width=0.2         # spessore delle tacchette (default ~1)
)

# Rimuove il bordo esterno
for spine in ax.spines.values():
    spine.set_visible(False)

# Mostra la legenda
st.pyplot(fig_colorbar)



# === Descrizione introduttiva della web app ===
st.divider()

st.markdown("## 🌡️ About this App")
st.markdown("""
Welcome to the **Heat Stress**, an interactive platform designed by Filippo Bissi to help you understand how **extreme heat** affects human well-being.

We start by showing you the **air temperature** over Northern Italy in 3D, but that's just the surface.  
In the following pages, you'll explore and compare **four key heat stress indicators**, each reflecting a different aspect of how heat and humidity are perceived or become dangerous for the human body:

---

### 🔍 The Indices We Use

- **💧 Humidex**  
  Developed in Canada, it gives a **perceived temperature** based on temperature and dew point — often producing higher values than the HI.

- **🏃‍♂️ WBGT (Wet Bulb Globe Temperature)**  
  Used globally for **occupational health** and **sports safety**, it factors in temperature, humidity, wind, and solar radiation.

- **🔬 UTCI (Universal Thermal Climate Index)**  
  A comprehensive scientific model that **integrates multiple climate variables** and simulates their effect on human thermal stress.

- **☠️ Lethal Heat Stress Index (LHSI)**  
  An advanced indicator that identifies conditions where **heat becomes life-threatening**, especially when combined with high humidity.

---

If you want to further undertand the scientific bases behind these indices I invite you to go through the comparative work of 
            [Rachid & Qureshi, 2023](https://doi.org/10.3390/cli11090181).

""")


st.markdown("---")

st.info("Use the menu on the left to explore how each index behaves across time and space!")
