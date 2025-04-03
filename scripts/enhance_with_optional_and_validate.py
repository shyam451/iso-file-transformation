"""
Enhance XML files with optional parameters and validate against XSD schema.
"""
import os
import sys
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import re
import requests
import tempfile
from lxml import etree

def extract_optional_fields(excel_file):
    """
    Extract optional fields from the Full_View sheet of an ISO 20022 Excel file.
    
    Args:
        excel_file (str): Path to the ISO 20022 Excel file
        
    Returns:
        dict: Dictionary containing optional fields by path
    """
    print(f"Extracting optional fields from {os.path.basename(excel_file)}...")
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Full_View')
        
        df = df.dropna(how='all')
        
        df.columns = [str(col).strip() for col in df.columns]
        
        structure_df = df[['Lvl', 'Name', 'XML Tag', 'Mult', 'Type / Code', 'Path', 'Definition']]
        
        optional_fields = {}
        
        for _, row in structure_df.iterrows():
            if pd.notna(row['Path']) and pd.notna(row['XML Tag']) and pd.notna(row['Mult']):
                path = str(row['Path'])
                xml_tag = str(row['XML Tag'])
                mult = str(row['Mult'])
                
                if '0' in mult and '..' in mult:
                    parent_path = os.path.dirname(path)
                    if parent_path not in optional_fields:
                        optional_fields[parent_path] = []
                    
                    optional_fields[parent_path].append({
                        'path': path,
                        'xml_tag': xml_tag,
                        'multiplicity': mult,
                        'data_type': str(row['Type / Code']) if pd.notna(row['Type / Code']) else "",
                        'definition': str(row['Definition']) if pd.notna(row['Definition']) else ""
                    })
        
        print(f"Found {sum(len(fields) for fields in optional_fields.values())} optional fields")
        return optional_fields
    
    except Exception as e:
        print(f"Error extracting optional fields from Excel: {e}")
        return {}

