"""
Manually prettify XML files to improve readability with consistent indentation.
This script handles malformed XML that standard XML parsers cannot process.
"""
import os
import sys
import glob
import re

def remove_duplicate_xml_declaration(content):
    """Remove duplicate XML declarations."""
    if content.count('<?xml') > 1:
        return re.sub(r'<\?xml.*?\?>\s*', '', content, count=1)
    return content

def fix_malformed_tags(content):
    """Fix malformed tags in the XML content."""
    content = re.sub(r'<([^>]+)>ID-<\1>-001', r'<\1>ID-\1-001', content)
    
    content = re.sub(r'(\d+\.\d+)"\s+Ccy="([^"]+)', r'\1" Ccy="\2', content)
    content = re.sub(r'(\d+\.\d+)\s+Ccy="([^"]+)', r'\1" Ccy="\2', content)
    
    return content

def add_indentation(content):
    """Add proper indentation to XML content."""
    match = re.search(r'<Document[^>]*>(.*?)</Document>', content, re.DOTALL)
    if not match:
        return content
    
    document_attrs = re.search(r'<Document([^>]*)>', content).group(1)
    document_content = match.group(1)
    
    result = '<?xml version="1.0" encoding="UTF-8"?>\n'
    result += f'<Document{document_attrs}>\n'
    
    fi_match = re.search(r'<FIToFICstmrCdtTrf>(.*?)</FIToFICstmrCdtTrf>', document_content, re.DOTALL)
    if fi_match:
        fi_content = fi_match.group(1)
        result += '  <FIToFICstmrCdtTrf>\n'
        
        grp_match = re.search(r'<GrpHdr>(.*?)</GrpHdr>', fi_content, re.DOTALL)
        if grp_match:
            grp_content = grp_match.group(1)
            result += '    <GrpHdr>\n'
            
            elements = re.findall(r'<([^/>\s]+)([^>]*)>(.*?)</\1>', grp_content, re.DOTALL)
            for tag, attrs, content in elements:
                if len(content.strip()) < 50 and '<' not in content:
                    result += f'      <{tag}{attrs}>{content}</{tag}>\n'
                else:
                    result += f'      <{tag}{attrs}>\n'
                    sub_elements = re.findall(r'<([^/>\s]+)([^>]*)>(.*?)</\1>', content, re.DOTALL)
                    for sub_tag, sub_attrs, sub_content in sub_elements:
                        if len(sub_content.strip()) < 50 and '<' not in sub_content:
                            result += f'        <{sub_tag}{sub_attrs}>{sub_content}</{sub_tag}>\n'
                        else:
                            result += f'        <{sub_tag}{sub_attrs}>{sub_content}</{sub_tag}>\n'
                    result += f'      </{tag}>\n'
            
            result += '    </GrpHdr>\n'
        
        cdt_match = re.search(r'<CdtTrfTxInf>(.*?)</CdtTrfTxInf>', fi_content, re.DOTALL)
        if cdt_match:
            cdt_content = cdt_match.group(1)
            result += '    <CdtTrfTxInf>\n'
            
            elements = re.findall(r'<([^/>\s]+)([^>]*)>(.*?)</\1>', cdt_content, re.DOTALL)
            for tag, attrs, content in elements:
                if len(content.strip()) < 50 and '<' not in content:
                    result += f'      <{tag}{attrs}>{content}</{tag}>\n'
                else:
                    result += f'      <{tag}{attrs}>\n'
                    sub_elements = re.findall(r'<([^/>\s]+)([^>]*)>(.*?)</\1>', content, re.DOTALL)
                    for sub_tag, sub_attrs, sub_content in sub_elements:
                        if len(sub_content.strip()) < 50 and '<' not in sub_content:
                            result += f'        <{sub_tag}{sub_attrs}>{sub_content}</{sub_tag}>\n'
                        else:
                            result += f'        <{sub_tag}{sub_attrs}>{sub_content}</{sub_tag}>\n'
                    result += f'      </{tag}>\n'
            
            result += '    </CdtTrfTxInf>\n'
        
        remaining = re.sub(r'<GrpHdr>.*?</GrpHdr>', '', fi_content, flags=re.DOTALL)
        remaining = re.sub(r'<CdtTrfTxInf>.*?</CdtTrfTxInf>', '', remaining, flags=re.DOTALL)
        if remaining.strip():
            result += f'    {remaining.strip()}\n'
        
        result += '  </FIToFICstmrCdtTrf>\n'
    
    remaining = re.sub(r'<FIToFICstmrCdtTrf>.*?</FIToFICstmrCdtTrf>', '', document_content, flags=re.DOTALL)
    if remaining.strip():
        result += f'  {remaining.strip()}\n'
    
    result += '</Document>'
    return result

def prettify_xml_file(file_path):
    """Prettify an XML file with consistent indentation."""
    print(f"Prettifying {os.path.basename(file_path)}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = remove_duplicate_xml_declaration(content)
        content = fix_malformed_tags(content)
        
        pretty_content = add_indentation(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(pretty_content)
        
        print(f"  Successfully prettified {os.path.basename(file_path)}")
        return True
    
    except Exception as e:
        print(f"  Error prettifying {os.path.basename(file_path)}: {e}")
        return False

def main():
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    prettified_files = 0
    for sample_file in sample_files:
        if prettify_xml_file(sample_file):
            prettified_files += 1
    
    print(f"Prettified {prettified_files} of {len(sample_files)} sample files")

if __name__ == "__main__":
    main()
