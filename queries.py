
"""
queries.py
Loads fact and dimension tables from warehouse and provides helper functions
"""

import pandas as pd
import os

WAREHOUSE_DIR = "../warehouse"

def load_fact():
    return pd.read_csv(os.path.join(WAREHOUSE_DIR, "fact_transport.csv"))

def load_gender(years=None):
    df = pd.read_csv(os.path.join(WAREHOUSE_DIR, "dim_gender.csv"))
    return df

def load_causes(years=None):
    df = pd.read_csv(os.path.join(WAREHOUSE_DIR, "dim_causes.csv"))
    return df

def load_vehicle_distribution(years=None):
    df = pd.read_csv(os.path.join(WAREHOUSE_DIR, "dim_vehicle_distribution.csv"))
    return df

def filter_fact(df, years=None, regions=None):
    filtered = df.copy()
    if years:
        filtered = filtered[filtered["YEAR"].isin(years)]
    if regions:
        filtered = filtered[filtered["Region"].isin(regions)]
    return filtered
