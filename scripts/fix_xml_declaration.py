"""
Fix XML declaration issues in sample messages.
"""
import os
import sys
import glob
import re

def fix_xml_declaration(file_path):
    """
    Fix XML declaration issues in a file.
    
    Args:
        file_path (str): Path to the XML file
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Fixing XML declaration in {os.path.basename(file_path)}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '</?xml>' in content:
            content = content.replace('<?xml version="1.0" encoding="UTF-8"?></?xml>', 
                                     '<?xml version="1.0" encoding="UTF-8"?>')
        
        content = re.sub(r'(\d+\.\d+)"?\s+Ccy="([^"]+)', r'\1" Ccy="\2"', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Fixed XML declaration in {os.path.basename(file_path)}")
        return True
    
    except Exception as e:
        print(f"  Error fixing XML declaration in {os.path.basename(file_path)}: {e}")
        return False

def main():
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    fixed_files = 0
    for sample_file in sample_files:
        if fix_xml_declaration(sample_file):
            fixed_files += 1
    
    print(f"Fixed {fixed_files} of {len(sample_files)} sample files")

if __name__ == "__main__":
    main()
