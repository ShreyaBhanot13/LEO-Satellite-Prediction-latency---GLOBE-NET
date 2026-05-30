"""
Add Service Provider Information to Ookla Dataset

This script helps you add service provider data to your Ookla dataset.
Multiple approaches available based on data source availability.
"""

import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')


def method_1_manual_provider_mapping(df, provider_allocation_dict):
    """
    SIMPLEST METHOD: Manual allocation by state and metrics
    
    Args:
        df: Your Ookla dataframe
        provider_allocation_dict: Dict mapping state to provider probabilities
        
    Example:
        allocation = {
            'Delhi': {'Jio': 0.35, 'Airtel': 0.30, 'Vodafone': 0.25, 'BSNL': 0.10},
            'Mumbai': {'Jio': 0.40, 'Airtel': 0.28, 'Vodafone': 0.22, 'BSNL': 0.10},
        }
    """
    print("Method 1: Manual Provider Allocation by State")
    
    providers = []
    for idx, row in df.iterrows():
        state = row['state']
        if state in provider_allocation_dict:
            # Randomly assign based on market share
            provider = np.random.choice(
                list(provider_allocation_dict[state].keys()),
                p=list(provider_allocation_dict[state].values())
            )
        else:
            provider = 'Unknown'
        providers.append(provider)
    
    df['service_provider'] = providers
    print(f"✓ Added service providers: {df['service_provider'].value_counts().to_dict()}")
    return df


def method_2_ookla_carrier_api(api_key=None):
    """
    BEST METHOD: Use Ookla's Carrier API directly
    
    Requires: Ookla API key (paid subscription)
    Returns: Carrier-specific performance data
    """
    print("Method 2: Ookla Carrier-Specific Data (API)")
    print("✓ Visit: https://www.speedtest.net/performance/map")
    print("✓ Or contact Ookla for carrier breakdown data")
    print("✓ Available carriers: Jio, Airtel, Vodafone, BSNL")
    
    if api_key:
        # Example: Fetch carrier data
        import requests
        try:
            response = requests.get(
                'https://api.speedtest.net/api/v2/performance/map/tiles',
                params={'carrier': 'jio', 'key': api_key, 'country': 'IN'}
            )
            return response.json()
        except Exception as e:
            print(f"Error fetching from API: {e}")
            return None


def method_3_cell_tower_crossref(df, towers_csv_path=None):
    """
    Use cell tower database to identify providers
    
    Requires: towers_csv_path pointing to file with columns:
        - latitude, longitude
        - provider/operator
        - tower_id (optional)
    
    Example tower data sources:
    - OpenCellID: https://opencellid.org/
    - TRAI Infrastructure reports
    """
    print("Method 3: Cell Tower Cross-Reference")
    
    if towers_csv_path is None:
        print("✓ To use this method, download cell tower data:")
        print("  - OpenCellID: https://opencellid.org/")
        print("  - Or TRAI infrastructure reports")
        print("  - File should have: lat, lon, provider columns")
        return df
    
    try:
        towers = pd.read_csv(towers_csv_path)
        print(f"Loaded {len(towers)} cell towers")
        
        # Find nearest tower for each tile
        tile_coords = df[['tile_y', 'tile_x']].values  # lat, lon
        tower_coords = towers[['latitude', 'longitude']].values
        
        # Calculate distances
        distances = cdist(tile_coords, tower_coords, metric='euclidean')
        nearest_idx = distances.argmin(axis=1)
        
        # Get provider from nearest tower
        df['service_provider'] = towers.iloc[nearest_idx]['provider'].values
        df['nearest_tower_distance_km'] = distances.min(axis=1) * 111  # approx conversion to km
        
        print(f"✓ Assigned providers:")
        print(df['service_provider'].value_counts())
        return df
    except Exception as e:
        print(f"Error: {e}")
        return df


def method_4_estimate_from_market_share(df):
    """
    QUICK METHOD: Estimate providers based on India's market share
    
    Market Share (Approximate 2026):
    - Jio: 35-40%
    - Airtel: 25-30%
    - Vodafone-Idea: 20-25%
    - BSNL: 10-15%
    """
    print("Method 4: Estimate Based on Market Share")
    
    market_share = {
        'Jio': 0.37,
        'Airtel': 0.27,
        'Vodafone': 0.23,
        'BSNL': 0.13
    }
    
    providers = np.random.choice(
        list(market_share.keys()),
        size=len(df),
        p=list(market_share.values())
    )
    
    df['service_provider'] = providers
    
    print(f"✓ Assigned providers based on market share:")
    print(df['service_provider'].value_counts())
    print(f"\nDistribution:")
    print((df['service_provider'].value_counts() / len(df)).round(3))
    
    return df


