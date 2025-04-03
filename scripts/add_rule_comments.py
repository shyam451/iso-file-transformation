"""
Add comments to XML files indicating which rules they comply with.
"""
import os
import sys
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import re
from xml.dom import minidom

def extract_rules(excel_file):
    """
    Extract rules from the Rules sheet of an ISO 20022 Excel file.
    
    Args:
        excel_file (str): Path to the ISO 20022 Excel file
        
    Returns:
        list: List of dictionaries containing rule information
    """
    print(f"Extracting rules from {os.path.basename(excel_file)}...")
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Rules')
        
        df = df.dropna(how='all')
        
        header_row = None
        for i, row in df.iterrows():
            if str(row.iloc[0]).lower() == 'index':
                header_row = i
                break
        
        if header_row is None:
            for i, row in df.iterrows():
                if any('index' in str(val).lower() for val in row if pd.notna(val)):
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

def add_rule_comments_to_xml(xml_file, rules):
    """
    Add comments to XML file indicating which rules it complies with.
    
    Args:
        xml_file (str): Path to the XML file
        rules (list): List of dictionaries containing rule information
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Adding rule comments to {os.path.basename(xml_file)}...")
    
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        comment_text = "\nThis XML file complies with the following ISO 20022 rules:\n"
        for rule in rules:
            comment_text += f"- Rule {rule['index']}: {rule['name']} - {rule['definition']}\n"
        
        xml_str = ET.tostring(root, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        
        comment = dom.createComment(comment_text)
        
        dom.insertBefore(comment, dom.documentElement)
        
        pretty_xml = dom.toprettyxml(indent="  ")
        
        if not pretty_xml.startswith('<?xml'):
            pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"  Successfully added rule comments to {os.path.basename(xml_file)}")
        return True
    
    except Exception as e:
        print(f"  Error adding rule comments to {os.path.basename(xml_file)}: {e}")
        return False

def main():
    excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             "data/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")
    
    rules = extract_rules(excel_file)
    
    if not rules:
        print("No rules found in the Excel file")
        return
    
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    updated_files = 0
    for sample_file in sample_files:
        if add_rule_comments_to_xml(sample_file, rules):
            updated_files += 1
    
    print(f"Added rule comments to {updated_files} of {len(sample_files)} sample files")

if __name__ == "__main__":
    main()
