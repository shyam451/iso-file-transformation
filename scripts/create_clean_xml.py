"""
Create clean XML files for ISO 20022 payment scenarios.
This script generates well-formed XML files from scratch based on the payment scenarios.
"""
import os
import sys
import glob
import json

def create_domestic_payment_xml():
    """Create a clean XML for domestic payment scenario."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>MSG-DOMESTIC-PAYMENT-001</MsgId>
      <CreDtTm>2025-04-03T12:00:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <EndToEndId>E2E-DOM-001</EndToEndId>
        <TxId>TX-DOM-001</TxId>
      </PmtId>
      <PmtTpInf>
        <SvcLvl>
          <Cd>NURG</Cd>
        </SvcLvl>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="CAD">1000.00</IntrBkSttlmAmt>
      <ChrgBr>SHAR</ChrgBr>
      <Dbtr>
        <Nm>John Smith</Nm>
        <PstlAdr>
          <StrtNm>123 Maple Street</StrtNm>
          <TwnNm>Toronto</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>12345678</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>BANKCA01XXX</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>BANKCA02XXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Jane Doe</Nm>
        <PstlAdr>
          <StrtNm>456 Oak Avenue</StrtNm>
          <TwnNm>Vancouver</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>87654321</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>Invoice payment</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
"""
    return xml

def create_cross_border_payment_xml():
    """Create a clean XML for cross-border payment scenario."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>MSG-CROSS-BORDER-PAYMENT-001</MsgId>
      <CreDtTm>2025-04-03T12:00:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <EndToEndId>E2E-XBORDER-001</EndToEndId>
        <TxId>TX-XBORDER-001</TxId>
      </PmtId>
      <PmtTpInf>
        <SvcLvl>
          <Cd>NURG</Cd>
        </SvcLvl>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="USD">2000.00</IntrBkSttlmAmt>
      <ChrgBr>SHAR</ChrgBr>
      <Dbtr>
        <Nm>John Smith</Nm>
        <PstlAdr>
          <StrtNm>123 Maple Street</StrtNm>
          <TwnNm>Toronto</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>12345678</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>BANKCA01XXX</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>BANKUS01XXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Jane Doe</Nm>
        <PstlAdr>
          <StrtNm>789 Broadway</StrtNm>
          <TwnNm>New York</TwnNm>
          <Ctry>US</Ctry>
        </PstlAdr>
        <CtryOfRes>US</CtryOfRes>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>87654321</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>International invoice payment</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
"""
    return xml

def create_high_value_payment_xml():
    """Create a clean XML for high-value payment scenario."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>MSG-HIGH-VALUE-PAYMENT-001</MsgId>
      <CreDtTm>2025-04-03T12:00:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <EndToEndId>E2E-HIGHVAL-001</EndToEndId>
        <TxId>TX-HIGHVAL-001</TxId>
      </PmtId>
      <PmtTpInf>
        <SvcLvl>
          <Cd>NURG</Cd>
        </SvcLvl>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="CAD">1000000.00</IntrBkSttlmAmt>
      <ChrgBr>SHAR</ChrgBr>
      <Dbtr>
        <Nm>ABC Corporation</Nm>
        <PstlAdr>
          <StrtNm>123 Corporate Plaza</StrtNm>
          <TwnNm>Toronto</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>12345678</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>BANKCA01XXX</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>BANKCA02XXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>XYZ Corporation</Nm>
        <PstlAdr>
          <StrtNm>456 Business Park</StrtNm>
          <TwnNm>Vancouver</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>87654321</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>Corporate acquisition payment</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
"""
    return xml

def create_urgent_payment_xml():
    """Create a clean XML for urgent payment scenario."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>MSG-URGENT-PAYMENT-001</MsgId>
      <CreDtTm>2025-04-03T12:00:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <EndToEndId>E2E-URGENT-001</EndToEndId>
        <TxId>TX-URGENT-001</TxId>
      </PmtId>
      <PmtTpInf>
        <InstrPrty>HIGH</InstrPrty>
        <SvcLvl>
          <Cd>URGP</Cd>
        </SvcLvl>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="CAD">5000.00</IntrBkSttlmAmt>
      <ChrgBr>SHAR</ChrgBr>
      <Dbtr>
        <Nm>John Smith</Nm>
        <PstlAdr>
          <StrtNm>123 Maple Street</StrtNm>
          <TwnNm>Toronto</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>12345678</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>BANKCA01XXX</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>BANKCA02XXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Jane Doe</Nm>
        <PstlAdr>
          <StrtNm>456 Oak Avenue</StrtNm>
          <TwnNm>Vancouver</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>87654321</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>Urgent payment for medical expenses</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
"""
    return xml

