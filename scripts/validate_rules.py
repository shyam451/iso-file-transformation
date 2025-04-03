"""
Validate sample XML messages against the rules defined in the ISO 20022 Excel file.
"""
import os
import sys
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import re
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def extract_rules(excel_file):
    """
    Extract rules from the Rules sheet of an ISO 20022 Excel file.
    
    Args:
        excel_file (str): Path to the ISO 20022 Excel file
        
    Returns:
        list: List of dictionaries containing rule information
    """
    print(f"Extracting rules from {os.path.basename(excel_file)}...")
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Rules')
        
        df = df.dropna(how='all')
        
        header_row = None
        for i, row in df.iterrows():
            if str(row.iloc[0]).lower() == 'index':
                header_row = i
                break
        
        if header_row is None:
            for i, row in df.iterrows():
                if any('index' in str(val).lower() for val in row if pd.notna(val)):
                    header_row = i
                    break
        
        if header_row is None:
            print("Could not find header row in Rules sheet")
            return []
        
        rules_df = df.iloc[header_row+1:].copy()
        
        rules_df.columns = ['Index', 'Name', 'Definition'] + list(rules_df.columns[3:])
        
        rules = []
        
        for _, row in rules_df.iterrows():
            if pd.notna(row['Index']) and pd.notna(row['Name']):
                rule = {
                    'index': str(row['Index']),
                    'name': str(row['Name']),
                    'definition': str(row['Definition']) if pd.notna(row['Definition']) else ""
                }
                rules.append(rule)
        
        print(f"Found {len(rules)} rules")
        return rules
    
    except Exception as e:
        print(f"Error extracting rules from Excel: {e}")
        return []

def parse_rule_definition(rule_definition):
    """
    Parse a rule definition to extract conditions and requirements.
    
    Args:
        rule_definition (str): Rule definition text
        
    Returns:
        dict: Dictionary containing parsed rule information
    """
    parsed_rule = {
        'elements': [],
        'conditions': [],
        'requirements': []
    }
    
    elements = re.findall(r'<([^>]+)>', rule_definition)
    parsed_rule['elements'] = list(set(elements))
    
    conditions = re.findall(r'(?:If|When)\s+([^,\.]+)', rule_definition)
    parsed_rule['conditions'] = conditions
    
    requirements = re.findall(r'(?:must|shall|should)\s+([^,\.]+)', rule_definition)
    parsed_rule['requirements'] = requirements
    
    return parsed_rule

def validate_xml_against_rules(xml_file, rules):
    """
    Validate an XML file against the extracted rules.
    
    Args:
        xml_file (str): Path to the XML file
        rules (list): List of dictionaries containing rule information
        
    Returns:
        dict: Dictionary containing validation results
    """
    print(f"Validating {os.path.basename(xml_file)}...")
    
    validation_results = {
        'file': os.path.basename(xml_file),
        'passed_rules': [],
        'failed_rules': [],
        'not_applicable_rules': []
    }
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
        
        all_elements = []
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            all_elements.append(tag)
        
        all_text = []
        for elem in root.iter():
            if elem.text and elem.text.strip():
                all_text.append(elem.text.strip())
        
        for rule in rules:
            rule_id = rule['index']
            rule_name = rule['name']
            rule_definition = rule['definition']
            
            parsed_rule = parse_rule_definition(rule_definition)
            
            rule_applicable = True
            for element in parsed_rule['elements']:
                if element not in all_elements:
                    rule_applicable = False
                    break
            
            if not rule_applicable:
                validation_results['not_applicable_rules'].append({
                    'rule_id': rule_id,
                    'rule_name': rule_name,
                    'reason': f"Elements mentioned in rule not found in XML"
                })
                continue
            
            rule_passed = True
            failure_reason = ""
            
            if 'currency' in rule_definition.lower() or 'ccy' in rule_definition.lower():
                if 'CAD' in rule_definition and 'CAD' not in str(all_text):
                    rule_passed = False
                    failure_reason = "CAD currency not found in XML"
                elif 'EUR' in rule_definition and 'EUR' not in str(all_text):
                    rule_passed = False
                    failure_reason = "EUR currency not found in XML"
                elif 'USD' in rule_definition and 'USD' not in str(all_text):
                    rule_passed = False
                    failure_reason = "USD currency not found in XML"
            
            if 'amount' in rule_definition.lower() or 'amt' in rule_definition.lower():
                amount_elements = [elem for elem in root.iter() if 
                                  (elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag).endswith('Amt')]
                if not amount_elements:
                    rule_passed = False
                    failure_reason = "Amount elements not found in XML"
            
            if 'settlement' in rule_definition.lower() or 'sttlm' in rule_definition.lower():
                settlement_elements = [elem for elem in root.iter() if 
                                      (elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag).startswith('Sttlm')]
                if not settlement_elements:
                    rule_passed = False
                    failure_reason = "Settlement elements not found in XML"
            
            if rule_passed:
                validation_results['passed_rules'].append({
                    'rule_id': rule_id,
                    'rule_name': rule_name
                })
            else:
                validation_results['failed_rules'].append({
                    'rule_id': rule_id,
                    'rule_name': rule_name,
                    'reason': failure_reason
                })
        
        print(f"  Passed: {len(validation_results['passed_rules'])}, "
              f"Failed: {len(validation_results['failed_rules'])}, "
              f"Not Applicable: {len(validation_results['not_applicable_rules'])}")
        
        return validation_results
    
    except Exception as e:
        print(f"Error validating XML against rules: {e}")
        validation_results['failed_rules'].append({
            'rule_id': 'PARSE_ERROR',
            'rule_name': 'XML Parsing Error',
            'reason': str(e)
        })
        return validation_results

