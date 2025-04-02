import pandas as pd
import os
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Path to the Excel file
excel_file = os.path.expanduser("~/attachments/a3d8f110-7f59-403b-9340-98c29a674930/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")

def extract_message_structure():
    """Extract the message structure from the Full_View sheet"""
    print("Extracting message structure...")
    
    # Read the Full_View sheet
    df = pd.read_excel(excel_file, sheet_name='Full_View')
    
    # Clean up the dataframe
    df = df.dropna(how='all')
    
    # Rename columns for easier access
    df.columns = [str(col).strip() for col in df.columns]
    
    # Extract relevant columns
    structure_df = df[['Lvl', 'Name', 'XML Tag', 'Mult', 'Type / Code', 'Path', 'Definition']]
    
    # Create a dictionary to store the message structure
    message_structure = {}
    
    # Iterate through rows to build the structure
    for _, row in structure_df.iterrows():
        if pd.notna(row['Path']) and pd.notna(row['XML Tag']):
            path = row['Path']
            xml_tag = row['XML Tag']
            name = row['Name']
            mult = row['Mult'] if pd.notna(row['Mult']) else ""
            data_type = row['Type / Code'] if pd.notna(row['Type / Code']) else ""
            definition = row['Definition'] if pd.notna(row['Definition']) else ""
            
            message_structure[path] = {
                'name': name,
                'xml_tag': xml_tag,
                'multiplicity': mult,
                'data_type': data_type,
                'definition': definition
            }
    
    return message_structure

def extract_rules():
    """Extract rules from the Rules sheet"""
    print("Extracting rules...")
    
    # Read the Rules sheet
    df = pd.read_excel(excel_file, sheet_name='Rules')
    
    # Clean up the dataframe
    df = df.dropna(how='all')
    
    # Find the row with column headers
    header_row = df[df.iloc[:, 0] == 'Index'].index[0]
    
    # Extract data after the header row
    rules_df = df.iloc[header_row+1:].copy()
    
    # Rename columns
    rules_df.columns = ['Index', 'Name', 'Definition'] + list(rules_df.columns[3:])
    
    # Create a list to store the rules
    rules = []
    
    # Iterate through rows to extract rules
    for _, row in rules_df.iterrows():
        if pd.notna(row['Index']) and pd.notna(row['Name']):
            rule = {
                'index': row['Index'],
                'name': row['Name'],
                'definition': row['Definition'] if pd.notna(row['Definition']) else ""
            }
            rules.append(rule)
    
    return rules

def identify_payment_scenarios(message_structure, rules):
    """Identify payment scenarios based on the message structure and rules"""
    print("Identifying payment scenarios...")
    
    # Basic payment scenarios
    scenarios = [
        {
            'name': 'Domestic Payment',
            'description': 'A payment between two financial institutions within the same country',
            'key_fields': {
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId/EndToEndId': 'E2E-DOM-001',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/Ccy': 'CAD',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/CtryOfRes': 'CA',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/CtryOfRes': 'CA'
            }
        },
        {
            'name': 'Cross-Border Payment',
            'description': 'A payment between two financial institutions in different countries',
            'key_fields': {
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId/EndToEndId': 'E2E-XBORDER-001',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/Ccy': 'USD',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/CtryOfRes': 'CA',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/CtryOfRes': 'US'
            }
        },
        {
            'name': 'High-Value Payment',
            'description': 'A high-value payment between financial institutions',
            'key_fields': {
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId/EndToEndId': 'E2E-HIGHVAL-001',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt': '1000000.00',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/Ccy': 'CAD'
            }
        },
        {
            'name': 'Urgent Payment',
            'description': 'An urgent payment with high priority',
            'key_fields': {
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId/EndToEndId': 'E2E-URGENT-001',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/SttlmPrty': 'HIGH'
            }
        }
    ]
    
    # Add rule-based scenarios
    for rule in rules:
        if 'CAD' in rule['definition'] and 'Interbank' in rule['definition']:
            # Add CAD Interbank Settlement scenario
            scenarios.append({
                'name': 'CAD Interbank Settlement',
                'description': 'Payment with CAD as the interbank settlement currency',
                'key_fields': {
                    '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId/EndToEndId': 'E2E-CAD-INTRBNK-001',
                    '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/Ccy': 'CAD',
                    '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/InstdAmt/Ccy': 'CAD'
                },
                'rule_reference': rule['index']
            })
    
    return scenarios

