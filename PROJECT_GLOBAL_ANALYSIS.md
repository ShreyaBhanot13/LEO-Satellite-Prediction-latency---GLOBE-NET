# Global Network Performance Analysis Project

**Scope:** India (Ookla + operator data) + Germany + Netherlands + UK (European comparison)

---

## 📊 Project Objectives

### 1. **Regional Deep-Dive: Karnataka** ✓ (Operator Performance)
- Analyze 4 telecom operators: Jio, Airtel, Vodafone, BSNL
- Identify 2 best performers + 2 worst performers
- Root cause analysis: Why is performance different?

### 2. **State-Level Comparison** (India)
- Compare Karnataka vs other Indian states using Ookla data
- Service provider market share impact

### 3. **Global Comparison** (Cross-border insights)
- India (Ookla) vs Germany vs Netherlands
- Network infrastructure differences
- Provider ecosystem comparison

### 4. **Interactive Globe Visualization**
- 3D world map showing latency/speed by region
- Click-to-zoom for state/operator details
- Color-coded performance tiers

---

## 📁 New Project Structure

```
FY_ML/
├── 08_GLOBAL_ANALYSIS/
│   ├── 01_Data/
│   │   ├── India/
│   │   │   ├── ookla_full_india.csv (all states, Ookla)
│   │   │   ├── karnataka_operators.csv (Airtel, Jio, Vodafone, BSNL)
│   │   │   └── state_wise_summary.csv
│   │   ├── Germany/
│   │   │   ├── germany_iperf_data.csv (from your earlier analysis)
│   │   │   └── germany_operators.csv
│   │   ├── Netherlands/
│   │   │   ├── netherlands_iperf_data.csv
│   │   │   └── netherlands_operators.csv
│   │   └── global_comparison.csv (merged normalized data)
│   │
│   ├── 02_Analysis/
│   │   ├── karnataka_operator_analysis.py
│   │   ├── best_worst_providers.py (root cause analysis)
│   │   ├── state_comparison.py
│   │   ├── global_network_comparison.py
│   │   └── data_preprocessing.py
│   │
│   ├── 03_Visualizations/
│   │   ├── karnataka_providers_dashboard.py (Plotly/Dash)
│   │   ├── globe_visualization.py (Folium/Plotly globe)
│   │   ├── state_heatmap.py
│   │   └── global_comparison_charts.py
│   │
│   ├── 04_UI/
│   │   ├── app.py (Streamlit or Dash main app)
│   │   ├── pages/
│   │   │   ├── home.py
│   │   │   ├── karnataka.py (operator analysis)
│   │   │   ├── india_states.py (state comparison)
│   │   │   ├── global_map.py (globe visualization)
│   │   │   └── provider_insights.py (best/worst analysis)
│   │   └── assets/
│   │       ├── css/
│   │       └── images/
│   │
│   ├── 05_Notebooks/
│   │   ├── 01_EDA_Karnataka_Operators.ipynb
│   │   ├── 02_Best_Worst_Analysis.ipynb
│   │   ├── 03_Global_Comparison.ipynb
│   │   └── 04_Visualization_Tests.ipynb
│   │
│   ├── 06_Reports/
│   │   ├── karnataka_findings.md
│   │   ├── global_insights.md
│   │   └── recommendations.md
│   │
│   └── README_GLOBAL.md
```

---

## 🎯 Analysis Pipeline

### **Phase 1: Karnataka Operator Analysis**
**Input:** `karnataka_operators.csv` (1,767 records)

**Steps:**
1. Load operator performance data (Airtel, Jio, Vodafone, BSNL)
2. Calculate metrics by operator:
   - Mean/median latency
   - Download/upload speeds
   - Signal strength
   - Coverage (% of tiles)
   - Consistency (std deviation)

3. **Identify Best 2 & Worst 2:**
   ```
   Best: Highest speed + lowest latency + strongest signal
   Worst: Lowest speed + highest latency + weakest signal
   ```

4. **Root Cause Analysis - Why?**
   - Infrastructure age
   - Technology mix (4G vs 5G)
   - Spectrum allocation
   - Geographic coverage patterns
   - Tower density
   - Backhaul capacity

---

### **Phase 2: India State-Level Comparison**
**Input:** Ookla data (562,527 tiles across 36 states)

**Analysis:**
- State-wise latency rankings
- Provider market share impact by state
- Geographic clusters (metros vs tier-2 vs rural)
- North/South/East/West regional patterns

---

### **Phase 3: Global Comparison**
**Input:** Germany + Netherlands + India datasets

**Comparison Dimensions:**
1. **Network Performance**
   - Latency: India vs Europe
   - Download/upload speeds
   - Consistency (jitter, packet loss if available)

2. **Provider Ecosystem**
   - Number of providers
   - Market concentration
   - Performance spread (best vs worst delta)

3. **Infrastructure Maturity**
   - 4G/5G adoption rates
   - Urban vs rural divide
   - Technology investment levels

---

### **Phase 4: Interactive Visualizations**

#### **Dashboard 1: Karnataka Operators**
- 4-panel comparison (Airtel vs Jio vs Vodafone vs BSNL)
- Metrics: Speed, Latency, Signal, Consistency
- Downloadable reports per operator

#### **Dashboard 2: India States**
- Interactive heatmap: Latency by state
- Drill-down: Click state → operator breakdown
- Market share pie chart

