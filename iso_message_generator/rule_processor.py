"""
Extract and process ISO 20022 validation rules from Excel files.
"""
import pandas as pd

def extract_rules(excel_file):
    """
    Extract rules from the Rules sheet of an ISO 20022 Excel file.
    
    Args:
        excel_file (str): Path to the ISO 20022 Excel file
        
    Returns:
        list: List of dictionaries containing rule information
    """
    print("Extracting rules...")
    
    df = pd.read_excel(excel_file, sheet_name='Rules')
    
    df = df.dropna(how='all')
    
    header_row = df[df.iloc[:, 0] == 'Index'].index[0]
    
    rules_df = df.iloc[header_row+1:].copy()
    
    rules_df.columns = ['Index', 'Name', 'Definition'] + list(rules_df.columns[3:])
    
    rules = []
    
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
    """
    Identify payment scenarios based on the message structure and rules.
    
    Args:
        message_structure (dict): Dictionary containing the message structure
        rules (list): List of dictionaries containing rule information
        
    Returns:
        list: List of dictionaries containing payment scenario information
    """
    print("Identifying payment scenarios...")
    
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
    
    for rule in rules:
        if 'CAD' in rule['definition'] and 'Interbank' in rule['definition']:
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
