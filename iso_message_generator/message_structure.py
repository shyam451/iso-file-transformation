"""
Extract ISO 20022 message structure from Excel files.
"""
import pandas as pd
import os

def extract_message_structure(excel_file):
    """
    Extract the message structure from the Full_View sheet of an ISO 20022 Excel file.
    
    Args:
        excel_file (str): Path to the ISO 20022 Excel file
        
    Returns:
        dict: Dictionary containing the message structure
    """
    print("Extracting message structure...")
    
    df = pd.read_excel(excel_file, sheet_name='Full_View')
    
    df = df.dropna(how='all')
    
    df.columns = [str(col).strip() for col in df.columns]
    
    structure_df = df[['Lvl', 'Name', 'XML Tag', 'Mult', 'Type / Code', 'Path', 'Definition']]
    
    message_structure = {}
    
    for _, row in structure_df.iterrows():
        if pd.notna(row['Path']) and pd.notna(row['XML Tag']):
            path = row['Path']
            xml_tag = row['XML Tag']
            name = row['Name']
            mult = row['Mult'] if pd.notna(row['Mult']) else ""
            data_type = row['Type / Code'] if pd.notna(row['Type / Code']) else ""
            definition = row['Definition'] if pd.notna(row['Definition']) else ""
            
            message_structure[path] = {
                'name': name,
                'xml_tag': xml_tag,
                'multiplicity': mult,
                'data_type': data_type,
                'definition': definition
            }
    
    return message_structure
