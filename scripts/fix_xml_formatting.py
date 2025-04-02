"""
Fix XML formatting in sample messages to remove extra spaces and ensure consistent formatting.
"""
import os
import sys
import glob
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def fix_xml_formatting(xml_file):
    """
    Fix XML formatting in a file.
    
    Args:
        xml_file (str): Path to the XML file
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Fixing formatting in {os.path.basename(xml_file)}...")
    
    with open(xml_file, 'r') as f:
        content = f.read()
    
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        print(f"  Error parsing XML: {e}")
        return False
    
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]  # Remove namespace prefix
    
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    lines = pretty_xml.splitlines()
    cleaned_lines = []
    for line in lines:
        if line.strip():  # Keep non-empty lines
            cleaned_lines.append(line)
    
    cleaned_xml = "\n".join(cleaned_lines)
    
    if not cleaned_xml.startswith('<?xml'):
        cleaned_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + cleaned_xml
    
    with open(xml_file, 'w') as f:
        f.write(cleaned_xml)
    
    print(f"  Fixed formatting in {os.path.basename(xml_file)}")
    return True

def main():
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    fixed_files = 0
    for sample_file in sample_files:
        if fix_xml_formatting(sample_file):
            fixed_files += 1
    
    print(f"Fixed formatting in {fixed_files} of {len(sample_files)} sample files")

if __name__ == "__main__":
    main()
