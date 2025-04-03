"""
Enhance XML sample messages with optional fields from the ISO 20022 standard.
"""
import os
import sys
import json
import glob
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_json_file(file_path):
    """Load a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def get_scenario_fields(scenario_name, examples):
    """Get fields specific to a payment scenario."""
    scenario_fields = {}
    
    scenario_fields['/Document/FIToFICstmrCdtTrf/GrpHdr/MsgId'] = f"MSG-{scenario_name.replace(' ', '-').upper()}-001"
    scenario_fields['/Document/FIToFICstmrCdtTrf/GrpHdr/CreDtTm'] = "2025-04-03T12:00:00Z"
    scenario_fields['/Document/FIToFICstmrCdtTrf/GrpHdr/NbOfTxs'] = "1"
    scenario_fields['/Document/FIToFICstmrCdtTrf/GrpHdr/SttlmInf/SttlmMtd'] = "CLRG"
    scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId/EndToEndId'] = f"E2E-{scenario_name.replace(' ', '-').upper()}-001"
    
    if scenario_name == "Domestic Payment":
        scenario_fields['/Document/FIToFICstmrCdtTrf/GrpHdr/InstgAgt/FinInstnId/BICFI'] = "BANKCA00XXX"
        scenario_fields['/Document/FIToFICstmrCdtTrf/GrpHdr/InstdAgt/FinInstnId/BICFI'] = "BANKCA01XXX"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtTpInf/SvcLvl/Cd'] = "NURG"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtTpInf/LclInstrm/Cd'] = "RTR"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/Nm'] = "John Smith"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/PstlAdr/StrtNm'] = "123 Maple Street"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/PstlAdr/TwnNm'] = "Toronto"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/PstlAdr/Ctry'] = "CA"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/CtryOfRes'] = "CA"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/DbtrAcct/Id/Othr/Id'] = "12345678"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI'] = "BANKCA00XXX"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/Nm'] = "Jane Doe"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/PstlAdr/StrtNm'] = "456 Oak Avenue"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/PstlAdr/TwnNm'] = "Vancouver"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/PstlAdr/Ctry'] = "CA"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/CtryOfRes'] = "CA"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/CdtrAcct/Id/Othr/Id'] = "87654321"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI'] = "BANKCA01XXX"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt'] = "5000.00"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/Ccy'] = "CAD"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Purp/Cd'] = "CASH"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/RmtInf/Ustrd'] = "Payment for services"
    
    elif scenario_name == "Cross-Border Payment":
        scenario_fields['/Document/FIToFICstmrCdtTrf/GrpHdr/InstgAgt/FinInstnId/BICFI'] = "BANKCA00XXX"
        scenario_fields['/Document/FIToFICstmrCdtTrf/GrpHdr/InstdAgt/FinInstnId/BICFI'] = "BANKUS00XXX"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtTpInf/SvcLvl/Cd'] = "NURG"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtTpInf/LclInstrm/Cd'] = "RTR"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/Nm'] = "John Smith"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/PstlAdr/StrtNm'] = "123 Maple Street"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/PstlAdr/TwnNm'] = "Toronto"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/PstlAdr/Ctry'] = "CA"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/CtryOfRes'] = "CA"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/DbtrAcct/Id/Othr/Id'] = "12345678"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI'] = "BANKCA00XXX"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/Nm'] = "Bob Johnson"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/PstlAdr/StrtNm'] = "789 Pine Road"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/PstlAdr/TwnNm'] = "New York"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/PstlAdr/Ctry'] = "US"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/CtryOfRes'] = "US"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/CdtrAcct/Id/Othr/Id'] = "87654321"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI'] = "BANKUS00XXX"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt'] = "7500.00"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/Ccy'] = "USD"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/XchgRateInf/RateTp'] = "SPOT"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/XchgRateInf/XchgRate'] = "1.25"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/ChrgBr'] = "SHAR"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Purp/Cd'] = "INTC"
        scenario_fields['/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/RmtInf/Ustrd'] = "Invoice payment #12345"
    
    
    for path, value in examples.items():
        if path not in scenario_fields:
            scenario_fields[path] = value
    
    return scenario_fields

def enhance_xml_file(xml_file, fields, rules):
    """Enhance an XML file with optional fields."""
    print(f"Enhancing {os.path.basename(xml_file)}...")
    
    filename = os.path.basename(xml_file)
    scenario_name = filename.replace('_', ' ').replace('.xml', '').title()
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    if 'xmlns' not in root.attrib:
        root.set('xmlns', 'urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08')
    
    examples = load_json_file(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reference/field_examples.json"))
    scenario_fields = get_scenario_fields(scenario_name, examples)
    
    for path, value in scenario_fields.items():
        if path.startswith('/Document'):
            path_components = path.split('/')[2:]  # Skip /Document
        else:
            path_components = path.split('/')
            path_components = [c for c in path_components if c]
        
        is_currency = False
        if path_components[-1] == 'Ccy':
            is_currency = True
            path_components = path_components[:-1]
        
        current_element = root
        for i, component in enumerate(path_components):
            element = None
            for child in current_element:
                if child.tag == component:
                    element = child
                    break
            
            if element is None:
                element = ET.SubElement(current_element, component)
            current_element = element
        
        if is_currency:
            current_element.set('Ccy', value)
        else:
            current_element.text = value
    
    rough_string = ET.tostring(root, 'utf-8')
    
    try:
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
    except Exception as e:
        print(f"  Error formatting XML: {e}")
        decoded = rough_string.decode('utf-8')
        pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + decoded
    
    lines = pretty_xml.splitlines()
    cleaned_lines = []
    for line in lines:
        if line.strip():  # Keep non-empty lines
            cleaned_lines.append(line)
    
    cleaned_xml = "\n".join(cleaned_lines)
    
    with open(xml_file, 'w') as f:
        f.write(cleaned_xml)
    
    print(f"  Enhanced {os.path.basename(xml_file)} with optional fields")
    return True

def main():
    fields_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reference/all_fields.json")
    rules_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reference/all_rules.json")
    
    fields = load_json_file(fields_file)
    rules = load_json_file(rules_file)
    
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    enhanced_files = 0
    for sample_file in sample_files:
        if enhance_xml_file(sample_file, fields, rules):
            enhanced_files += 1
    
    print(f"Enhanced {enhanced_files} of {len(sample_files)} sample files with optional fields")

if __name__ == "__main__":
    main()
