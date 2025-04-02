"""
Generate ISO 20022 XML messages based on payment scenarios.
"""
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os

def create_sample_xml(scenario, message_structure, output_dir=None):
    """
    Create a sample XML message for a payment scenario.
    
    Args:
        scenario (dict): Dictionary containing payment scenario information
        message_structure (dict): Dictionary containing the message structure
        output_dir (str, optional): Directory to save the XML file. If None, the XML is returned as a string.
        
    Returns:
        str: Pretty-printed XML string
    """
    root = ET.Element("Document")
    root.set("xmlns", "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08")
    
    fi_to_fi = ET.SubElement(root, "FIToFICstmrCdtTrf")
    
    grp_hdr = ET.SubElement(fi_to_fi, "GrpHdr")
    
    ET.SubElement(grp_hdr, "MsgId").text = f"MSG-{scenario['name'].replace(' ', '-')}-001"
    ET.SubElement(grp_hdr, "CreDtTm").text = "2025-04-02T15:10:00Z"
    ET.SubElement(grp_hdr, "NbOfTxs").text = "1"
    ET.SubElement(grp_hdr, "SttlmInf").text = "CLRG"
    
    cdt_trf_tx_inf = ET.SubElement(fi_to_fi, "CdtTrfTxInf")
    
    for path, value in scenario['key_fields'].items():
        elements = path.split('/')
        elements = [e for e in elements if e]  # Remove empty strings
        
        elements = elements[2:]
        
        current_element = cdt_trf_tx_inf
        
        for i, element_name in enumerate(elements[:-1]):
            existing = current_element.find(element_name)
            if existing is not None:
                current_element = existing
            else:
                new_element = ET.SubElement(current_element, element_name)
                current_element = new_element
        
        leaf_name = elements[-1]
        
        if leaf_name == 'Ccy':
            parent = current_element
            parent.set('Ccy', value)
        else:
            ET.SubElement(current_element, leaf_name).text = value
    
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{scenario['name'].replace(' ', '_').lower()}.xml"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(pretty_xml)
        
        print(f"Saved sample message to {file_path}")
    
    return pretty_xml