def generate_validation_report(validation_results):
    """
    Generate a validation report from the validation results.
    
    Args:
        validation_results (list): List of dictionaries containing validation results
        
    Returns:
        str: Validation report as a string
    """
    report = "# ISO 20022 XML Validation Report\n\n"
    
    total_files = len(validation_results)
    total_passed = sum(len(result['passed_rules']) for result in validation_results)
    total_failed = sum(len(result['failed_rules']) for result in validation_results)
    total_not_applicable = sum(len(result['not_applicable_rules']) for result in validation_results)
    
    report += f"## Summary\n\n"
    report += f"- Total Files Validated: {total_files}\n"
    report += f"- Total Rules Passed: {total_passed}\n"
    report += f"- Total Rules Failed: {total_failed}\n"
    report += f"- Total Rules Not Applicable: {total_not_applicable}\n\n"
    
    report += f"## Detailed Results\n\n"
    
    for result in validation_results:
        file_name = result['file']
        passed_rules = result['passed_rules']
        failed_rules = result['failed_rules']
        not_applicable_rules = result['not_applicable_rules']
        
        report += f"### {file_name}\n\n"
        
        if passed_rules:
            report += f"#### Passed Rules ({len(passed_rules)})\n\n"
            for rule in passed_rules:
                report += f"- {rule['rule_id']}: {rule['rule_name']}\n"
            report += "\n"
        
        if failed_rules:
            report += f"#### Failed Rules ({len(failed_rules)})\n\n"
            for rule in failed_rules:
                report += f"- {rule['rule_id']}: {rule['rule_name']} - {rule['reason']}\n"
            report += "\n"
        
        if not_applicable_rules:
            report += f"#### Not Applicable Rules ({len(not_applicable_rules)})\n\n"
            for rule in not_applicable_rules:
                report += f"- {rule['rule_id']}: {rule['rule_name']} - {rule['reason']}\n"
            report += "\n"
    
    return report

def main():
    excel_file = os.path.expanduser("~/attachments/a3d8f110-7f59-403b-9340-98c29a674930/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")
    
    rules = extract_rules(excel_file)
    
    if not rules:
        print("No rules found in the Excel file")
        return
    
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    validation_results = []
    for sample_file in sample_files:
        result = validate_xml_against_rules(sample_file, rules)
        validation_results.append(result)
    
    report = generate_validation_report(validation_results)
    
    report_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "validation_report.md")
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Validation report saved to {report_file}")

if __name__ == "__main__":
    main()
