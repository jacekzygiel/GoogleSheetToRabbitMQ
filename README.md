# Google Sheets to RabbitMQ

## Description
Example project with implementation of reading data from Google Sheet and sending to RabbitMQ in json format.
Maps data from Google Sheet cells to key - value json.
e.g.

| Id | Key  | Value |
|----|------|-------|
| 1  | Mark | 150   |
| 2  | Tom  | 23    |
| 3  | Ben  | 214   |

Will be passed to RabbitMQ as a json:
`{'Mark', '150', 'Tom', '23', 'Ben', '214'}`

## Prerequisite

1. Install dependencies
`python -m pip install -r requirements.txt`

2. Enable the Google Sheets API
3. Download the configuration file and save in main project directory with a name `credentials.json`
4. Setup configuration in config.ini:
    1. Spreadsheet id  - e.g. for url `https://docs.google.com/spreadsheets/d/1v9YzGazewSYS/`
    spreadsheet_id value is `1v9YzGazewSYS`
    2. Set Spreadsheet range of cells to get e.g. `'Arkusz1!A2:E'`
    3. RabbitMQ data

## Run using command line
`python sheetToRabbit.py`