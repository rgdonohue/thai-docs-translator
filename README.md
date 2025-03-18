# Thai Fishing Document Search

This project processes Thai Maritime Enforcement Command Center reports to:
1. Extract text from Thai PDFs
2. Translate the content to English
3. Search for specific vessel names
4. Update a tracking spreadsheet with results

## Setup

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
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

```python
python src/main.py
```

## Security Notes

- API keys and credentials should be stored in `.env` file
- Never commit `.env` or credential files to version control
- Use environment variables for sensitive configuration 