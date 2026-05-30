# Project Setup Guide

## Quick Start (3 Steps)

### Step 1: Activate Virtual Environment
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
.venv\Scripts\activate.bat
```

### Step 2: Install Dependencies (if needed)
```bash
pip install -r requirements.txt
```

### Step 3: Open Jupyter Notebook
```bash
cd 02_Notebooks
jupyter notebook Ookla_India_Latency_Analysis_Professional.ipynb
```

---

## Detailed Environment Setup

### Python Version
- **Installed:** Python 3.14.2
- **Location:** `.venv/` virtual environment (Windows)
- **Status:** ✓ Ready to use

### First-Time Setup (Complete)

If starting fresh, follow these steps:

#### 1. Create Virtual Environment
```bash
python -m venv .venv
```

#### 2. Activate Virtual Environment
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
.venv\Scripts\activate.bat
```

#### 3. Install All Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Verify Installation
```python
python -c "import pandas; import geopandas; print('All packages installed!')"
```

---

## Environment Details

### Key Dependencies Installed

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| pandas | 3.0.1 | Data manipulation | ✓ |
| numpy | 2.4.2 | Numerical computing | ✓ |
| geopandas | 1.1.3 | Geospatial analysis | ✓ |
| shapely | 2.1.2 | Geometric operations | ✓ |
| scipy | 1.17.0 | Statistical analysis | ✓ |
| scikit-learn | 1.8.0 | ML algorithms | ✓ |
| matplotlib | 3.10.8 | Plotting | ✓ |
| seaborn | 0.13.2 | Statistical viz | ✓ |
| xgboost | 3.2.0 | Gradient boosting | ✓ |
| lightgbm | 4.6.0 | Light gradient boosting | ✓ |
| catboost | 1.2.10 | Categorical boosting | ✓ |
| jupyter | 1.0.0 | Notebook interface | ✓ |

### Optional Packages
For specific tasks, additional packages may be needed:

```bash
# Time series analysis
pip install statsmodels

# Deep learning
pip install tensorflow tensorflow-hub

# Advanced visualization
pip install folium  # Interactive maps
pip install plotly  # Interactive plots

# Database connectivity
pip install sqlalchemy psycopg2-binary
```

---

## Working with Jupyter Notebooks

### Start Jupyter Lab (Recommended)
```bash
# From project root
jupyter lab
```

### Start Jupyter Notebook
```bash
# From project root
jupyter notebook
```

### Launch Specific Notebook
```bash
jupyter notebook 02_Notebooks/Ookla_India_Latency_Analysis_Professional.ipynb
```

### Kernel Management
```bash
# List available kernels
jupyter kernelspec list

# Install Python kernel
python -m ipykernel install --user --name py314 --display-name "Python 3.14"

# Remove kernel
jupyter kernelspec uninstall py314
```

---

## Running Analysis

### Option 1: Execute Complete Notebook
```bash
cd 02_Notebooks
jupyter nbconvert --to notebook --execute Ookla_India_Latency_Analysis_Professional.ipynb
```

### Option 2: Run Cell by Cell in Jupyter
1. Open notebook in Jupyter
2. Use `Shift+Enter` to execute cells sequentially
3. View results and visualizations

### Option 3: Run Python Scripts
```bash
# From project root
python 03_Scripts/analysis/main_analysis.py
```

---

## Data Access

### Primary Dataset Locations

| Dataset | Path | Size | Purpose |
|---------|------|------|---------|
| Holistic | `01_Data/processed/ookla_india_latency_holistic.csv` | 141 MB | Main dataset (all columns) |
| Simplified | `01_Data/processed/ookla_data_with_states.csv` | 27.9 MB | Reduced columns export |
| Raw | `01_Data/raw/india_mobile_latency_full.csv` | 62.7 MB | Original no-state data |
| State Stats | `05_Results/reports/state_wise_latency_analysis.csv` | 3 KB | Aggregated by state |

### Load Data in Python
```python
import pandas as pd

# Load holistic dataset
df = pd.read_csv('01_Data/processed/ookla_india_latency_holistic.csv')

# Quick exploration
print(f"Shape: {df.shape}")
print(f"Memory: {df.memory_usage(deep=True).sum() / 1e9:.2f} GB")
print(df.info())
print(df.describe())
```

### Load Geospatial Data
```python
import geopandas as gpd
from shapely.geometry import Point

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df['tile_x'], df['tile_y']),
    crs='EPSG:4326'
)

# State-level analysis
print(gdf.groupby('state')['avg_lat_ms'].agg(['mean', 'median', 'std']))
```

