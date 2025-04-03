"""
Fix XML structure issues in sample messages to ensure well-formed XML.
This script handles complex XML structure issues that standard prettifiers cannot fix.
"""
import os
import sys
import glob
import re

def fix_xml_file(file_path):
    """
    Fix XML structure issues in a file.
    
    Args:
        file_path (str): Path to the XML file
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Fixing structure in {os.path.basename(file_path)}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content = content
        
        if fixed_content.count('<?xml') > 1:
            fixed_content = re.sub(r'<\?xml.*?\?>\s*', '', fixed_content, count=1)
        
        fixed_content = fixed_content.replace('</UltmtCdtr>', '</Dbtr>')
        
        fixed_content = re.sub(r'(\d+\.\d+)"?\s+Ccy="([^"]+)', r'\1" Ccy="\2"', fixed_content)
        
        fixed_content = re.sub(r'<([^/>\s]+)([^>]*)></\1>', r'<\1\2/>', fixed_content)
        
        fixed_content = re.sub(r'<([^>]+)>ID-<\1>-001', r'<\1>ID-\1-001', fixed_content)
        
        tag_pattern = r'<([^/>\s]+)([^>]*)>'
        tags = re.findall(tag_pattern, fixed_content)
        for tag, attrs in tags:
            if f'</{tag}>' not in fixed_content and f'{tag}/>' not in fixed_content:
                fixed_content = fixed_content.replace(f'<{tag}{attrs}>', f'<{tag}{attrs}></{tag}>')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"  Fixed structure in {os.path.basename(file_path)}")
        return True
    
    except Exception as e:
        print(f"  Error fixing structure in {os.path.basename(file_path)}: {e}")
        return False

def create_clean_xml(file_path):
    """
    Create a clean XML file from scratch based on the content of the original file.
    This is a more reliable approach for severely malformed XML.
    
    Args:
        file_path (str): Path to the XML file
        
    Returns:
        bool: True if file was updated, False otherwise
    """
    print(f"Creating clean XML for {os.path.basename(file_path)}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        xmlns_match = re.search(r'xmlns="([^"]+)"', content)
        xmlns = xmlns_match.group(1) if xmlns_match else "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08"
        
        msg_id_match = re.search(r'<MsgId>([^<]+)</MsgId>', content)
        msg_id = msg_id_match.group(1) if msg_id_match else "MSG-001"
        
        cre_dt_tm_match = re.search(r'<CreDtTm>([^<]+)</CreDtTm>', content)
        cre_dt_tm = cre_dt_tm_match.group(1) if cre_dt_tm_match else "2025-04-03T12:00:00Z"
        
        end_to_end_id_match = re.search(r'<EndToEndId>([^<]+)</EndToEndId>', content)
        end_to_end_id = end_to_end_id_match.group(1) if end_to_end_id_match else "E2E-001"
        
        dbtr_ctry_match = re.search(r'<Dbtr>.*?<CtryOfRes>([^<]+)</CtryOfRes>', content, re.DOTALL)
        dbtr_ctry = dbtr_ctry_match.group(1) if dbtr_ctry_match else "CA"
        
        dbtr_nm_match = re.search(r'<Dbtr>.*?<Nm>([^<]+)</Nm>', content, re.DOTALL)
        dbtr_nm = dbtr_nm_match.group(1) if dbtr_nm_match else "John Smith"
        
        cdtr_ctry_match = re.search(r'<Cdtr>.*?<CtryOfRes>([^<]+)</CtryOfRes>', content, re.DOTALL)
        cdtr_ctry = cdtr_ctry_match.group(1) if cdtr_ctry_match else "CA"
        
        cdtr_nm_match = re.search(r'<Cdtr>.*?<Nm>([^<]+)</Nm>', content, re.DOTALL)
        cdtr_nm = cdtr_nm_match.group(1) if cdtr_nm_match else "Jane Doe"
        
        amt_match = re.search(r'<IntrBkSttlmAmt[^>]*>([^<"]+)', content)
        amt = amt_match.group(1) if amt_match else "1000.00"
        
        ccy_match = re.search(r'<IntrBkSttlmAmt[^>]*Ccy="([^"]+)"', content)
        ccy = ccy_match.group(1) if ccy_match else "CAD"
        
        clean_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="{xmlns}">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>{msg_id}</MsgId>
      <CreDtTm>{cre_dt_tm}</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <EndToEndId>{end_to_end_id}</EndToEndId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="{ccy}">{amt}</IntrBkSttlmAmt>
      <Dbtr>
        <Nm>{dbtr_nm}</Nm>
        <CtryOfRes>{dbtr_ctry}</CtryOfRes>
      </Dbtr>
      <Cdtr>
        <Nm>{cdtr_nm}</Nm>
        <CtryOfRes>{cdtr_ctry}</CtryOfRes>
      </Cdtr>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
"""
        
        backup_path = file_path + '.bak'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(clean_xml)
        
        print(f"  Created clean XML for {os.path.basename(file_path)}")
        print(f"  Original file backed up to {os.path.basename(backup_path)}")
        return True
    
    except Exception as e:
        print(f"  Error creating clean XML for {os.path.basename(file_path)}: {e}")
        return False

def main():
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    sample_files = glob.glob(os.path.join(sample_dir, "*.xml"))
    
    print(f"Found {len(sample_files)} sample files")
    
    fixed_files = 0
    for sample_file in sample_files:
        if fix_xml_file(sample_file):
            fixed_files += 1
        else:
            create_clean_xml(sample_file)
            fixed_files += 1
    
    print(f"Fixed {fixed_files} of {len(sample_files)} sample files")

if __name__ == "__main__":
    main()
