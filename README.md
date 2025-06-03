# 🔥 Heat Stress Analysis in Lombardy

This repository was created by **Filippo Bissi** as part of the Geoinformatics Engineering MSc program at **Politecnico di Milano** (2024–2025).  
It includes a complete pipeline for analyzing **heat stress indices** from ERA5 downscaled climate data and visualizing results through a **Streamlit-based web application**.

---

## 📁 Repository Structure Overview

### 📊 Notebooks

| Filename                                | Description |
|----------------------------------------|-------------|
| `00_Data_download.ipynb`               | Connects to the CMCC DDS API and downloads hourly ERA5 downscaled climate data over Italy (to be run with WSL/Linux). |
| `01_Data_exploration.ipynb`            | Explores the raw ERA5 dataset. Includes dimensionality checks, basic visualizations, and variable validation. |
| `02_Initial_data_analysis.ipynb`       | Performs early-stage analysis of temperature patterns, spatial anomalies, and computes preliminary statistics. |
| `03_Heat_stress_indices_extraction.ipynb` | Calculates heat stress indices such as Lethal Heat Stress Index, WBGT, UTCI, Humidex, etc. |
| `04_Heatstress_outputs_exploration.ipynb` | Aggregates outputs of various indices, computes thresholds, and explores extreme events. |
| `05_Dataset_reduction_for_demo.ipynb`  | Reduces full-resolution datasets into a lightweight version for use in public deployment. |
| `heatstress_evolution_2023_masked.ipynb` | GIF-based visualization of heat stress progression for summer 2023. |

---

## 🌐 Heat Stress App (Streamlit)

An interactive web application to explore spatial and temporal patterns of heat stress across Lombardy, based on downscaled ERA5 data.

### 🚀 Link to the App

👉 [Launch the App](https://heatstressapp.streamlit.app)  

### 🛠 Built With

- `Streamlit`
- `xarray`, `pandas`, `numpy`
- `matplotlib`, `seaborn`, `plotly`
- `contextily`, `rioxarray`, `geopandas`
- ERA5 downscaled datasets (via CMCC DDS)

### 🧭 App Pages

| Page              | Description |
|-------------------|-------------|
| **HeatStress**    | Main landing page with 3D visualization of temperature over Lombardy. |
| **Dashboard**     | Daily time series of all computed heat stress indices. |
| **Trend Analyzer**| Long-term evolution plots based on climatological thresholds. |

---

## 📁 Folder: `Heat_stress_App/`

Contains the deployed Streamlit app code and associated data:

- `HeatStress.py`: main entry point
- `pages/`: individual app pages
- `data/`: reduced-size `.nc` and `.csv` demo files
- `.streamlit/config.toml`: custom theme and server settings
- `requirements.txt`: all dependencies for deployment

---

## 📜 License

Free to clone and adapt for academic or research use.  
Feel free to reference this project in your work.