def create_cad_interbank_settlement_xml():
    """Create a clean XML for CAD interbank settlement scenario."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>MSG-CAD-INTERBANK-SETTLEMENT-001</MsgId>
      <CreDtTm>2025-04-03T12:00:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <EndToEndId>E2E-CAD-INTRBNK-001</EndToEndId>
        <TxId>TX-CAD-INTRBNK-001</TxId>
      </PmtId>
      <PmtTpInf>
        <SvcLvl>
          <Cd>NURG</Cd>
        </SvcLvl>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="CAD">500000.00</IntrBkSttlmAmt>
      <InstdAmt Ccy="CAD">500000.00</InstdAmt>
      <ChrgBr>SHAR</ChrgBr>
      <Dbtr>
        <Nm>Bank of Montreal</Nm>
        <PstlAdr>
          <StrtNm>100 King Street West</StrtNm>
          <TwnNm>Toronto</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>12345678</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>BOFMCAM2XXX</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>ROYCCAT2XXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Royal Bank of Canada</Nm>
        <PstlAdr>
          <StrtNm>200 Bay Street</StrtNm>
          <TwnNm>Toronto</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>87654321</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>Interbank settlement</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
"""
    return xml

def create_return_payment_xml():
    """Create a clean XML for return payment scenario."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>MSG-RETURN-PAYMENT-001</MsgId>
      <CreDtTm>2025-04-03T12:00:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <EndToEndId>E2E-RETURN-001</EndToEndId>
        <TxId>TX-RETURN-001</TxId>
        <ClrSysRef>ORIG-TX-123456</ClrSysRef>
      </PmtId>
      <PmtTpInf>
        <SvcLvl>
          <Cd>NURG</Cd>
        </SvcLvl>
        <LclInstrm>
          <Cd>RTN</Cd>
        </LclInstrm>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="CAD">1500.00</IntrBkSttlmAmt>
      <ChrgBr>SHAR</ChrgBr>
      <Dbtr>
        <Nm>Jane Doe</Nm>
        <PstlAdr>
          <StrtNm>456 Oak Avenue</StrtNm>
          <TwnNm>Vancouver</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>87654321</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>BANKCA02XXX</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>BANKCA01XXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>John Smith</Nm>
        <PstlAdr>
          <StrtNm>123 Maple Street</StrtNm>
          <TwnNm>Toronto</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>12345678</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <RtrRsnInf>
        <Rsn>
          <Cd>AC01</Cd>
        </Rsn>
        <AddtlInf>Incorrect account number</AddtlInf>
      </RtrRsnInf>
      <RmtInf>
        <Ustrd>Return of payment</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
"""
    return xml

def create_international_payment_xml():
    """Create a clean XML for international payment scenario."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>MSG-INTERNATIONAL-PAYMENT-001</MsgId>
      <CreDtTm>2025-04-03T12:00:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <EndToEndId>E2E-INTL-001</EndToEndId>
        <TxId>TX-INTL-001</TxId>
      </PmtId>
      <PmtTpInf>
        <SvcLvl>
          <Cd>NURG</Cd>
        </SvcLvl>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="EUR">10000.00</IntrBkSttlmAmt>
      <InstdAmt Ccy="USD">12000.00</InstdAmt>
      <XchgRate>1.2</XchgRate>
      <ChrgBr>SHAR</ChrgBr>
      <Dbtr>
        <Nm>John Smith</Nm>
        <PstlAdr>
          <StrtNm>123 Maple Street</StrtNm>
          <TwnNm>Toronto</TwnNm>
          <Ctry>CA</Ctry>
        </PstlAdr>
        <CtryOfRes>CA</CtryOfRes>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>12345678</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>BANKCA01XXX</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>BANKFR01XXX</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Pierre Dupont</Nm>
        <PstlAdr>
          <StrtNm>45 Rue de Paris</StrtNm>
          <TwnNm>Paris</TwnNm>
          <Ctry>FR</Ctry>
        </PstlAdr>
        <CtryOfRes>FR</CtryOfRes>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>FR7630006000011234567890189</IBAN>
        </Id>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>International invoice payment</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
"""
    return xml

def main():
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_messages")
    
    os.makedirs(sample_dir, exist_ok=True)
    
    scenarios = {
        "domestic_payment.xml": create_domestic_payment_xml(),
        "cross-border_payment.xml": create_cross_border_payment_xml(),
        "high-value_payment.xml": create_high_value_payment_xml(),
        "urgent_payment.xml": create_urgent_payment_xml(),
        "cad_interbank_settlement.xml": create_cad_interbank_settlement_xml(),
        "return_payment.xml": create_return_payment_xml(),
        "international_payment.xml": create_international_payment_xml()
    }
    
    for filename, xml_content in scenarios.items():
        file_path = os.path.join(sample_dir, filename)
        
        if os.path.exists(file_path):
            backup_path = file_path + '.bak'
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                print(f"  Backed up original {filename} to {os.path.basename(backup_path)}")
            except Exception as e:
                print(f"  Error backing up {filename}: {e}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            print(f"  Created clean XML for {filename}")
        except Exception as e:
            print(f"  Error creating clean XML for {filename}: {e}")
    
    print(f"Created clean XML files for {len(scenarios)} payment scenarios")

if __name__ == "__main__":
    main()