#### **Dashboard 3: Globe Visualization**
- 3D world map (Plotly Globe)
- Hover: See latency/speed at each country
- Color scale: Red (poor) → Green (excellent)
- Zoom into India, Germany, Netherlands
- Click to see state/regional breakdown

#### **Dashboard 4: Root Cause Analysis**
- Best vs Worst operator comparison (radar charts)
- Infrastructure investment correlation
- Technology adoption impact
- Geographic advantage analysis

---

## 🛠️ Tech Stack

### **Backend:**
- Python 3.14
- pandas, numpy, scipy (data processing)
- geopandas, folium (geo-visualization)

### **Frontend (UI):**
- **Option A: Streamlit** (fastest to build, interactive)
- **Option B: Dash/Plotly** (more professional dashboards)
- **Option C: Flask + React** (full custom control)

### **Visualization:**
- Plotly (interactive 3D globe)
- Folium (geographic heatmaps)
- Matplotlib/Seaborn (statistical plots)
- Dash/Streamlit (UI framework)

### **Deployment:**
- Local: `streamlit run app.py`
- Cloud: Heroku, AWS, or Azure

---

## 📈 Key Metrics to Track

### **Karnataka Operators:**
- Mean latency (ms)
- P95 latency (95th percentile)
- Download speed (Kbps)
- Upload speed (Kbps)
- Signal strength (-dBm)
- Consistency score (inverse of std dev)
- Coverage % (tiles with service)

### **State Comparison:**
- Mean latency by state
- Latency variance (std dev)
- Provider diversity (# of providers)
- Urban/rural split
- Top operator per state

### **Global:**
- India latency vs Europe
- Speed comparison
- Provider count
- Market concentration (HHI)
- Technology adoption (% 5G)

---

## 🎨 UI Mockup - Main Features

```
┌─────────────────────────────────────────────┐
│  Global Network Performance Analysis        │
├─────────────────────────────────────────────┤
│ 📍 SELECT REGION:                           │
│  ☐ India (All States)                       │
│  ☑ Karnataka (Operators)                    │
│  ☐ Germany                                  │
│  ☐ Netherlands                              │
│                                             │
│ 🗺️ GLOBE VIEW (3D Interactive Map)          │
│   [Click to zoom / Hover for details]      │
│                                             │
│ 📊 ANALYTICS:                               │
│  ┌─────────────────────────────────────┐   │
│  │ Top 2 Performers | Bottom 2         │   │
│  │ [Radar Charts]   | [Radar Charts]   │   │
│  └─────────────────────────────────────┘   │
│                                             │
│ 📋 INSIGHTS:                                │
│  • Why is Jio #1 in Karnataka?              │
│  • Why is BSNL #4? (Infrastructure gap)    │
│  • India vs Global: Where we stand         │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🚀 Implementation Roadmap

### **Week 1: Data Preparation**
- [ ] Move/organize Germany & Netherlands data
- [ ] Extract Karnataka state data from Ookla
- [ ] Clean operator performance dataset
- [ ] Create normalized global dataset

### **Week 2: Analysis**
- [ ] Karnataka operator analysis
- [ ] Best/worst provider profiling
- [ ] State-level ranking system
- [ ] Global comparison metrics

### **Week 3: Visualization**
- [ ] Create Plotly globe
- [ ] Build Streamlit/Dash app
- [ ] Interactive dashboards
- [ ] 3D globe integration

### **Week 4: Refinement & Presentation**
- [ ] Performance optimization
- [ ] Report generation
- [ ] Final UI polish
- [ ] Deployment & demo

---

## 📥 Datasets Required

### **Current (Have):**
- ✓ India Ookla (562,527 tiles)
- ✓ Karnataka operators (1,767 records)
- ✓ Germany data (from earlier analysis)
- ✓ Netherlands data (from earlier analysis)

### **Missing (Optional):**
- Germany/Netherlands operator breakdown (to match India analysis)
- 5G coverage maps (for context)
- Population density (to contextualize)

---

## 💡 Root Cause Hypotheses for Karnataka Operators

### **Why Jio Might Be #1:**
- Newer infrastructure (recent 4G rollout)
- Largest capex investment
- Best spectrum allocation
- Dense tower deployment
- 5G investments

### **Why BSNL Might Be #4:**
- Aging infrastructure
- Limited capex budget
- Older technology stack
- Lower tower density
- Government-driven (not market-driven)

### **Investigation Methods:**
1. Correlate speeds with tower density
2. Compare technology deployment dates
3. Analyze spectrum bands used
4. Check investment reports (annual)
5. Map geographic coverage patterns

---

## ✅ Deliverables

1. **Interactive Globe Visualization** (3D world map)
2. **Karnataka Operator Analysis Report** (Best/Worst breakdown)
3. **Global Comparison Dashboard** (India vs Europe)
4. **Streamlit/Dash Web App** (Multi-page interactive UI)
5. **Root Cause Analysis** (Why differences exist)
6. **Technical Documentation** (How to extend/modify)

---

**Next Steps:**
1. ✓ Confirm you have Germany/Netherlands data files
2. ✓ Decide on UI framework (Streamlit vs Dash vs Flask+React)
3. Start Phase 1: Karnataka operator analysis
4. Build visualizations incrementally

Would you like me to start with any specific phase?
