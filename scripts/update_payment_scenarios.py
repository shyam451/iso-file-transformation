"""
Update payment scenarios and generate additional sample messages.
"""
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso_message_generator.message_structure import extract_message_structure
from iso_message_generator.rule_processor import extract_rules
from iso_message_generator.fixed_xml_generator import create_sample_xml

def update_payment_scenarios():
    excel_file = os.path.expanduser("~/attachments/a3d8f110-7f59-403b-9340-98c29a674930/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    message_structure = extract_message_structure(excel_file)
    print(f"Extracted {len(message_structure)} message elements")
    
    rules = extract_rules(excel_file)
    print(f"Extracted {len(rules)} rules")
    
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
        },
        {
            'name': 'CAD Interbank Settlement',
            'description': 'Payment with CAD as the interbank settlement currency',
            'key_fields': {
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId/EndToEndId': 'E2E-CAD-INTRBNK-001',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/Ccy': 'CAD',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/InstdAmt/Ccy': 'CAD'
            }
        },
        {
            'name': 'Return Payment',
            'description': 'A payment that is being returned to the original sender',
            'key_fields': {
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId/EndToEndId': 'E2E-RETURN-001',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtTpInf/SvcLvl/Prtry': 'RETURN',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/RtrInf/Rsn/Cd': 'NARR',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/RtrInf/AddtlInf': 'Payment returned as requested'
            }
        },
        {
            'name': 'International Payment',
            'description': 'An international payment with currency conversion',
            'key_fields': {
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId/EndToEndId': 'E2E-INTL-001',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt/Ccy': 'EUR',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/InstdAmt/Ccy': 'USD',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Dbtr/CtryOfRes': 'CA',
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/Cdtr/CtryOfRes': 'FR'
            }
        }
    ]
    
    print(f"Defined {len(scenarios)} payment scenarios")
    
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
    update_payment_scenarios()
