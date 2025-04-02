"""
Regenerate sample messages using the fixed XML generator.
"""
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso_message_generator.message_structure import extract_message_structure
from iso_message_generator.rule_processor import extract_rules, identify_payment_scenarios
from iso_message_generator.fixed_xml_generator import create_sample_xml

def main():
    excel_file = os.path.expanduser("~/attachments/a3d8f110-7f59-403b-9340-98c29a674930/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    message_structure = extract_message_structure(excel_file)
    print(f"Extracted {len(message_structure)} message elements")
    
    rules = extract_rules(excel_file)
    print(f"Extracted {len(rules)} rules")
    
    scenarios = identify_payment_scenarios(message_structure, rules)
    print(f"Identified {len(scenarios)} payment scenarios")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for scenario in scenarios:
        print(f"Creating sample message for {scenario['name']}...")
        xml_content = create_sample_xml(scenario, message_structure, output_dir)
    
    scenarios_json = []
    for scenario in scenarios:
        scenario_info = {
            'name': scenario['name'],
            'description': scenario['description'],
            'file_name': f"{scenario['name'].replace(' ', '_').lower()}.xml"
        }
        scenarios_json.append(scenario_info)
    
    scenarios_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "payment_scenarios.json")
    with open(scenarios_file, 'w') as f:
        json.dump(scenarios_json, f, indent=2)
    
    print(f"Saved scenarios information to {scenarios_file}")

if __name__ == "__main__":
    main()
