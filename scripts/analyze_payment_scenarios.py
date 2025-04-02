"""
Analyze ISO 20022 Excel file to identify all possible payment scenarios.
"""
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_payment_scenarios():
    excel_file = os.path.expanduser("~/attachments/a3d8f110-7f59-403b-9340-98c29a674930/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")
    
    print("Analyzing ISO 20022 Excel file for payment scenarios...")
    
    print("\n=== Analyzing Rules Sheet ===")
    try:
        rules_df = pd.read_excel(excel_file, sheet_name='Rules')
        
        header_row = rules_df[rules_df.iloc[:, 0] == 'Index'].index[0]
        
        rules_df = rules_df.iloc[header_row+1:].copy()
        
        rules_df.columns = ['Index', 'Name', 'Definition'] + list(rules_df.columns[3:])
        
        print("\nRules that might indicate payment scenarios:")
        for _, row in rules_df.iterrows():
            if pd.notna(row['Index']) and pd.notna(row['Definition']):
                print(f"- Rule {row['Index']}: {row['Name']}")
                print(f"  Definition: {row['Definition']}")
                print()
    except Exception as e:
        print(f"Error analyzing Rules sheet: {e}")
    
    print("\n=== Analyzing Full_View Sheet for Payment Type Indicators ===")
    try:
        full_view_df = pd.read_excel(excel_file, sheet_name='Full_View')
        
        full_view_df = full_view_df.dropna(how='all')
        
        full_view_df.columns = [str(col).strip() for col in full_view_df.columns]
        
        payment_type_indicators = full_view_df[
            (full_view_df['Name'].str.contains('Type', na=False)) | 
            (full_view_df['Name'].str.contains('Category', na=False)) |
            (full_view_df['Name'].str.contains('Priority', na=False)) |
            (full_view_df['XML Tag'].str.contains('Tp', na=False)) |
            (full_view_df['XML Tag'].str.contains('Ctgy', na=False)) |
            (full_view_df['XML Tag'].str.contains('Prtry', na=False))
        ]
        
        print("\nPayment type indicators found:")
        for _, row in payment_type_indicators.iterrows():
            print(f"- {row['Name']} ({row['XML Tag']})")
            if pd.notna(row['Type / Code']):
                print(f"  Type/Code: {row['Type / Code']}")
            if pd.notna(row['Definition']):
                print(f"  Definition: {row['Definition']}")
            print()
        
        currency_fields = full_view_df[
            (full_view_df['Name'].str.contains('Currency', na=False)) | 
            (full_view_df['XML Tag'].str.contains('Ccy', na=False))
        ]
        
        print("\nCurrency-related fields:")
        for _, row in currency_fields.iterrows():
            print(f"- {row['Name']} ({row['XML Tag']})")
            if pd.notna(row['Path']):
                print(f"  Path: {row['Path']}")
            print()
        
        settlement_fields = full_view_df[
            (full_view_df['Name'].str.contains('Settlement', na=False)) | 
            (full_view_df['XML Tag'].str.contains('Sttlm', na=False))
        ]
        
        print("\nSettlement-related fields:")
        for _, row in settlement_fields.iterrows():
            print(f"- {row['Name']} ({row['XML Tag']})")
            if pd.notna(row['Path']):
                print(f"  Path: {row['Path']}")
            print()
    except Exception as e:
        print(f"Error analyzing Full_View sheet: {e}")
    
    print("\n=== Potential Payment Scenarios ===")
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
                '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtTpInf/SvcLvl/Prtry': 'RETURN'
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
    
    for i, scenario in enumerate(scenarios):
        print(f"{i+1}. {scenario['name']}: {scenario['description']}")
        print("   Key fields:")
        for path, value in scenario['key_fields'].items():
            print(f"   - {path}: {value}")
        print()

if __name__ == "__main__":
    analyze_payment_scenarios()