---

## Common Tasks

### Generate Visualizations
```bash
cd 03_Scripts/analysis
python generate_visualizations.py
```

### Train ML Model
```bash
cd 03_Scripts/modeling
python train_model.py
```

### Run Analysis Pipeline
```bash
cd 03_Scripts
python run_pipeline.py
```

### Data Preprocessing
```bash
cd 03_Scripts/preprocessing
python prepare_data.py
```

---

## Troubleshooting

### Issue: Module Not Found
```bash
# Solution: Reinstall requirements
pip install --upgrade -r requirements.txt
```

### Issue: Jupyter Kernel Dead
```bash
# Solution: Restart kernel
# In Jupyter: Kernel → Restart
# Or: python -m ipykernel install --user
```

### Issue: Out of Memory
```bash
# Solution: Process data in chunks
for chunk in pd.read_csv('file.csv', chunksize=10000):
    # Process chunk
    pass
```

### Issue: Geospatial Join Too Slow
```bash
# Solution: Use spatial indexing
gdf_states.sindex  # Creates spatial index automatically
```

### Issue: File Not Found
```python
# Check current directory
import os
os.getcwd()

# Use absolute paths or navigate to correct directory
os.chdir('c:\\Users\\250019004\\FY_ML')
```

---

## Performance Tips

### Load Large CSV Efficiently
```python
# Read specific columns only
df = pd.read_csv('file.csv', usecols=['col1', 'col2', 'col3'])

# Use dtypes to optimize memory
dtypes = {'tile_y': 'float32', 'avg_lat_ms': 'int16'}
df = pd.read_csv('file.csv', dtype=dtypes)

# Read in chunks for very large files
chunks = []
for chunk in pd.read_csv('file.csv', chunksize=50000):
    chunks.append(chunk.groupby('state').agg(...))
result = pd.concat(chunks)
```

### Optimize Spatial Operations
```python
# Create spatial index before join
gdf_states.sindex
gdf_tiles.sindex

# Use predicate for efficient join
result = gpd.sjoin(gdf_tiles, gdf_states, predicate='within')
```

### Parallel Processing
```python
from joblib import Parallel, delayed

# Process in parallel
results = Parallel(n_jobs=-1)(
    delayed(process_partition)(df_partition) 
    for df_partition in partitions
)
```

---

## Version Control Setup

### Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit: FY_ML project setup"
```

### Clone (If Starting from Repository)
```bash
git clone <repository-url>
cd FY_ML
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Push to GitHub
```bash
git remote add origin https://github.com/username/FY_ML.git
git branch -M main
git push -u origin main
```

---

## IDE Setup

### VS Code
1. Install Python extension (Microsoft)
2. Select interpreter: `.\.venv\Scripts\python.exe`
3. Install Jupyter extension
4. Open notebook: `02_Notebooks/Ookla_India_Latency_Analysis_Professional.ipynb`

### PyCharm
1. Open Project
2. Configure Interpreter: `.venv`
3. Install Jupyter plugin
4. Run notebook or scripts directly

### Jupyter Lab
```bash
# Install JupyterLab
pip install jupyterlab

# Start
jupyter lab

# Access: http://localhost:8888/lab
```

---

## Next Steps

1. ✓ **Review Setup:** Confirm environment is ready
2. ✓ **Load Data:** Test data loading with sample code
3. **Explore Notebook:** Run through `02_Notebooks/` analysis
4. **Review Findings:** Check `06_Documentation/` reports
5. **Develop Models:** Create scripts in `03_Scripts/modeling/`
6. **Share Results:** Export from `05_Results/`

---

## Support & Resources

### Documentation
- **Project Overview:** `README.md`
- **Folder Structure:** `ORGANIZATION_GUIDE.md`
- **Data Details:** `DATA_DICTIONARY.md`
- **Analysis Methods:** `06_Documentation/analysis/`

### Key Files
- **Main Notebook:** `02_Notebooks/Ookla_India_Latency_Analysis_Professional.ipynb`
- **Main Dataset:** `01_Data/processed/ookla_india_latency_holistic.csv`
- **Findings:** `06_Documentation/findings/`

### External Resources
- [pandas Documentation](https://pandas.pydata.org/)
- [GeoPandas Guide](https://geopandas.org/)
- [Jupyter Documentation](https://jupyter.org/)
- [scikit-learn Tutorials](https://scikit-learn.org/stable/)

---

**Setup Date:** May 4, 2026  
**Status:** Environment Ready ✓  
**Python Version:** 3.14.2  
**All dependencies installed and verified**
