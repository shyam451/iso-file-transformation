"""
Extract all optional fields and rules from the ISO 20022 Excel file.
"""
import os
import sys
import pandas as pd
import json
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def extract_all_fields(excel_file):
    """
    Extract all fields (mandatory and optional) from the Excel file.
    
    Args:
        excel_file (str): Path to the ISO 20022 Excel file
        
    Returns:
        dict: Dictionary containing all fields categorized by multiplicity
    """
    print(f"Extracting all fields from {os.path.basename(excel_file)}...")
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Full_View')
        
        df = df.dropna(how='all')
        
        path_col = None
        mult_col = None
        xml_tag_col = None
        name_col = None
        type_col = None
        definition_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            if 'path' in col_str:
                path_col = col
            elif 'mult' in col_str:
                mult_col = col
            elif 'xml tag' in col_str or 'tag' in col_str:
                xml_tag_col = col
            elif 'name' in col_str:
                name_col = col
            elif 'type' in col_str or 'code' in col_str:
                type_col = col
            elif 'definition' in col_str or 'desc' in col_str:
                definition_col = col
        
        if not all([path_col, mult_col, xml_tag_col, name_col]):
            print("Could not find all required columns in the Excel file")
            return None
        
        fields = {
            'mandatory': [],
            'optional': [],
            'conditional': []
        }
        
        for i, row in df.iterrows():
            if pd.notna(row[path_col]) and pd.notna(row[xml_tag_col]):
                path = str(row[path_col])
                xml_tag = str(row[xml_tag_col])
                name = str(row[name_col]) if pd.notna(row[name_col]) else ""
                mult = str(row[mult_col]) if pd.notna(row[mult_col]) else ""
                data_type = str(row[type_col]) if type_col and pd.notna(row[type_col]) else ""
                definition = str(row[definition_col]) if definition_col and pd.notna(row[definition_col]) else ""
                
                field = {
                    'path': path,
                    'name': name,
                    'xml_tag': xml_tag,
                    'multiplicity': mult,
                    'data_type': data_type,
                    'definition': definition
                }
                
                if mult in ['1', '1..1']:
                    fields['mandatory'].append(field)
                elif mult in ['0..1', '0..n']:
                    fields['optional'].append(field)
                else:
                    fields['conditional'].append(field)
        
        print(f"Found {len(fields['mandatory'])} mandatory fields")
        print(f"Found {len(fields['optional'])} optional fields")
        print(f"Found {len(fields['conditional'])} conditional fields")
        
        return fields
    
    except Exception as e:
        print(f"Error extracting fields from Excel: {e}")
        return None

def extract_all_rules(excel_file):
    """
    Extract all rules from the Excel file.
    
    Args:
        excel_file (str): Path to the ISO 20022 Excel file
        
    Returns:
        list: List of dictionaries containing rule information
    """
    print(f"Extracting all rules from {os.path.basename(excel_file)}...")
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Rules')
        
        df = df.dropna(how='all')
        
        header_row = None
        for i, row in df.iterrows():
            if 'Index' in str(row.iloc[0]):
                header_row = i
                break
        
        if header_row is None:
            print("Could not find header row in Rules sheet")
            return []
        
        rules_df = df.iloc[header_row+1:].copy()
        
        rules_df.columns = ['Index', 'Name', 'Definition'] + list(rules_df.columns[3:])
        
        rules = []
        
        for _, row in rules_df.iterrows():
            if pd.notna(row['Index']) and pd.notna(row['Name']):
                rule = {
                    'index': str(row['Index']),
                    'name': str(row['Name']),
                    'definition': str(row['Definition']) if pd.notna(row['Definition']) else ""
                }
                rules.append(rule)
        
        print(f"Found {len(rules)} rules")
        return rules
    
    except Exception as e:
        print(f"Error extracting rules from Excel: {e}")
        return []

def generate_field_examples(fields):
    """
    Generate example values for fields based on their data type.
    
    Args:
        fields (dict): Dictionary containing fields categorized by multiplicity
        
    Returns:
        dict: Dictionary mapping field paths to example values
    """
    examples = {}
    
    for category in fields.values():
        for field in category:
            path = field['path']
            data_type = field['data_type'].lower()
            xml_tag = field['xml_tag']
            
            if 'amount' in data_type or 'amt' in xml_tag.lower():
                examples[path] = "1000.00"
            elif 'date' in data_type or 'time' in data_type or 'dt' in xml_tag.lower():
                examples[path] = "2025-04-03T12:00:00Z"
            elif 'code' in data_type:
                examples[path] = "CODE"
            elif 'identifier' in data_type or 'id' in xml_tag.lower():
                examples[path] = f"ID-{xml_tag}-001"
            elif 'text' in data_type or 'name' in data_type:
                examples[path] = f"Sample {field['name']}"
            elif 'currency' in data_type or 'ccy' in xml_tag.lower():
                examples[path] = "CAD"
            elif 'boolean' in data_type:
                examples[path] = "true"
            elif 'number' in data_type or 'numeric' in data_type:
                examples[path] = "123"
            else:
                examples[path] = f"Sample {xml_tag}"
    
    return examples

def save_fields_to_json(fields, output_file):
    """
    Save fields to a JSON file.
    
    Args:
        fields (dict): Dictionary containing fields categorized by multiplicity
        output_file (str): Path to the output JSON file
    """
    with open(output_file, 'w') as f:
        json.dump(fields, f, indent=2)
    
    print(f"Saved fields to {output_file}")

def save_rules_to_json(rules, output_file):
    """
    Save rules to a JSON file.
    
    Args:
        rules (list): List of dictionaries containing rule information
        output_file (str): Path to the output JSON file
    """
    with open(output_file, 'w') as f:
        json.dump(rules, f, indent=2)
    
    print(f"Saved rules to {output_file}")

def save_examples_to_json(examples, output_file):
    """
    Save example values to a JSON file.
    
    Args:
        examples (dict): Dictionary mapping field paths to example values
        output_file (str): Path to the output JSON file
    """
    with open(output_file, 'w') as f:
        json.dump(examples, f, indent=2)
    
    print(f"Saved examples to {output_file}")

def main():
    excel_file = os.path.expanduser("~/attachments/a3d8f110-7f59-403b-9340-98c29a674930/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")
    
    fields = extract_all_fields(excel_file)
    rules = extract_all_rules(excel_file)
    
    if fields:
        examples = generate_field_examples(fields)
        
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reference")
        os.makedirs(output_dir, exist_ok=True)
        
        save_fields_to_json(fields, os.path.join(output_dir, "all_fields.json"))
        save_rules_to_json(rules, os.path.join(output_dir, "all_rules.json"))
        save_examples_to_json(examples, os.path.join(output_dir, "field_examples.json"))

if __name__ == "__main__":
    main()
