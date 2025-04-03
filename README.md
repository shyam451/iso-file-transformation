# ISO 20022 File Transformation

This repository contains tools for analyzing ISO 20022 message structures and generating sample XML messages for different payment scenarios. It specifically focuses on the pacs.008 (Financial Institution To Financial Institution Customer Credit Transfer) message type.

## Repository Structure

- `iso_message_generator/`: Python module for ISO 20022 message generation
   - `message_structure.py`: Extract message structure from Excel files
   - `rule_processor.py`: Process validation rules and identify payment scenarios
   - `xml_generator.py`: Generate XML messages for payment scenarios

- `sample_messages/`: Sample XML messages for different payment scenarios
   - `domestic_payment.xml`: Domestic payment scenario
   - `cross-border_payment.xml`: Cross-border payment scenario
   - `high-value_payment.xml`: High-value payment scenario
   - `urgent_payment.xml`: Urgent payment scenario
   - `cad_interbank_settlement.xml`: CAD Interbank Settlement scenario
   - `return_payment.xml`: Return Payment scenario
   - `international_payment.xml`: International Payment scenario

- `scripts/`: Utility scripts
   - `analyze_iso_file.py`: Analyze ISO 20022 Excel files
   - `extract_message_structure.py`: Extract message structure and generate sample files
   - `generate_custom_message.py`: Generate custom messages for specific scenarios
   - `validate_rules.py`: Validate XML messages against rules from the Excel file
   - `create_clean_xml.py`: Generate clean, well-formed XML files for all scenarios

- `data/`: Reference data files
   - `rtr_fi_to_fi_customer_credit_transfer_pacs.008excel.xlsx`: Reference Excel file for pacs.008 message structure

- `validation_report.md`: Report of validation results for all sample messages

## Payment Scenarios

The following payment scenarios are supported:

1. **Domestic Payment**: A payment between two financial institutions within the same country
2. **Cross-Border Payment**: A payment between two financial institutions in different countries
3. **High-Value Payment**: A high-value payment between financial institutions
4. **Urgent Payment**: An urgent payment with high priority
5. **CAD Interbank Settlement**: Payment with CAD as the interbank settlement currency
6. **Return Payment**: A payment that is being returned to the original sender
7. **International Payment**: An international payment with currency conversion

## Usage

### Generating Sample Messages

To generate a sample message for a specific payment scenario:

```bash
python scripts/generate_custom_message.py --scenario "Domestic Payment" --output custom_domestic.xml
```

### Analyzing ISO 20022 Excel Files

To analyze an ISO 20022 Excel file:

```bash
python scripts/analyze_iso_file.py --excel /path/to/iso_excel_file.xlsx
```

### Extracting Message Structure and Generating Samples

To extract the message structure and generate sample files:

```bash
python scripts/extract_message_structure.py --excel /path/to/iso_excel_file.xlsx --output /path/to/output_dir
```

## Requirements

- Python 3.6+
- pandas
- openpyxl
