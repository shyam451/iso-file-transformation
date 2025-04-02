import pandas as pd
import os
import json
from pprint import pprint

# Path to the Excel file
excel_file = os.path.expanduser("~/attachments/a3d8f110-7f59-403b-9340-98c29a674930/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")

def analyze_sheet(sheet_name):
    print(f"\n\n=== Analyzing sheet: {sheet_name} ===")
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    # Skip initial empty rows if any
    df = df.dropna(how='all')
    
    # Print first few rows to understand structure
    print(f"\nFirst 10 rows of {sheet_name}:")
    print(df.head(10))
    
    # Print column information
    print("\nColumn information:")
    for col in df.columns:
        non_null = df[col].count()
        print(f"- {col}: {non_null} non-null values")
    
    return df

# Try to read the Excel file and analyze sheets
try:
    # Read the Excel file
    xls = pd.ExcelFile(excel_file)
    
    # Print sheet names
    print("Sheet names in the Excel file:")
    for sheet_name in xls.sheet_names:
        print(f"- {sheet_name}")
    
    # Analyze Light_View and Full_View sheets which likely contain the message structure
    if 'Light_View' in xls.sheet_names:
        light_view_df = analyze_sheet('Light_View')
    
    if 'Full_View' in xls.sheet_names:
        full_view_df = analyze_sheet('Full_View')
    
    # Analyze Rules sheet if it exists
    if 'Rules' in xls.sheet_names:
        rules_df = analyze_sheet('Rules')
        
except Exception as e:
    print(f"Error reading Excel file: {e}")
