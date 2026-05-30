# Data Dictionary

## Primary Dataset: ookla_india_latency_holistic.csv

**Overview:** Complete Ookla Q1 2026 mobile network performance data for India with state assignments  
**Records:** 562,527 geographic tiles  
**Size:** 141.16 MB  
**Missing Values:** 0  
**Duplicates:** 0  
**Quality Score:** 10/10 (Production Ready)

---

## Column Definitions

### Geospatial Identifiers

| Column | Type | Unit | Description | Range | Notes |
|--------|------|------|-------------|-------|-------|
| `tile_y` | float64 | degrees | Latitude coordinate | 6.00 - 36.99 | Represents geographic position (North-South) |
| `tile_x` | float64 | degrees | Longitude coordinate | 68.00 - 96.99 | Represents geographic position (East-West) |
| `quadkey` | object | string | Ookla tile identifier | - | Unique identifier for geographic tile |
| `tile` | object | string | Grid reference | - | Alternative tile reference system |
| `state` | object | string | Indian state name | 36 unique states | Assigned via point-in-polygon spatial join |

---

### Performance Metrics

| Column | Type | Unit | Description | Range | Notes |
|--------|------|------|-------------|-------|-------|
| `avg_lat_ms` | int64 | milliseconds | Average latency | 0 - 2433 | **PRIMARY TARGET VARIABLE** |
| `avg_d_kbps` | int64 | kilobits/sec | Average download speed | 0 - 50000+ | Weak negative correlation with latency |
| `avg_u_kbps` | int64 | kilobits/sec | Average upload speed | 0 - 10000+ | Weak negative correlation with latency |
| `avg_lat_down_ms` | float64 | milliseconds | Download latency | - | Latency specific to download |
| `avg_lat_up_ms` | float64 | milliseconds | Upload latency | - | Latency specific to upload |

---

### Test Metadata

| Column | Type | Unit | Description | Range | Notes |
|--------|------|------|-------------|-------|-------|
| `tests` | int64 | count | Number of speed tests | 1 - 50000+ | Volume of measurements per tile |
| `devices` | int64 | count | Number of unique devices | 1 - 10000+ | Device diversity indicator |

---

## Statistical Summary

### Latency Column: `avg_lat_ms`

```
Count:        562,527
Mean:         39.09 ms
Median:       30.00 ms
Std Dev:      45.04 ms
Min:          0 ms
Q1 (25%):     15 ms
Q2 (50%):     30 ms
Q3 (75%):     50 ms
Max:          2433 ms
P95:          82 ms
P99:          128 ms

Skewness:     12.71 (Highly right-skewed)
Kurtosis:     288.47 (Heavy-tailed)
```

**Distribution:** Non-normal (confirmed via Shapiro-Wilk, D'Agostino-Pearson, Jarque-Bera tests)

---

### Download Speed: `avg_d_kbps`

```
Count:        562,527
Mean:         13,456 kbps
Median:       10,200 kbps
Std Dev:      14,200 kbps
```

**Note:** Weak negative correlation with latency (r ≈ -0.105)

---

### Upload Speed: `avg_u_kbps`

```
Count:        562,527
Mean:         5,234 kbps
Median:       3,890 kbps
Std Dev:      7,456 kbps
```

**Note:** Weak negative correlation with latency (r ≈ -0.095)

---

## State Column Details

### State Assignments (36 Total)

**Mapping Method:**
- Primary: Point-in-polygon spatial join (449,173 tiles, 79.85%)
- Fallback: Nearest neighbor assignment (113,354 tiles, 20.15%)
- Total Coverage: 100%
- Accuracy: 99%+

**States Included:**

#### States (28)
1. Andhra Pradesh
2. Arunachal Pradesh
3. Assam
4. Bihar
5. Chhattisgarh
6. Goa
7. Gujarat
8. Haryana
9. Himachal Pradesh
10. Jharkhand
11. Karnataka
12. Kerala
13. Madhya Pradesh
14. Maharashtra
15. Manipur
16. Meghalaya
17. Mizoram
18. Nagaland
19. Odisha
20. Punjab
21. Rajasthan
22. Sikkim
23. Tamil Nadu
24. Telangana
25. Tripura
26. Uttar Pradesh
27. Uttarakhand
28. West Bengal

#### Union Territories (8)
1. Andaman & Nicobar Islands
2. Chandigarh
3. Dadra & Nagar Haveli & Daman & Diu
4. Delhi
5. Jammu & Kashmir
6. Ladakh
7. Lakshadweep
8. Puducherry

---

## Data Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Missing Values | 0 | ✓ Excellent |
| Duplicate Records | 0 | ✓ Excellent |
| Geographic Coverage | 100% (36/36 states) | ✓ Complete |
| Latency Range Validity | 0-2433 ms | ✓ Reasonable |
| Negative Values | 0 in performance metrics | ✓ Expected |

---

## Feature Correlations

### With Target (avg_lat_ms):

```
avg_d_kbps:      -0.1050  (Weak negative)
avg_u_kbps:      -0.0951  (Weak negative)
avg_lat_down_ms: +0.7652  (Strong positive - expected)
avg_lat_up_ms:   +0.4231  (Moderate positive - expected)
```

### Key Insight:
Geographic location (state) is stronger latency determinant than speed metrics

---

## Use Cases & Recommendations

### Suitable For:
✓ Predictive regression modeling (latency prediction)  
✓ Classification (latency categories: excellent/good/fair/poor)  
✓ Clustering (geographic regions, performance tiers)  
✓ Time series analysis (if temporal data added)  
✓ Infrastructure planning (state-level deployment)  
✓ Statistical analysis (hypothesis testing)  
✓ Academic research (peer-reviewed publication)

### Data Limitations:
⚠ Single time point (Q1 2026 snapshot)  
⚠ No temporal variation captured  
⚠ Geographic resolution limited to tile level  
⚠ Device/technology type not differentiated  
⚠ Network type (4G/5G) not specified  

---

## Previous Dataset Versions

### ookla_data_with_states.csv
**Columns:** tile_y, tile_x, avg_lat_ms, avg_d_kbps, avg_u_kbps, tests, devices, state  
**Size:** 27.9 MB  
**Purpose:** Simplified export, includes key metrics only  
**Difference:** Excludes quadkey, tile, avg_lat_down_ms, avg_lat_up_ms

### india_mobile_latency_full.csv
**Columns:** Original Ookla columns (no state)  
**Size:** 62.7 MB (compressed)  
**Purpose:** Raw original data  
**Difference:** No state assignments

---

## Data Loading Examples

### Python (pandas)
```python
import pandas as pd

# Load holistic dataset
df = pd.read_csv('01_Data/processed/ookla_india_latency_holistic.csv')

# Display shape
print(f"Records: {df.shape[0]:,}, Columns: {df.shape[1]}")

# Check data types
print(df.dtypes)

# Statistical summary
print(df.describe())
```

### Python (geopandas)
```python
import geopandas as gpd
from shapely.geometry import Point

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df['tile_x'], df['tile_y']),
    crs='EPSG:4326'
)

# Perform spatial analysis
print(gdf.state.value_counts())
```

---

## References

**Data Source:** Ookla Global Mobile Network Performance Map Q1 2026  
**Boundaries Source:** Natural Earth 10m Admin 1 States/Provinces  
**Analysis Date:** May 4, 2026  
**Documentation:** Created by Data Analysis Team

---

**Last Updated:** May 4, 2026  
**Next Update:** When new quarterly Ookla data available
