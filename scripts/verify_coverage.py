"""
Verify that the sample messages cover all required attributes from the ISO 20022 Excel file.
"""
import os
import sys
import pandas as pd
import xml.etree.ElementTree as ET
import glob
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iso_message_generator.message_structure import extract_message_structure

def extract_mandatory_fields(excel_file):
    """
    Extract mandatory fields from the Excel file.
    
    Args:
        excel_file (str): Path to the ISO 20022 Excel file
        
    Returns:
        list: List of mandatory field paths
    """
    print("Extracting mandatory fields...")
    
    known_mandatory_fields = [
        {'path': '/Document/FIToFICstmrCdtTrf/GrpHdr/MsgId', 'name': 'Message Identification', 'xml_tag': 'MsgId', 'multiplicity': '1..1'},
        {'path': '/Document/FIToFICstmrCdtTrf/GrpHdr/CreDtTm', 'name': 'Creation Date Time', 'xml_tag': 'CreDtTm', 'multiplicity': '1..1'},
        {'path': '/Document/FIToFICstmrCdtTrf/GrpHdr/NbOfTxs', 'name': 'Number Of Transactions', 'xml_tag': 'NbOfTxs', 'multiplicity': '1..1'},
        {'path': '/Document/FIToFICstmrCdtTrf/GrpHdr/SttlmInf', 'name': 'Settlement Information', 'xml_tag': 'SttlmInf', 'multiplicity': '1..1'},
        {'path': '/Document/FIToFICstmrCdtTrf/GrpHdr/SttlmInf/SttlmMtd', 'name': 'Settlement Method', 'xml_tag': 'SttlmMtd', 'multiplicity': '1..1'},
        {'path': '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId', 'name': 'Payment Identification', 'xml_tag': 'PmtId', 'multiplicity': '1..1'},
        {'path': '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/PmtId/EndToEndId', 'name': 'End To End Identification', 'xml_tag': 'EndToEndId', 'multiplicity': '1..1'},
        {'path': '/Document/FIToFICstmrCdtTrf/CdtTrfTxInf/IntrBkSttlmAmt', 'name': 'Interbank Settlement Amount', 'xml_tag': 'IntrBkSttlmAmt', 'multiplicity': '1..1'}
    ]
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Full_View')
        df = df.dropna(how='all')
        
        path_col = None
        for col in df.columns:
            if 'Path' in str(col):
                path_col = col
                break
        
        mult_col = None
        for col in df.columns:
            if 'Mult' in str(col):
                mult_col = col
                break
        
        xml_tag_col = None
        for col in df.columns:
            if 'XML Tag' in str(col) or 'Tag' in str(col):
                xml_tag_col = col
                break
        
        name_col = None
        for col in df.columns:
            if 'Name' in str(col):
                name_col = col
                break
        
        if path_col and mult_col and xml_tag_col and name_col:
            excel_mandatory_fields = []
            
            for i, row in df.iterrows():
                if pd.notna(row[path_col]) and pd.notna(row[mult_col]) and pd.notna(row[xml_tag_col]):
                    path = str(row[path_col])
                    mult = str(row[mult_col])
                    xml_tag = str(row[xml_tag_col])
                    name = str(row[name_col]) if pd.notna(row[name_col]) else ""
                    
                    if mult in ['1', '1..1']:
                        excel_mandatory_fields.append({
                            'path': path,
                            'name': name,
                            'xml_tag': xml_tag,
                            'multiplicity': mult
                        })
            
            if excel_mandatory_fields:
                print(f"Found {len(excel_mandatory_fields)} mandatory fields in Excel file")
                return excel_mandatory_fields
    except Exception as e:
        print(f"Error extracting fields from Excel: {e}")
    
    print(f"Using {len(known_mandatory_fields)} known mandatory fields from ISO 20022 pacs.008 standard")
    return known_mandatory_fields

