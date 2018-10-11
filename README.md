# Google Sheets to RabbitMQ

## Prerequisite

1. Install dependencies
`python -m pip install -r requirements.txt`

2. Enable the Google Sheets API
3. Download the configuration file and save in main project directory with a name `credentials.json`
4. Setup configuration in config.ini:
    1. Spreedsheet id  - e.g. for url `https://docs.google.com/spreadsheets/d/1v9YzGazewSYS/`
    spreadsheet_id value is `1v9YzGazewSYS`
    2. Set Spreadsheet range of cells to get e.g. `'Arkusz1!A2:E'`
    3. RabbitMQ data

## Run using command line
`python sheetToRabbit.py`