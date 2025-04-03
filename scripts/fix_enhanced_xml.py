"""
Fix formatting issues in enhanced XML files.
"""
import os
import sys
import glob
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def clean_xml_content(content):
    """Clean XML content by removing HTML entities and fixing formatting."""
    if content.count('<?xml') > 1:
        content = re.sub(r'<\?xml.*?\?>\s*', '', content, count=1)
    
    content = content.replace('&lt;', '<').replace('&gt;', '>')
    
    content = re.sub(r'Sample <[^>]+>', '', content)
    
    content = re.sub(r'<@Ccy>([^<]+)</@Ccy>', r' Ccy="\1"', content)
    
    content = re.sub(r'(\d+\.\d+)\s+Ccy="([^"]+)"', r'\1" Ccy="\2', content)
    
    return content

def fix_xml_file(xml_file):
    """Fix XML formatting in a file."""
    print(f"Fixing {os.path.basename(xml_file)}...")
    
    try:
        with open(xml_file, 'r') as f:
            content = f.read()
        
        cleaned_content = clean_xml_content(content)
        
        try:
            root = ET.fromstring(cleaned_content)
            rough_string = ET.tostring(root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            lines = pretty_xml.splitlines()
            cleaned_lines = []
            for line in lines:
                if line.strip():  # Keep non-empty lines
                    cleaned_lines.append(line)
            
            pretty_xml = "\n".join(cleaned_lines)
        except Exception as e:
            print(f"  Error parsing XML after cleaning: {e}")
            pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + cleaned_content
        
        with open(xml_file, 'w') as f:
            f.write(pretty_xml)
        
        print(f"  Fixed {os.path.basename(xml_file)}")
        return True
    except Exception as e:
        print(f"  Error fixing {os.path.basename(xml_file)}: {e}")
        return False

def main():
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    fixed_files = 0
    for sample_file in sample_files:
        if fix_xml_file(sample_file):
            fixed_files += 1
    
    print(f"Fixed {fixed_files} of {len(sample_files)} sample files")

if __name__ == "__main__":
    main()
