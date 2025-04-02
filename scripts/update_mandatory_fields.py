"""
Update sample messages to include all mandatory fields from ISO 20022 pacs.008 standard.
"""
import os
import sys
import glob
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.verify_coverage import extract_mandatory_fields, extract_fields_from_xml

def ensure_mandatory_fields(xml_file, mandatory_fields):
    """
    Ensure that an XML file includes all mandatory fields.
    
    Args:
        xml_file (str): Path to the XML file
        mandatory_fields (list): List of mandatory field dictionaries
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Checking {os.path.basename(xml_file)}...")
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
    
    existing_fields = extract_fields_from_xml(xml_file)
    
    missing_fields = []
    for field in mandatory_fields:
        field_path = field['path']
        xml_tag = field['xml_tag']
        
        path_covered = any(field_path.endswith(xml_field) or xml_field.endswith(field_path) for xml_field in existing_fields)
        tag_covered = any(xml_tag in xml_field.split('/')[-1] for xml_field in existing_fields)
        
        if not (path_covered or tag_covered):
            missing_fields.append(field)
    
    if not missing_fields:
        print(f"  All mandatory fields are present")
        return False
    
    print(f"  Missing {len(missing_fields)} mandatory fields: {[f['xml_tag'] for f in missing_fields]}")
    
    updated = False
    
    for field in missing_fields:
        field_path = field['path']
        xml_tag = field['xml_tag']
        
        path_components = field_path.split('/')
        path_components = [c for c in path_components if c]  # Remove empty strings
        
        if path_components[0] == 'Document':
            path_components = path_components[1:]
        
        current_element = root
        for i, component in enumerate(path_components[:-1]):
            found = False
            for child in current_element:
                tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if tag_name == component:
                    current_element = child
                    found = True
                    break
            
            if not found:
                new_element = ET.SubElement(current_element, component)
                current_element = new_element
                updated = True
        
        leaf_component = path_components[-1]
        found = False
        for child in current_element:
            tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag_name == leaf_component:
                found = True
                break
        
        if not found:
            if xml_tag == 'MsgId':
                ET.SubElement(current_element, leaf_component).text = f"MSG-{os.path.basename(xml_file).replace('.xml', '').replace('_', '-').upper()}-001"
            elif xml_tag == 'CreDtTm':
                ET.SubElement(current_element, leaf_component).text = "2025-04-02T15:10:00Z"
            elif xml_tag == 'NbOfTxs':
                ET.SubElement(current_element, leaf_component).text = "1"
            elif xml_tag == 'SttlmMtd':
                ET.SubElement(current_element, leaf_component).text = "CLRG"
            elif xml_tag == 'EndToEndId':
                ET.SubElement(current_element, leaf_component).text = f"E2E-{os.path.basename(xml_file).replace('.xml', '').replace('_', '-').upper()}-001"
            elif xml_tag == 'IntrBkSttlmAmt':
                amount_element = ET.SubElement(current_element, leaf_component)
                amount_element.text = "1000.00"
                amount_element.set('Ccy', "CAD")
            else:
                ET.SubElement(current_element, leaf_component)
            
            updated = True
    
    if updated:
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        with open(xml_file, 'w') as f:
            f.write(pretty_xml)
        
        print(f"  Updated {xml_file} with missing mandatory fields")
    
    return updated

def main():
    excel_file = os.path.expanduser("~/attachments/a3d8f110-7f59-403b-9340-98c29a674930/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")
    
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    mandatory_fields = extract_mandatory_fields(excel_file)
    print(f"Found {len(mandatory_fields)} mandatory fields")
    
    updated_files = 0
    for sample_file in sample_files:
        if ensure_mandatory_fields(sample_file, mandatory_fields):
            updated_files += 1
    
    print(f"Updated {updated_files} of {len(sample_files)} sample files")

if __name__ == "__main__":
    main()
