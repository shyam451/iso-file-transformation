"""
Generate ISO 20022 XML messages based on payment scenarios with proper amount handling.
"""
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os

def create_sample_xml(scenario, message_structure, output_dir=None):
    """
    Create a sample XML message for a payment scenario with proper amount handling.
    
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
    
    processed_paths = set()
    
    for path, value in scenario['key_fields'].items():
        if 'IntrBkSttlmAmt' in path or 'InstdAmt' in path or 'EqvtAmt' in path:
            continue  # Skip amount fields for now
            
        elements = path.split('/')
        elements = [e for e in elements if e]  # Remove empty strings
        
        elements = elements[2:]  # Skip Document and FIToFICstmrCdtTrf
        
        if elements[0] == "CdtTrfTxInf":
            elements = elements[1:]
        
        current_element = cdt_trf_tx_inf
        
        if elements and elements[-1] == 'Ccy':
            continue  # Skip currency attributes for now
        
        for i, element_name in enumerate(elements[:-1]):
            existing = current_element.find(element_name)
            if existing is not None:
                current_element = existing
            else:
                new_element = ET.SubElement(current_element, element_name)
                current_element = new_element
        
        leaf_name = elements[-1]
        ET.SubElement(current_element, leaf_name).text = value
        processed_paths.add(path)
    
    amount_fields = {}
    
    for path, value in scenario['key_fields'].items():
        if 'Amt' in path:
            if path.endswith('/Ccy'):
                amount_path = path[:-4]  # Remove /Ccy
                if amount_path not in amount_fields:
                    amount_fields[amount_path] = {'amount': None, 'currency': value}
                else:
                    amount_fields[amount_path]['currency'] = value
            elif any(amt in path for amt in ['IntrBkSttlmAmt', 'InstdAmt', 'EqvtAmt']):
                if path not in amount_fields:
                    amount_fields[path] = {'amount': value, 'currency': 'CAD'}  # Default currency
                else:
                    amount_fields[path]['amount'] = value
    
    for path, details in amount_fields.items():
        elements = path.split('/')
        elements = [e for e in elements if e]  # Remove empty strings
        
        elements = elements[2:]  # Skip Document and FIToFICstmrCdtTrf
        
        if elements[0] == "CdtTrfTxInf":
            elements = elements[1:]
        
        current_element = cdt_trf_tx_inf
        
        for i, element_name in enumerate(elements[:-1]):
            existing = current_element.find(element_name)
            if existing is not None:
                current_element = existing
            else:
                new_element = ET.SubElement(current_element, element_name)
                current_element = new_element
        
        amount_element = ET.SubElement(current_element, elements[-1])
        amount_element.text = details['amount']
        amount_element.set('Ccy', details['currency'])
    
    if not amount_fields:
        default_amount = "1000.00"
        if scenario['name'] == "High-Value Payment":
            default_amount = "1000000.00"
        
        currency = "CAD"  # Default currency
        
        intr_amt = ET.SubElement(cdt_trf_tx_inf, "IntrBkSttlmAmt")
        intr_amt.text = default_amount
        intr_amt.set("Ccy", currency)
    
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
