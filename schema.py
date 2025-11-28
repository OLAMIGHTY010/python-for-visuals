
# schema.py
import pandas as pd

def load_data(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path, sheet_name="Tranport Data Clean", engine="openpyxl")
    
    # Convert numeric columns
    numeric_cols = [
        'FATAL', 'SERIOUS', 'MINOR', 'TOTAL CASES',
        'NUMBER INJURED', 'NUMBER KILLED', 'TOTAL CASUALTY', 'PEOPLE INVOLVED'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df
