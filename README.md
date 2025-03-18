# Thai Fishing Document Search

This project processes Thai Maritime Enforcement Command Center reports to:
1. Extract text from Thai PDFs
2. Translate the content to English
3. Search for specific vessel names
4. Update a tracking spreadsheet with results

## Project Overview

This tool automates the process of searching Thai Maritime Enforcement Command Center reports for mentions of specific fishing vessels. The reports detail various incidents such as:
- Incursions into restricted waters
- Medical emergencies at sea
- Other maritime incidents

## Methodology

### 1. Data Sources
- **Reports**: Thai Maritime Enforcement Command Center PDFs
  - Source: [Command Center Data](https://thai-mecc.go.th/thaimeccsite/th/datacenter/list/37)
  - Format: PDF documents in Thai language
  - Location: [Google Drive Folder](https://drive.google.com/drive/folders/16s54ytS4kozrvq4JPGNfR0sbzkSsaZH9)

- **Vessel List**: Spreadsheet containing target vessel names
  - Format: Google Sheets document
  - Contains: Vessel names and columns for report links
  - Location: [Vessel Spreadsheet](https://docs.google.com/spreadsheets/d/1B3fZdyk2DF6U4NyPqkyB2tqImWbPrm83fiwN67iJVpU)

### 2. Processing Pipeline
1. **PDF Text Extraction**
   - Read Thai PDFs using OCR-aware text extraction
   - Maintain page structure for reference

2. **Translation**
   - Translate extracted text from Thai to English
   - Uses Google Cloud Translation API
   - Preserves document structure

3. **Vessel Name Search**
   - Implements fuzzy matching to account for translation variations
   - Searches both exact matches and approximate matches
   - Records match locations and confidence scores

4. **Results Recording**
   - Updates vessel spreadsheet with links to matching reports
   - Maintains translated versions of PDFs
   - Logs processing results and any issues

### 3. Outputs
1. Translated versions of each PDF (prefix: "translated_")
2. Updated spreadsheet with links to relevant reports
3. Processing logs and error reports

## Setup

1. Clone this repository
2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
VESSEL_SPREADSHEET_ID=your-spreadsheet-id
REPORTS_FOLDER_ID=your-folder-id
```

4. Configure Google Cloud services:
   - Enable Cloud Translation API
   - Enable Google Sheets API
   - Create service account with appropriate permissions

## Project Structure

```
.
├── src/
│   ├── pdf_processor.py      # PDF text extraction
│   ├── translator.py         # Translation handling
│   ├── search.py            # Vessel name search
│   ├── spreadsheet.py       # Google Sheets integration
│   └── config.py            # Configuration management
├── tests/                   # Test files
├── .env                     # Environment variables (not in git)
├── requirements.txt         # Project dependencies
└── README.md               # This file
```

## Usage

1. Place PDF files in the `input_pdfs` directory
2. Run the setup validator:
```bash
python src/setup_validator.py
```

3. Run the main processing script:
```bash
python src/main.py
```

4. Check the `translated_pdfs` directory for results and `logs` for processing details

## Security Notes

- API keys and credentials should be stored in `.env` file
- Never commit `.env` or credential files to version control
- Use environment variables for sensitive configuration

## Notes

- Translation services may incur costs through Google Cloud
- Processing time depends on PDF size and number
- Fuzzy matching parameters can be adjusted in config.py 