"""
Generate all required plots for:
- India dataset: 01_Data/processed/ookla_india_latency_holistic.csv
- Wetlinks datasets: 01_Data/raw/Germany/analysis_data_Osnabrück.csv, 01_Data/raw/Netherlands/analysis_data_Enschede.csv

Outputs are saved in 05_Results/visualizations/india_and_wetlinks/
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Output directory
OUTDIR = Path("05_Results/visualizations/india_and_wetlinks")
OUTDIR.mkdir(parents=True, exist_ok=True)

# Dataset paths
INDIA_PATH = Path("outputs_v5/ookla_india_latency_holistic.csv")
GERMANY_PATH = Path("data/raw/Germany/analysis_data_Osnabrück.csv")
NLD_PATH = Path("data/raw/Netherlands/analysis_data_Enschede.csv")

# Helper for safe plot saving
def savefig(name):
    plt.tight_layout()
    plt.savefig(OUTDIR / name, dpi=300, bbox_inches="tight")
    plt.close()


# --- INDIA DATASET ---
india = pd.read_csv(INDIA_PATH)

# 1. Latency distribution
plt.figure(figsize=(10,5))
plt.hist(india['avg_lat_ms'], bins=60, color='royalblue', alpha=0.8)
plt.title('India: Latency Distribution')
plt.xlabel('Latency (ms)')
plt.ylabel('Count')
savefig('india_latency_histogram.png')

# 2. Download/Upload speed distributions
plt.figure(figsize=(10,5))
plt.hist(india['avg_d_kbps'], bins=60, color='seagreen', alpha=0.7)
plt.title('India: Download Speed Distribution')
plt.xlabel('Download Speed (Kbps)')
plt.ylabel('Count')
savefig('india_download_histogram.png')

plt.figure(figsize=(10,5))
plt.hist(india['avg_u_kbps'], bins=60, color='orange', alpha=0.7)
plt.title('India: Upload Speed Distribution')
plt.xlabel('Upload Speed (Kbps)')
plt.ylabel('Count')
savefig('india_upload_histogram.png')

# 3. Boxplot by state
plt.figure(figsize=(14,7))
order = india.groupby('state')['avg_lat_ms'].median().sort_values().index if 'state' in india.columns else None
if order is not None:
    sns.boxplot(data=india, x='state', y='avg_lat_ms', order=order, showfliers=False)
    plt.xticks(rotation=90)
    plt.title('India: Latency by State')
    plt.ylabel('Latency (ms)')
    plt.xlabel('State')
    savefig('india_latency_by_state_boxplot.png')

# 4. Correlation heatmap
plt.figure(figsize=(8,6))
cols = [c for c in ['avg_lat_ms','avg_d_kbps','avg_u_kbps','tests','devices'] if c in india.columns]
if len(cols) > 1:
    corr = india[cols].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('India: Feature Correlation Heatmap')
    savefig('india_correlation_heatmap.png')

# 5. Latency vs. Download/Upload scatter
if 'avg_d_kbps' in india.columns:
    plt.figure(figsize=(7,5))
    sns.scatterplot(x='avg_d_kbps', y='avg_lat_ms', data=india, alpha=0.2)
    plt.title('India: Latency vs Download Speed')
    plt.xlabel('Download Speed (Kbps)')
    plt.ylabel('Latency (ms)')
    savefig('india_latency_vs_download.png')

if 'avg_u_kbps' in india.columns:
    plt.figure(figsize=(7,5))
    sns.scatterplot(x='avg_u_kbps', y='avg_lat_ms', data=india, alpha=0.2)
    plt.title('India: Latency vs Upload Speed')
    plt.xlabel('Upload Speed (Kbps)')
    plt.ylabel('Latency (ms)')
    savefig('india_latency_vs_upload.png')

# 6. Geographic scatter (if available)
if 'tile_x' in india.columns and 'tile_y' in india.columns:
    plt.figure(figsize=(10,7))
    plt.scatter(india['tile_x'], india['tile_y'], c=india['avg_lat_ms'], cmap='RdYlGn_r', s=1, alpha=0.3)
    plt.colorbar(label='Latency (ms)')
    plt.title('India: Geographic Latency Distribution')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    savefig('india_geographic_latency.png')

# 7. Missing values heatmap
plt.figure(figsize=(12,6))
sns.heatmap(india.isnull(), cbar=False, cmap='viridis')
plt.title('India: Missing Values Heatmap')
savefig('india_missing_values_heatmap.png')

# 8. Pairplot (if not too large)
sample = india.sample(min(2000, len(india)), random_state=42) if len(india) > 2000 else india
pairplot_cols = [c for c in ['avg_lat_ms','avg_d_kbps','avg_u_kbps','tests','devices'] if c in india.columns]
if len(pairplot_cols) > 1:
    sns.pairplot(sample[pairplot_cols])
    plt.suptitle('India: Pairplot', y=1.02)
    savefig('india_pairplot.png')

# 9. Operator-wise boxplot (if operator column exists)
if 'operator' in india.columns:
    plt.figure(figsize=(12,6))
    sns.boxplot(data=india, x='operator', y='avg_lat_ms')
    plt.title('India: Latency by Operator')
    savefig('india_latency_by_operator_boxplot.png')

# 10. Temporal trend (if date column exists)
if 'date' in india.columns:
    india['date'] = pd.to_datetime(india['date'], errors='coerce')
    india_date = india.dropna(subset=['date'])
    if not india_date.empty:
        plt.figure(figsize=(12,6))
        india_date.groupby('date')['avg_lat_ms'].mean().plot()
        plt.title('India: Mean Latency Over Time')
        plt.ylabel('Mean Latency (ms)')
        plt.xlabel('Date')
        savefig('india_latency_over_time.png')

# --- WETLINKS: GERMANY ---
germany = pd.read_csv(GERMANY_PATH)

if 'ping_avg' in germany.columns:
    plt.figure(figsize=(10,5))
    plt.hist(germany['ping_avg'], bins=50, color='royalblue', alpha=0.8)
    plt.title('Germany: Latency Distribution')
    plt.xlabel('Latency (ms)')
    plt.ylabel('Count')
    savefig('germany_latency_histogram.png')

if 'download' in germany.columns:
    plt.figure(figsize=(10,5))
    plt.hist(germany['download'], bins=50, color='seagreen', alpha=0.7)
    plt.title('Germany: Download Speed Distribution')
    plt.xlabel('Download Speed (Mbps)')
    plt.ylabel('Count')
    savefig('germany_download_histogram.png')

if 'upload' in germany.columns:
    plt.figure(figsize=(10,5))
    plt.hist(germany['upload'], bins=50, color='orange', alpha=0.7)
    plt.title('Germany: Upload Speed Distribution')
    plt.xlabel('Upload Speed (Mbps)')
    plt.ylabel('Count')
    savefig('germany_upload_histogram.png')

if set(['download','upload','ping_avg']).issubset(germany.columns):
    plt.figure(figsize=(8,6))
    corr = germany[['download','upload','ping_avg']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Germany: Feature Correlation Heatmap')
    savefig('germany_correlation_heatmap.png')

# --- WETLINKS: NETHERLANDS ---
nld = pd.read_csv(NLD_PATH)

if 'ping_avg' in nld.columns:
    plt.figure(figsize=(10,5))
    plt.hist(nld['ping_avg'], bins=50, color='royalblue', alpha=0.8)
    plt.title('Netherlands: Latency Distribution')
    plt.xlabel('Latency (ms)')
    plt.ylabel('Count')
    savefig('nld_latency_histogram.png')

if 'download' in nld.columns:
    plt.figure(figsize=(10,5))
    plt.hist(nld['download'], bins=50, color='seagreen', alpha=0.7)
    plt.title('Netherlands: Download Speed Distribution')
    plt.xlabel('Download Speed (Mbps)')
    plt.ylabel('Count')
    savefig('nld_download_histogram.png')

if 'upload' in nld.columns:
    plt.figure(figsize=(10,5))
    plt.hist(nld['upload'], bins=50, color='orange', alpha=0.7)
    plt.title('Netherlands: Upload Speed Distribution')
    plt.xlabel('Upload Speed (Mbps)')
    plt.ylabel('Count')
    savefig('nld_upload_histogram.png')

if set(['download','upload','ping_avg']).issubset(nld.columns):
    plt.figure(figsize=(8,6))
    corr = nld[['download','upload','ping_avg']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Netherlands: Feature Correlation Heatmap')
    savefig('nld_correlation_heatmap.png')

print('All plots generated and saved to', OUTDIR)