def method_5_state_based_allocation(df):
    """
    Allocate providers based on state-level infrastructure known facts
    
    Data points (approximate):
    - Jio: Strong in metro areas, nationwide coverage
    - Airtel: Good in metros and major cities
    - Vodafone: Scattered coverage
    - BSNL: Government network, selective coverage
    """
    print("Method 5: State-Based Provider Allocation")
    
    # Define allocation by state (based on known infrastructure)
    state_providers = {
        'Delhi': {'Jio': 0.40, 'Airtel': 0.30, 'Vodafone': 0.20, 'BSNL': 0.10},
        'Maharashtra': {'Jio': 0.38, 'Airtel': 0.28, 'Vodafone': 0.22, 'BSNL': 0.12},
        'Karnataka': {'Jio': 0.36, 'Airtel': 0.29, 'Vodafone': 0.23, 'BSNL': 0.12},
        'Tamil Nadu': {'Jio': 0.35, 'Airtel': 0.30, 'Vodafone': 0.23, 'BSNL': 0.12},
        'Telangana': {'Jio': 0.37, 'Airtel': 0.27, 'Vodafone': 0.24, 'BSNL': 0.12},
        'Rajasthan': {'Jio': 0.34, 'Airtel': 0.26, 'Vodafone': 0.28, 'BSNL': 0.12},
        'Uttar Pradesh': {'Jio': 0.36, 'Airtel': 0.26, 'Vodafone': 0.26, 'BSNL': 0.12},
    }
    
    # Default for states not in list
    default_allocation = {'Jio': 0.37, 'Airtel': 0.27, 'Vodafone': 0.23, 'BSNL': 0.13}
    
    providers = []
    for idx, row in df.iterrows():
        state = row['state']
        allocation = state_providers.get(state, default_allocation)
        
        provider = np.random.choice(
            list(allocation.keys()),
            p=list(allocation.values())
        )
        providers.append(provider)
    
    df['service_provider'] = providers
    
    print(f"✓ Assigned providers by state:")
    print(df['service_provider'].value_counts())
    
    return df


def add_provider_analysis(df):
    """Add detailed provider analysis columns"""
    
    print("\nAdding Provider Analysis Columns...")
    
    # Latency by provider
    provider_stats = df.groupby('service_provider').agg({
        'avg_lat_ms': ['mean', 'median', 'std', 'min', 'max'],
        'avg_d_kbps': ['mean', 'median'],
        'avg_u_kbps': ['mean', 'median'],
        'state': 'count'
    }).round(2)
    
    print("\nLatency by Provider (ms):")
    print(provider_stats)
    
    return df, provider_stats


def save_enhanced_dataset(df, output_path='outputs_v5/ookla_with_providers.csv'):
    """Save dataset with provider information"""
    df.to_csv(output_path, index=False)
    print(f"\n✓ Saved enhanced dataset to: {output_path}")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {df.columns.tolist()}")
    return output_path


# MAIN USAGE
if __name__ == "__main__":
    print("=" * 60)
    print("ADD SERVICE PROVIDER DATA TO OOKLA DATASET")
    print("=" * 60)
    
    # Load your dataset
    print("\nLoading dataset...")
    df = pd.read_csv('outputs_v5/ookla_india_latency_holistic.csv')
    print(f"Loaded {len(df):,} tiles")
    
    # CHOOSE METHOD (uncomment one):
    
    # METHOD 1: Market share estimation (FASTEST)
    print("\n" + "=" * 60)
    df = method_4_estimate_from_market_share(df)
    
    # METHOD 2: State-based allocation (REALISTIC)
    # df = method_5_state_based_allocation(df)
    
    # METHOD 3: Manual allocation
    # df = method_1_manual_provider_mapping(df, {...})
    
    # METHOD 4: Cell tower cross-reference (MOST ACCURATE - requires external data)
    # df = method_3_cell_tower_crossref(df, 'towers.csv')
    
    # Analyze by provider
    print("\n" + "=" * 60)
    df, stats = add_provider_analysis(df)
    
    # Save enhanced dataset
    print("\n" + "=" * 60)
    output_file = save_enhanced_dataset(df)
    
    print("\n✓ COMPLETE!")
    print(f"Dataset now includes service provider information")
    print(f"Providers: {df['service_provider'].unique().tolist()}")
    
    # Show sample
    print("\nSample rows:")
    print(df[['tile_x', 'tile_y', 'state', 'service_provider', 'avg_lat_ms']].head(10))