def create_sample_xml(scenario, message_structure):
    """Create a sample XML message for a payment scenario"""
    # Create the root element
    root = ET.Element("Document")
    root.set("xmlns", "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08")
    
    # Create the FIToFICstmrCdtTrf element
    fi_to_fi = ET.SubElement(root, "FIToFICstmrCdtTrf")
    
    # Create the GrpHdr element
    grp_hdr = ET.SubElement(fi_to_fi, "GrpHdr")
    
    # Add common GrpHdr elements
    ET.SubElement(grp_hdr, "MsgId").text = f"MSG-{scenario['name'].replace(' ', '-')}-001"
    ET.SubElement(grp_hdr, "CreDtTm").text = "2025-04-02T15:10:00Z"
    ET.SubElement(grp_hdr, "NbOfTxs").text = "1"
    ET.SubElement(grp_hdr, "SttlmInf").text = "CLRG"
    
    # Create the CdtTrfTxInf element
    cdt_trf_tx_inf = ET.SubElement(fi_to_fi, "CdtTrfTxInf")
    
    # Add scenario-specific fields
    for path, value in scenario['key_fields'].items():
        # Extract the element names from the path
        elements = path.split('/')
        elements = [e for e in elements if e]  # Remove empty strings
        
        # Skip the Document and FIToFICstmrCdtTrf elements as they're already created
        elements = elements[2:]
        
        # Start from the CdtTrfTxInf element
        current_element = cdt_trf_tx_inf
        
        # Create nested elements
        for i, element_name in enumerate(elements[:-1]):
            # Check if the element already exists
            existing = current_element.find(element_name)
            if existing is not None:
                current_element = existing
            else:
                new_element = ET.SubElement(current_element, element_name)
                current_element = new_element
        
        # Add the leaf element with the value
        leaf_name = elements[-1]
        
        # Handle currency attributes
        if leaf_name == 'Ccy':
            # The parent element should have a Ccy attribute
            parent = current_element
            parent.set('Ccy', value)
        else:
            ET.SubElement(current_element, leaf_name).text = value
    
    # Convert to pretty XML string
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    return pretty_xml

def main():
    # Extract message structure
    message_structure = extract_message_structure()
    print(f"Extracted {len(message_structure)} message elements")
    
    # Extract rules
    rules = extract_rules()
    print(f"Extracted {len(rules)} rules")
    
    # Identify payment scenarios
    scenarios = identify_payment_scenarios(message_structure, rules)
    print(f"Identified {len(scenarios)} payment scenarios")
    
    # Create output directory
    output_dir = os.path.expanduser("~/repos/iso-file-transformation/sample_messages")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create sample XML messages for each scenario
    for scenario in scenarios:
        print(f"Creating sample message for {scenario['name']}...")
        xml_content = create_sample_xml(scenario, message_structure)
        
        # Save to file
        filename = f"{scenario['name'].replace(' ', '_').lower()}.xml"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(xml_content)
        
        print(f"Saved sample message to {file_path}")
    
    # Create a JSON file with scenario descriptions
    scenarios_json = []
    for scenario in scenarios:
        scenario_info = {
            'name': scenario['name'],
            'description': scenario['description'],
            'file_name': f"{scenario['name'].replace(' ', '_').lower()}.xml"
        }
        scenarios_json.append(scenario_info)
    
    # Save scenarios to JSON file
    scenarios_file = os.path.join(os.path.expanduser("~/repos/iso-file-transformation"), "payment_scenarios.json")
    with open(scenarios_file, 'w') as f:
        json.dump(scenarios_json, f, indent=2)
    
    print(f"Saved scenarios information to {scenarios_file}")

if __name__ == "__main__":
    main()
