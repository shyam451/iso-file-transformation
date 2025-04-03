"""
Prettify XML files to improve readability with consistent indentation.
"""
import os
import sys
import glob
import xml.dom.minidom as minidom
from xml.etree import ElementTree as ET

def prettify_xml(xml_file):
    """
    Prettify an XML file with consistent indentation.
    
    Args:
        xml_file (str): Path to the XML file
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Prettifying {os.path.basename(xml_file)}...")
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        xml_str = ET.tostring(root, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        
        pretty_xml = dom.toprettyxml(indent='  ')
        
        lines = pretty_xml.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        pretty_xml = '\n'.join(non_empty_lines)
        
        if not pretty_xml.startswith('<?xml'):
            pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"  Successfully prettified {os.path.basename(xml_file)}")
        return True
    
    except Exception as e:
        print(f"  Error prettifying {os.path.basename(xml_file)}: {e}")
        return False

def main():
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    prettified_files = 0
    for sample_file in sample_files:
        if prettify_xml(sample_file):
            prettified_files += 1
    
    print(f"Prettified {prettified_files} of {len(sample_files)} sample files")

if __name__ == "__main__":
    main()
