"""
Remove extra spaces from XML files to ensure clean formatting.
"""
import os
import sys
import glob
import re
from lxml import etree

def remove_extra_spaces(xml_file):
    """
    Remove extra spaces from an XML file.
    
    Args:
        xml_file (str): Path to the XML file
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Removing extra spaces from {os.path.basename(xml_file)}...")
    
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xml_file, parser)
        
        xml_str = etree.tostring(tree, encoding='utf-8', xml_declaration=True, pretty_print=True)
        
        xml_str = xml_str.decode('utf-8')
        
        xml_str = re.sub(r'>\s+<', '><', xml_str)
        
        xml_str = re.sub(r'><', '>\n<', xml_str)
        
        lines = xml_str.split('\n')
        indent = 0
        result = []
        
        for line in lines:
            if not line.strip():
                continue
                
            if '</' in line and not line.strip().startswith('</'):
                pass
            elif '</' in line:
                indent -= 1
            
            if indent > 0 and not line.strip().startswith('<?xml'):
                result.append('  ' * indent + line.strip())
            else:
                result.append(line.strip())
            
            if '<' in line and not '</' in line and not '/>' in line:
                indent += 1
        
        xml_str = '\n'.join(result)
        
        comment_pattern = r'<!--(.*?)-->'
        comments = re.findall(comment_pattern, xml_str, re.DOTALL)
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        print(f"  Successfully removed extra spaces from {os.path.basename(xml_file)}")
        return True
    
    except Exception as e:
        print(f"  Error removing extra spaces from {os.path.basename(xml_file)}: {e}")
        return False

def main():
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    updated_files = 0
    for sample_file in sample_files:
        if remove_extra_spaces(sample_file):
            updated_files += 1
    
    print(f"Removed extra spaces from {updated_files} of {len(sample_files)} sample files")

if __name__ == "__main__":
    main()
