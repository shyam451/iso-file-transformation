"""
Fix XSD validation errors in XML files.
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

def fix_xsd_validation_errors(xml_file):
    """
    Fix XSD validation errors in an XML file.
    
    Args:
        xml_file (str): Path to the XML file
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Fixing XSD validation errors in {os.path.basename(xml_file)}...")
    
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ns_match = re.search(r'<(\w+):Document', content)
        ns_prefix = ns_match.group(1) if ns_match else "ns0"
        
        content = content.replace('INSTGAGT0XXX', 'INSTABCD0XXX')
        content = content.replace('INSTDAGT0XXX', 'INSTXYZW0XXX')
        
        svc_lvl_pattern = r'<{}:SvcLvl>([^<]*)</{}:SvcLvl>'.format(ns_prefix, ns_prefix)
        if re.search(svc_lvl_pattern, content):
            correct_svc_lvl = f"""
      <{ns_prefix}:SvcLvl>
        <{ns_prefix}:Cd>NURG</{ns_prefix}:Cd>
      </{ns_prefix}:SvcLvl>"""
            
            content = re.sub(svc_lvl_pattern, correct_svc_lvl, content)
        
        if 'return_payment.xml' in xml_file:
            lcl_instrm_pattern = r'<{}:LclInstrm>([^<]*)</{}:LclInstrm>'.format(ns_prefix, ns_prefix)
            if re.search(lcl_instrm_pattern, content):
                correct_lcl_instrm = f"""
      <{ns_prefix}:LclInstrm>
        <{ns_prefix}:Cd>RTGS</{ns_prefix}:Cd>
      </{ns_prefix}:LclInstrm>"""
                
                content = re.sub(lcl_instrm_pattern, correct_lcl_instrm, content)
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Successfully fixed XSD validation errors in {os.path.basename(xml_file)}")
        return True
    
    except Exception as e:
        print(f"  Error fixing XSD validation errors in {os.path.basename(xml_file)}: {e}")
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
        if fix_xsd_validation_errors(sample_file):
            fixed_files += 1
    
    print(f"Fixed XSD validation errors in {fixed_files} of {len(sample_files)} sample files")
    
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