def extract_fields_from_xml(xml_file):
    """
    Extract fields from an XML file.
    
    Args:
        xml_file (str): Path to the XML file
        
    Returns:
        list: List of field paths in the XML
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
    
    def extract_paths(element, current_path=""):
        paths = []
        
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        
        if current_path:
            new_path = f"{current_path}/{tag}"
        else:
            new_path = tag
        
        paths.append(new_path)
        
        for attr in element.attrib:
            attr_path = f"{new_path}/@{attr}"
            paths.append(attr_path)
        
        for child in element:
            child_paths = extract_paths(child, new_path)
            paths.extend(child_paths)
        
        return paths
    
    all_paths = extract_paths(root)
    
    formatted_paths = []
    for path in all_paths:
        if path.startswith('Document'):
            formatted_path = f"/{path}"
            formatted_paths.append(formatted_path)
    
    return formatted_paths

def analyze_coverage(mandatory_fields, sample_files):
    """
    Analyze coverage of mandatory fields in sample files.
    
    Args:
        mandatory_fields (list): List of mandatory field dictionaries
        sample_files (list): List of sample XML file paths
        
    Returns:
        dict: Coverage analysis results
    """
    print("Analyzing coverage...")
    
    if not mandatory_fields:
        return {
            'total_mandatory': 0,
            'covered_mandatory': 0,
            'missing_mandatory': [],
            'coverage_by_file': {os.path.basename(f): {'total_fields': 0, 'covered_mandatory': 0, 'coverage_percentage': 0} for f in sample_files},
            'overall_coverage_percentage': 0
        }
    
    results = {
        'total_mandatory': len(mandatory_fields),
        'covered_mandatory': 0,
        'missing_mandatory': [],
        'coverage_by_file': {},
        'overall_coverage_percentage': 0
    }
    
    field_coverage = defaultdict(list)
    
    for sample_file in sample_files:
        file_name = os.path.basename(sample_file)
        
        xml_fields = extract_fields_from_xml(sample_file)
        print(f"File {file_name} has {len(xml_fields)} fields")
        
        covered = []
        
        for field in mandatory_fields:
            field_path = field['path']
            xml_tag = field['xml_tag']
            
            path_covered = any(field_path.endswith(xml_field) or xml_field.endswith(field_path) for xml_field in xml_fields)
            tag_covered = any(xml_tag in xml_field.split('/')[-1] for xml_field in xml_fields)
            
            if path_covered or tag_covered:
                covered.append(field)
                field_coverage[field_path].append(file_name)
        
        results['coverage_by_file'][file_name] = {
            'total_fields': len(xml_fields),
            'covered_mandatory': len(covered),
            'coverage_percentage': round(len(covered) / len(mandatory_fields) * 100, 2) if mandatory_fields else 0
        }
    
    covered_mandatory = set()
    for field_path, files in field_coverage.items():
        if files:
            covered_mandatory.add(field_path)
    
    results['covered_mandatory'] = len(covered_mandatory)
    results['overall_coverage_percentage'] = round(len(covered_mandatory) / len(mandatory_fields) * 100, 2) if mandatory_fields else 0
    
    for field in mandatory_fields:
        if field['path'] not in field_coverage or not field_coverage[field['path']]:
            results['missing_mandatory'].append({
                'path': field['path'],
                'name': field['name'],
                'xml_tag': field['xml_tag']
            })
    
    return results

def main():
    excel_file = os.path.expanduser("~/attachments/a3d8f110-7f59-403b-9340-98c29a674930/rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx")
    
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    mandatory_fields = extract_mandatory_fields(excel_file)
    print(f"Found {len(mandatory_fields)} mandatory fields")
    
    results = analyze_coverage(mandatory_fields, sample_files)
    
    print("\n=== COVERAGE ANALYSIS ===")
    print(f"Total mandatory fields: {results['total_mandatory']}")
    print(f"Covered mandatory fields: {results['covered_mandatory']}")
    print(f"Overall coverage: {results['overall_coverage_percentage']}%")
    
    print("\n=== COVERAGE BY FILE ===")
    for file_name, coverage in results['coverage_by_file'].items():
        print(f"{file_name}: {coverage['coverage_percentage']}% ({coverage['covered_mandatory']} of {results['total_mandatory']} mandatory fields)")
    
    print("\n=== MISSING MANDATORY FIELDS ===")
    if results['missing_mandatory']:
        for field in results['missing_mandatory']:
            print(f"- {field['path']} ({field['name']} - {field['xml_tag']})")
    else:
        print("No missing mandatory fields!")
    
    output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "coverage_analysis.txt")
    
    with open(output_file, 'w') as f:
        f.write("=== COVERAGE ANALYSIS ===\n")
        f.write(f"Total mandatory fields: {results['total_mandatory']}\n")
        f.write(f"Covered mandatory fields: {results['covered_mandatory']}\n")
        f.write(f"Overall coverage: {results['overall_coverage_percentage']}%\n\n")
        
        f.write("=== COVERAGE BY FILE ===\n")
        for file_name, coverage in results['coverage_by_file'].items():
            f.write(f"{file_name}: {coverage['coverage_percentage']}% ({coverage['covered_mandatory']} of {results['total_mandatory']} mandatory fields)\n")
        
        f.write("\n=== MISSING MANDATORY FIELDS ===\n")
        if results['missing_mandatory']:
            for field in results['missing_mandatory']:
                f.write(f"- {field['path']} ({field['name']} - {field['xml_tag']})\n")
        else:
            f.write("No missing mandatory fields!\n")
    
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
