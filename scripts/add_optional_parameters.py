"""
Add optional parameters to XML files and validate against XSD schema.
This script handles the specific XML format used in the sample files.
"""
import os
import sys
import glob
import pandas as pd
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

def add_optional_parameters(xml_file, optional_fields):
    """
    Add optional parameters to an XML file.
    This function directly manipulates the XML text rather than using an XML parser.
    
    Args:
        xml_file (str): Path to the XML file
        optional_fields (dict): Dictionary containing optional fields by path
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Adding optional parameters to {os.path.basename(xml_file)}...")
    
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ns_match = re.search(r'<(\w+):Document', content)
        ns_prefix = ns_match.group(1) if ns_match else "ns0"
        
        grp_hdr_end = re.search(r'</{}:GrpHdr>'.format(ns_prefix), content)
        if grp_hdr_end:
            pos = grp_hdr_end.start()
            
            optional_grp_hdr = f"""
      <{ns_prefix}:InstgAgt>
        <{ns_prefix}:FinInstnId>
          <{ns_prefix}:BICFI>INSTGAGT0XXX</{ns_prefix}:BICFI>
        </{ns_prefix}:FinInstnId>
      </{ns_prefix}:InstgAgt>
      <{ns_prefix}:InstdAgt>
        <{ns_prefix}:FinInstnId>
          <{ns_prefix}:BICFI>INSTDAGT0XXX</{ns_prefix}:BICFI>
        </{ns_prefix}:FinInstnId>
      </{ns_prefix}:InstdAgt>"""
            
            content = content[:pos] + optional_grp_hdr + content[pos:]
        
        rmt_inf_match = re.search(r'<{}:RmtInf>'.format(ns_prefix), content)
        cdt_trf_end = re.search(r'</{}:CdtTrfTxInf>'.format(ns_prefix), content)
        
        if rmt_inf_match:
            pos = rmt_inf_match.start()
        elif cdt_trf_end:
            pos = cdt_trf_end.start()
        else:
            pos = None
        
        if pos:
            optional_cdt_trf = f"""
      <{ns_prefix}:InstrForCdtrAgt>
        <{ns_prefix}:Cd>PHOB</Cd>
        <{ns_prefix}:InstrInf>Please contact beneficiary by phone before credit</InstrInf>
      </{ns_prefix}:InstrForCdtrAgt>
      <{ns_prefix}:Purp>
        <{ns_prefix}:Cd>CASH</Cd>
      </{ns_prefix}:Purp>
      <{ns_prefix}:RgltryRptg>
        <{ns_prefix}:DbtCdtRptgInd>CRED</DbtCdtRptgInd>
        <{ns_prefix}:Authrty>
          <{ns_prefix}:Nm>Regulatory Authority</Nm>
          <{ns_prefix}:Ctry>CA</Ctry>
        </{ns_prefix}:Authrty>
      </{ns_prefix}:RgltryRptg>"""
            
            content = content[:pos] + optional_cdt_trf + content[pos:]
        
        if 'return_payment.xml' in xml_file:
            content = re.sub(r'<{}:RtrRsnInf>.*?</{}:RtrRsnInf>'.format(ns_prefix, ns_prefix), '', content, flags=re.DOTALL)
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Successfully added optional parameters to {os.path.basename(xml_file)}")
        return True
    
    except Exception as e:
        print(f"  Error adding optional parameters to {os.path.basename(xml_file)}: {e}")
        return False

def create_validation_report(sample_files, validation_results):
    """
    Create a validation report for the sample files.
    
    Args:
        sample_files (list): List of sample file paths
        validation_results (dict): Dictionary mapping file paths to validation results
        
    Returns:
        str: Path to the validation report file
    """
    report_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "xsd_validation_report.md")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# XSD Validation Report\n\n")
        f.write("This report shows the validation results of the sample XML files against the ISO 20022 XSD schema.\n\n")
        
        f.write("## Summary\n\n")
        valid_count = sum(1 for result in validation_results.values() if result['valid'])
        f.write(f"- {valid_count} of {len(sample_files)} sample files are valid according to the XSD schema\n\n")
        
        f.write("## Detailed Results\n\n")
        
        for sample_file in sample_files:
            basename = os.path.basename(sample_file)
            f.write(f"### {basename}\n\n")
            
            if sample_file in validation_results:
                result = validation_results[sample_file]
                f.write(f"- Valid according to XSD schema: {'Yes' if result['valid'] else 'No'}\n")
                
                if not result['valid'] and 'errors' in result:
                    f.write("- Validation errors:\n")
                    for error in result['errors']:
                        f.write(f"  - {error}\n")
            else:
                f.write("- Could not validate against XSD schema\n")
            
            f.write("\n")
    
    print(f"Created validation report at {report_file}")
    return report_file

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
    
    updated_files = 0
    for sample_file in sample_files:
        if add_optional_parameters(sample_file, optional_fields):
            updated_files += 1
    
    print(f"Added optional parameters to {updated_files} of {len(sample_files)} sample files")
    
    xsd_file = download_xsd_schema()
    
    validation_results = {}
    
    if xsd_file:
        for sample_file in sample_files:
            try:
                result = validate_against_xsd(sample_file, xsd_file)
                
                validation_results[sample_file] = {
                    'valid': result
                }
                
                if not result:
                    xmlschema_doc = etree.parse(xsd_file)
                    xmlschema = etree.XMLSchema(xmlschema_doc)
                    
                    xml_doc = etree.parse(sample_file)
                    
                    xmlschema.validate(xml_doc)
                    
                    validation_results[sample_file]['errors'] = [str(error) for error in xmlschema.error_log]
            except Exception as e:
                validation_results[sample_file] = {
                    'valid': False,
                    'errors': [str(e)]
                }
        
        valid_count = sum(1 for result in validation_results.values() if result['valid'])
        print(f"{valid_count} of {len(sample_files)} sample files are valid according to the XSD schema")
    
    create_validation_report(sample_files, validation_results)

if __name__ == "__main__":
    main()
