# Module 1: DATA COLLECTION & UNDERSTANDING

## Step-by-Step Data Exploration Plan

### **Phase 1A: Load & Inspect Ookla Data (562,527 records)**

**File:** `data/final_engineered_dataset.csv`

**What to check:**
```
1. Dataset shape: (rows, columns)
2. Column names & data types
3. Sample rows
4. Missing values (null count)
5. Unique values for categorical columns
6. Statistical summary (mean, median, std, min, max)
7. Geographic coverage (lat/lon distribution)
8. Latency distribution (target variable)
```

**Example findings to document:**
```
- Total records: 562,527
- States covered: 28-36?
- Latency range: 5ms to 500ms?
- Mean latency: ~40ms?
- Geographic grid coverage: Uniform or clustered?
```

---

### **Phase 1B: Load & Inspect TRAI Data (1,767 records)**

**File:** `TRAI_2025_all_states_5operators_12months.csv` (you'll download this)

**What to check:**
```
1. Dataset shape
2. Operators present: JIO, AIRTEL, VODAFONE, BSNL, VI?
3. States covered
4. Technology types: 4G, 5G, 3G?
5. Speed stats (download, upload in Kbps)
6. Signal strength distribution (dBm)
7. Monthly temporal coverage (Jan-Dec 2025?)
```

**Example findings to document:**
```
- Operators: 5 (JIO, AIRTEL, VODAFONE, BSNL, VI)
- States: 36
- Technology: 4G, 5G
- Speed range: 11 Kbps to 150,000 Kbps
- Signal range: -109 dBm to -71 dBm
```

---

### **Phase 1C: Load & Inspect Germany Data**

**File:** `data/raw/Germany/analysis_data_Osnabrück.csv`

**What to check:**
```
1. Number of records
2. Columns: download, upload, ping_avg, timestamp
3. Time period covered
4. Speed range (Mbps)
5. Latency/ping range (ms)
6. Consistency (std dev)
```

**Example findings:**
```
- Records: ~5,000-10,000
- Download speed: 10-100 Mbps
- Latency: 10-50ms (lower than India)
- Time period: Jan 2024 - Mar 2025
```

---

### **Phase 1D: Load & Inspect Netherlands Data**

**File:** `data/raw/Netherlands/analysis_data_Enschede.csv`

**Similar checks as Germany**

---

### **Phase 1E: Comparison Summary**

**Create a comparison table:**
```
╔════════════════════════════════════════════════════════════╗
║           DATA OVERVIEW - INITIAL STATISTICS               ║
╠════════════════════════════════════════════════════════════╣
║ Metric              │ Ookla   │ TRAI  │ Germany │ NLD    ║
├─────────────────────┼─────────┼───────┼─────────┼────────┤
║ Records             │ 562,527 │ 1,767 │ ~10K    │ ~10K   ║
║ Geographic regions  │ 36 states│ 36   │ 1 city  │ 1 city ║
║ Latency range (ms)  │ 5-500   │ N/A   │ 10-50   │ 10-50  ║
║ Speed range (Mbps)  │ 0-100   │ Kbps  │ 10-100  │ 10-100 ║
║ Main feature        │ Latency │ Speed │ Speed   │ Speed  ║
║ Source              │ Global  │ TRAI  │ iperf   │ iperf  ║
╚════════════════════════════════════════════════════════════╝
```

---

## KEY DATA CHARACTERISTICS YOU'LL FIND

### **Ookla Data (MOST IMPORTANT)**

**Geographic aspects:**
- Latitude/Longitude: Global coverage, but we focus on India (6-37°N, 68-97°E)
- 562K geographic tiles = very dense coverage
- State information needed (lat/lon → state mapping)

**Latency characteristics:**
- Right-skewed distribution (long tail of high-latency outliers)
- May have non-normal distribution
- Spatial correlation (nearby tiles have similar latency)

**Potential missing data:**
- Some regions may have sparse coverage
- Urban vs rural coverage imbalance?

---

### **TRAI Data (OPERATOR INSIGHTS)**

**Operator dimension:**
- JIO, AIRTEL, VODAFONE, BSNL, VI
- Performance differences due to infrastructure age, spectrum, investment

**Technology dimension:**
- 4G vs 5G adoption
- Speed bottlenecks in 4G regions

**Geographic dimension:**
- State-level variation in infrastructure quality
- Urban metro vs tier-2 cities vs rural

**Temporal dimension:**
- Monthly patterns (monsoon vs summer)
- Off-peak vs peak traffic implications

---

### **Germany & Netherlands (EUROPE BASELINE)**

**Why important:**
- Developed countries = mature infrastructure
- Baseline for comparison: India networks perform how vs developed nations?
- Show that models work globally (not India-specific)

**Characteristics:**
- Much lower latency (10-50ms vs India 30-100ms)
- Higher speeds (50-100 Mbps vs India 5-50 Mbps)
- More consistent (lower variance)
- Fewer regional variations

---

## DATA QUALITY ISSUES TO WATCH FOR

1. **Outliers in latency**
   - 500+ ms latencies (network failures?)
   - Keep or remove? Document decision

2. **Missing operators in some states**
   - TRAI data may not have all operators in all states
   - Impact on fairness of comparison

3. **Temporal misalignment**
   - Ookla: When was this data collected?
   - TRAI: 2025 data
   - Germany/NLD: Different time periods
   - Need to handle carefully in analysis

4. **Geographic misalignment**
   - Ookla tiles have (lat, lon) but need state labels
   - Spatial join required (point-in-polygon)
   - Already done in your holistic dataset?

5. **Scale differences**
   - Speed in Kbps (TRAI) vs Mbps (Germany/NLD)
   - Need normalization for fair comparison

---

## EXPLORATION OUTPUTS YOU'LL CREATE

**For your FYP report, create:**

### **1. Data Summary Report** (`data_summary_report.txt`)
```
OOKLA INDIA DATASET
- Total records: 562,527
- Date range: [fill in]
- Geographic extent: [N/S/E/W boundaries]
- States/territories: 36
- Mean latency: 39.09 ms
- Median latency: 30 ms
- Std dev: [calc]
- 95th percentile: [calc]
- Outliers (>300ms): [count]

TRAI 2025 DATASET
- Total records: ~20,000 (estimate)
- Operators: JIO, AIRTEL, VODAFONE, BSNL, VI
- States covered: 36
- Technology: 4G, 5G
- Mean speed: [calc] Kbps
- Signal range: -109 to -71 dBm

GERMANY (Osnabrück)
- Records: ~5,000
- Mean speed: [calc] Mbps
- Mean latency: [calc] ms

NETHERLANDS (Enschede)
- Records: ~5,000
- Mean speed: [calc] Mbps
- Mean latency: [calc] ms
```

### **2. Missing Values Report** (`missing_values_report.txt`)
```
Ookla:
- Column: missing_count (%)
- latitude: 0 (0%)
- longitude: 0 (0%)
- state: [X] ([Y]%)
- avg_lat_ms: [X] ([Y]%)
...

TRAI:
- operator: 0 (0%)
- signal_strength: [X] ([Y]%)
...
```

### **3. Distribution Visualizations** (PNG files)
```
- Ookla_latency_histogram.png (showing right-skew)
- Ookla_latency_by_state_boxplot.png
- TRAI_speed_by_operator_boxplot.png
- Germany_vs_NLD_latency_comparison.png
- Geographic_coverage_map.png (tile density)
```

### **4. Correlation Matrix** (`correlation_analysis.txt`)
```
Ookla features:
- Latency vs Longitude? (geographic gradient?)
- Latency vs [other features]
- Spearman & Pearson correlations

TRAI features:
- Speed vs Signal Strength
- Speed vs Operator
- Speed vs Technology (4G vs 5G)
```

---

## DATA EXPLORATION SCRIPT TEMPLATE

```python
# 01_data_collection_understanding.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ===== LOAD DATASETS =====
print("Loading Ookla data...")
ookla = pd.read_csv('data/final_engineered_dataset.csv')

print("Loading TRAI data...")
trai = pd.read_csv('data/TRAI_2025_all_states_5operators.csv')

print("Loading Germany data...")
germany = pd.read_csv('data/raw/Germany/analysis_data_Osnabrück.csv')

print("Loading Netherlands data...")
netherlands = pd.read_csv('data/raw/Netherlands/analysis_data_Enschede.csv')

# ===== OOKLA EXPLORATION =====
print("\n" + "="*50)
print("OOKLA DATA EXPLORATION")
print("="*50)

print(f"Shape: {ookla.shape}")
print(f"\nColumns: {ookla.columns.tolist()}")
print(f"\nData types:\n{ookla.dtypes}")
print(f"\nFirst 5 rows:\n{ookla.head()}")
print(f"\nBasic statistics:\n{ookla.describe()}")
print(f"\nMissing values:\n{ookla.isnull().sum()}")

# Latency analysis (key target variable)
print(f"\nLATENCY ANALYSIS:")
print(f"  Mean: {ookla['avg_lat_ms'].mean():.2f} ms")
print(f"  Median: {ookla['avg_lat_ms'].median():.2f} ms")
print(f"  Std Dev: {ookla['avg_lat_ms'].std():.2f} ms")
print(f"  Range: {ookla['avg_lat_ms'].min():.2f} - {ookla['avg_lat_ms'].max():.2f} ms")
print(f"  Outliers (>300ms): {(ookla['avg_lat_ms'] > 300).sum()}")

# State analysis
print(f"\nGEOGRAPHIC COVERAGE:")
print(f"  States: {ookla['state'].nunique()}")
print(f"  Records per state:\n{ookla['state'].value_counts()}")

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

axes[0, 0].hist(ookla['avg_lat_ms'], bins=50)
axes[0, 0].set_title('Ookla: Latency Distribution')
axes[0, 0].set_xlabel('Latency (ms)')

ookla.boxplot(column='avg_lat_ms', by='state', ax=axes[0, 1])
axes[0, 1].set_title('Ookla: Latency by State')

axes[1, 0].scatter(ookla['longitude'], ookla['latitude'], c=ookla['avg_lat_ms'], 
                    cmap='RdYlGn_r', alpha=0.3, s=1)
axes[1, 0].set_title('Ookla: Geographic Distribution of Latency')
axes[1, 0].set_xlabel('Longitude')
axes[1, 0].set_ylabel('Latitude')

# Similar for other datasets...
# [Germany, Netherlands, TRAI analysis]

plt.tight_layout()
plt.savefig('outputs/data_exploration_overview.png', dpi=300, bbox_inches='tight')
print("\n✓ Visualization saved to outputs/data_exploration_overview.png")

# ===== SAVE SUMMARY REPORT =====
with open('outputs/data_summary_report.txt', 'w') as f:
    f.write("DATA COLLECTION & UNDERSTANDING REPORT\n")
    f.write("="*60 + "\n\n")
    
    f.write("OOKLA INDIA DATASET\n")
    f.write("-"*60 + "\n")
    f.write(f"Shape: {ookla.shape}\n")
    f.write(f"Mean latency: {ookla['avg_lat_ms'].mean():.2f} ms\n")
    f.write(f"Median latency: {ookla['avg_lat_ms'].median():.2f} ms\n")
    f.write(f"Std dev: {ookla['avg_lat_ms'].std():.2f} ms\n\n")
    
    f.write("TRAI 2025 DATASET\n")
    f.write("-"*60 + "\n")
    f.write(f"Shape: {trai.shape}\n")
    f.write(f"Operators: {trai['operator'].unique().tolist()}\n")
    f.write(f"Mean speed: {trai['speed_kbps'].mean():.2f} Kbps\n\n")
    
    f.write("GERMANY (Osnabrück)\n")
    f.write("-"*60 + "\n")
    f.write(f"Shape: {germany.shape}\n")
    f.write(f"Mean latency: {germany['ping_avg'].mean():.2f} ms\n\n")
    
    f.write("NETHERLANDS (Enschede)\n")
    f.write("-"*60 + "\n")
    f.write(f"Shape: {netherlands.shape}\n")
    f.write(f"Mean latency: {netherlands['ping_avg'].mean():.2f} ms\n")

print("✓ Summary report saved to outputs/data_summary_report.txt")
```

---

## CHECKPOINT QUESTIONS (Before Moving to Module 2)

✅ Can you answer these?
- [ ] How many records in Ookla? How many states?
- [ ] What's the mean latency in India? In Europe?
- [ ] Which operator (Jio/Airtel/Vodafone/BSNL) has best speed in TRAI data?
- [ ] Are there missing values? Which columns?
- [ ] How does India's performance compare to Germany/Netherlands?
- [ ] What's the geographic distribution (urban vs rural)?
- [ ] Is latency normally distributed or skewed?

**If you can answer these, Module 1 is complete!**

---

## NEXT MODULE: Feature Engineering

Once you understand the data, Module 2 shows how to:
- Create 20-30 meaningful features from raw data
- Select the most important ones
- Prepare for ML model training
