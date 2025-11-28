
import pandas as pd
import os

def load_fact():
    file_path = os.path.join(os.path.dirname(__file__), "New Transport Data.xlsx")
    df = pd.read_excel(file_path, sheet_name="Tranport Data Clean", engine="openpyxl")
    numeric_cols = ['FATAL', 'SERIOUS', 'MINOR', 'TOTAL CASES', 'NUMBER INJURED', 'NUMBER KILLED',
                    'TOTAL CASUALTY', 'PEOPLE INVOLVED', 'FATALITY RATE', 'SPEEDING', 'PHONE USE',
                    'TYRE BURST', 'MECHANICAL FAULT', 'BRAKE FAILURE', 'OVERLOADING', 'DANGEROUS OVERTAKE',
                    'WRONGFUL OVERTAKE', 'RECKLESS DRIVING', 'SIGNAL VIOLATION', 'OTHERS']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df
