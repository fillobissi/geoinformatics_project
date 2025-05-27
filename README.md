## Repository Content Overview

This repository contains Python notebooks developed as part of a geoinformatics project on climate analysis and heat stress indicators.

### 📂 Notebooks Description

- `00_Data_download.ipynb`: Connects to the CMCC DDS API and downloads hourly ERA5 downscaled climate data over Italy (2.2 km resolution). All operations run via WSL.

- `01_Data_exploration.ipynb`: Explores the raw ERA5 dataset. It includes dimensionality checks, variable validation, and regional subset for Lombardy.

- `02_Initial_data_analysis.ipynb`: Performs early-stage analysis of temperature patterns, dew point, and calculates basic statistics.

- `03_Heatstress_outputs_exploration.ipynb`: Aggregates outputs of various heat stress indices and visualizes them. Useful for validation and peak detection.

- `250520_Heat_stress_indices_81_03.ipynb`: Calculates multiple heat stress indices from meteorological variables (e.g., Heat Index, WBGT, UTCI, etc.) for 1981–2003.

- `heatstress_evolution_2023_masked.ipynb`: Final visualization of heat stress evolution in 2023 using preprocessed mask and filtered time ranges.

---

Feel free to clone and adapt for academic or research use.