def download_xsd_schema():
    """
    Download the ISO 20022 XSD schema for pacs.008.001.08.
    
    Returns:
        str: Path to the downloaded XSD file
    """
    print("Downloading ISO 20022 XSD schema...")
    
    try:
        url = "https://www.iso20022.org/sites/default/files/documents/messages/pacs/schemas/pacs.008.001.08.xsd"
        response = requests.get(url)
        
        if response.status_code == 200:
            xsd_file = os.path.join(tempfile.gettempdir(), "pacs.008.001.08.xsd")
            with open(xsd_file, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded XSD schema to {xsd_file}")
            return xsd_file
        else:
            print(f"Failed to download XSD schema: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"Error downloading XSD schema: {e}")
        return None

def validate_against_xsd(xml_file, xsd_file):
    """
    Validate an XML file against an XSD schema.
    
    Args:
        xml_file (str): Path to the XML file
        xsd_file (str): Path to the XSD schema file
        
    Returns:
        bool: True if validation passed, False otherwise
    """
    print(f"Validating {os.path.basename(xml_file)} against XSD schema...")
    
    try:
        xmlschema_doc = etree.parse(xsd_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        
        xml_doc = etree.parse(xml_file)
        
        result = xmlschema.validate(xml_doc)
        
        if result:
            print(f"  {os.path.basename(xml_file)} is valid according to the XSD schema")
        else:
            print(f"  {os.path.basename(xml_file)} is NOT valid according to the XSD schema")
            print(f"  Validation errors: {xmlschema.error_log}")
        
        return result
    
    except Exception as e:
        print(f"  Error validating {os.path.basename(xml_file)}: {e}")
        return False

def enhance_xml_with_optional_fields(xml_file, optional_fields):
    """
    Enhance an XML file with optional fields.
    
    Args:
        xml_file (str): Path to the XML file
        optional_fields (dict): Dictionary containing optional fields by path
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Enhancing {os.path.basename(xml_file)} with optional fields...")
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]
        
        for parent_path, fields in optional_fields.items():
            elem_path = parent_path.replace('/Document/', './').replace('/', '/')
            
            parent_elems = root.findall(elem_path)
            
            for parent_elem in parent_elems:
                for field in fields:
                    tag = field['xml_tag']
                    if parent_elem.find(tag) is None:
                        new_elem = ET.SubElement(parent_elem, tag)
                        
                        data_type = field['data_type'].lower()
                        if 'code' in data_type:
                            new_elem.text = 'OTHR'
                        elif 'amount' in data_type:
                            new_elem.text = '100.00'
                            if 'ccy' in data_type.lower():
                                new_elem.set('Ccy', 'USD')
                        elif 'date' in data_type:
                            new_elem.text = '2025-04-03'
                        elif 'time' in data_type:
                            new_elem.text = '2025-04-03T12:00:00Z'
                        elif 'indicator' in data_type:
                            new_elem.text = 'true'
                        elif 'identifier' in data_type or 'id' in data_type:
                            new_elem.text = f'ID-{tag}-001'
                        elif 'text' in data_type or 'name' in data_type:
                            new_elem.text = f'Sample {tag}'
                        else:
                            new_elem.text = f'Sample {tag} value'
        
        for elem in root.iter():
            if not elem.tag.startswith('{'):
                elem.tag = f"{{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08}}{elem.tag}"
        
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        if not pretty_xml.startswith('<?xml'):
            pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml
        
        with open(xml_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        comment_match = re.search(r'<!--(.*?)-->', original_content, re.DOTALL)
        if comment_match:
            comment = comment_match.group(0)
            pretty_xml = re.sub(r'<\?xml.*?\?>', f'<?xml version="1.0" encoding="UTF-8"?>\n{comment}', pretty_xml)
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"  Successfully enhanced {os.path.basename(xml_file)} with optional fields")
        return True
    
    except Exception as e:
        print(f"  Error enhancing {os.path.basename(xml_file)}: {e}")
        return False

def main():
    excel_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             "data/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")
    
    optional_fields = extract_optional_fields(excel_file)
    
    if not optional_fields:
        print("No optional fields found in the Excel file")
        return
    
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    enhanced_files = 0
    for sample_file in sample_files:
        if enhance_xml_with_optional_fields(sample_file, optional_fields):
            enhanced_files += 1
    
    print(f"Enhanced {enhanced_files} of {len(sample_files)} sample files with optional fields")
    
    xsd_file = download_xsd_schema()
    
    if xsd_file:
        valid_files = 0
        for sample_file in sample_files:
            if validate_against_xsd(sample_file, xsd_file):
                valid_files += 1
        
        print(f"{valid_files} of {len(sample_files)} sample files are valid according to the XSD schema")
    
    report_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "xsd_validation_report.md")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# XSD Validation Report\n\n")
        f.write("This report shows the validation results of the sample XML files against the ISO 20022 XSD schema.\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- Enhanced {enhanced_files} of {len(sample_files)} sample files with optional fields\n")
        
        if xsd_file:
            f.write(f"- {valid_files} of {len(sample_files)} sample files are valid according to the XSD schema\n\n")
        else:
            f.write("- Could not validate against XSD schema because the schema could not be downloaded\n\n")
        
        f.write("## Detailed Results\n\n")
        
        for sample_file in sample_files:
            f.write(f"### {os.path.basename(sample_file)}\n\n")
            
            if xsd_file:
                result = validate_against_xsd(sample_file, xsd_file)
                f.write(f"- Valid according to XSD schema: {'Yes' if result else 'No'}\n")
                
                if not result:
                    f.write("- Validation errors:\n")
                    try:
                        xmlschema_doc = etree.parse(xsd_file)
                        xmlschema = etree.XMLSchema(xmlschema_doc)
                        
                        xml_doc = etree.parse(sample_file)
                        
                        xmlschema.validate(xml_doc)
                        
                        for error in xmlschema.error_log:
                            f.write(f"  - {error.message}\n")
                    except Exception as e:
                        f.write(f"  - Error validating: {e}\n")
            else:
                f.write("- Could not validate against XSD schema because the schema could not be downloaded\n")
            
            f.write("\n")
    
    print(f"Created validation report at {report_file}")

if __name__ == "__main__":
    main()
