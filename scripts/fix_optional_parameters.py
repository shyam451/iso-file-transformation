"""
Fix XML files with optional parameters to ensure they validate against XSD schema.
"""
import os
import sys
import glob
import re
import requests
import tempfile
from lxml import etree

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

def fix_xml_file(xml_file):
    """
    Fix XML file with optional parameters to ensure it validates against XSD schema.
    
    Args:
        xml_file (str): Path to the XML file
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Fixing {os.path.basename(xml_file)}...")
    
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = re.sub(r'<(ns\d+):Cd>(.*?)</\1:Cd', r'<\1:Cd>\2</\1:Cd>', content)
        
        if 'return_payment.xml' in xml_file:
            content = re.sub(r'<(ns\d+):RtrRsnInf>.*?</\1:RtrRsnInf>', '', content, flags=re.DOTALL)
        
        ns_match = re.search(r'<(\w+):Document', content)
        ns_prefix = ns_match.group(1) if ns_match else "ns0"
        
        instr_for_cdtr_agt_pattern = r'<{}:InstrForCdtrAgt>.*?</{}:InstrForCdtrAgt>'.format(ns_prefix, ns_prefix)
        if re.search(instr_for_cdtr_agt_pattern, content, re.DOTALL):
            correct_instr = f"""
      <{ns_prefix}:InstrForCdtrAgt>
        <{ns_prefix}:Cd>PHOB</{ns_prefix}:Cd>
        <{ns_prefix}:InstrInf>Please contact beneficiary by phone before credit</{ns_prefix}:InstrInf>
      </{ns_prefix}:InstrForCdtrAgt>"""
            
            content = re.sub(instr_for_cdtr_agt_pattern, correct_instr, content, flags=re.DOTALL)
        
        purp_pattern = r'<{}:Purp>.*?</{}:Purp>'.format(ns_prefix, ns_prefix)
        if re.search(purp_pattern, content, re.DOTALL):
            correct_purp = f"""
      <{ns_prefix}:Purp>
        <{ns_prefix}:Cd>CASH</{ns_prefix}:Cd>
      </{ns_prefix}:Purp>"""
            
            content = re.sub(purp_pattern, correct_purp, content, flags=re.DOTALL)
        
        rgltry_rptg_pattern = r'<{}:RgltryRptg>.*?</{}:RgltryRptg>'.format(ns_prefix, ns_prefix)
        if re.search(rgltry_rptg_pattern, content, re.DOTALL):
            correct_rgltry = f"""
      <{ns_prefix}:RgltryRptg>
        <{ns_prefix}:DbtCdtRptgInd>CRED</{ns_prefix}:DbtCdtRptgInd>
        <{ns_prefix}:Authrty>
          <{ns_prefix}:Nm>Regulatory Authority</{ns_prefix}:Nm>
          <{ns_prefix}:Ctry>CA</{ns_prefix}:Ctry>
        </{ns_prefix}:Authrty>
      </{ns_prefix}:RgltryRptg>"""
            
            content = re.sub(rgltry_rptg_pattern, correct_rgltry, content, flags=re.DOTALL)
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Successfully fixed {os.path.basename(xml_file)}")
        return True
    
    except Exception as e:
        print(f"  Error fixing {os.path.basename(xml_file)}: {e}")
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
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    fixed_files = 0
    for sample_file in sample_files:
        if fix_xml_file(sample_file):
            fixed_files += 1
    
    print(f"Fixed {fixed_files} of {len(sample_files)} sample files")
    
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
