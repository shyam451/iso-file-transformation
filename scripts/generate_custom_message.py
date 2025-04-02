"""
Generate custom ISO 20022 pacs.008 messages for specific payment scenarios.

Usage:
    python generate_custom_message.py --scenario <scenario_name> [--output <output_file>]
    
Example:
    python generate_custom_message.py --scenario "Domestic Payment" --output custom_domestic.xml
"""
import argparse
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso_message_generator import extract_message_structure, extract_rules, create_sample_xml
from iso_message_generator.rule_processor import identify_payment_scenarios

def main():
    parser = argparse.ArgumentParser(description='Generate custom ISO 20022 pacs.008 messages for specific payment scenarios.')
    parser.add_argument('--scenario', type=str, required=True, help='Name of the payment scenario')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--excel', type=str, help='Path to ISO Excel file')
    
    args = parser.parse_args()
    
    excel_file = args.excel or os.path.expanduser("~/attachments/a3d8f110-7f59-403b-9340-98c29a674930/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")
    
    message_structure = extract_message_structure(excel_file)
    rules = extract_rules(excel_file)
    
    scenarios = identify_payment_scenarios(message_structure, rules)
    
    scenario = None
    for s in scenarios:
        if s['name'].lower() == args.scenario.lower():
            scenario = s
            break
    
    if not scenario:
        print(f"Error: Scenario '{args.scenario}' not found")
        print("Available scenarios:")
        for s in scenarios:
            print(f"- {s['name']}")
        sys.exit(1)
    
    output_dir = os.path.dirname(args.output) if args.output else None
    xml = create_sample_xml(scenario, message_structure, output_dir)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(xml)
        print(f"XML message written to {args.output}")
    else:
        print(xml)

if __name__ == "__main__":
    main()
