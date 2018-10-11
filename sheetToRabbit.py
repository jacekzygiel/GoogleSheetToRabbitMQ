import json
from oauth2client import file, client, tools
from googleapiclient.discovery import build
from httplib2 import Http
import pika
from configparser import ConfigParser


class SheetToRabbit:
    def __init__(self):
        self.service = None
        self.response = None
        self.json_values = None
        self.SPREADSHEET_ID = None
        self.SPREADSHEET_RANGE = None
        self.RABBIT_HOST = None
        self.RABBIT_QUEUE = None
        self.RABBIT_EXCHANGE = None
        self.RABBIT_ROUNTING_KEY = None

    def get_config(self):
        config = ConfigParser()
        self.config.read("config.ini")
        self.SPREADSHEET_ID = config['Spreadsheet']['id']
        self.SPREADSHEET_RANGE = config['Spreadsheet']['range']
        self.RABBIT_HOST = config['RabbitMQ']['host']
        self.RABBIT_QUEUE = config['RabbitMQ']['queue']
        self.RABBIT_EXCHANGE = config['RabbitMQ']['exchange']
        self.RABBIT_ROUNTING_KEY = config['RabbitMQ']['routingkey']

    def check_credentials(self):
        scopes = 'https://www.googleapis.com/auth/spreadsheets.readonly'
        store = file.Storage('token.json')
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', scopes)
            creds = tools.run_flow(flow, store)
        self.service = build('sheets', 'v4', http=creds.authorize(Http()))

    def send_request_to_google_sheet(self):
        request = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID, range=self.SPREADSHEET_RANGE)
        self.response = request.execute()

    def parse_values_to_json(self):
        return json.dumps(self.response['values'])

    def send_values_to_rabbit(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.RABBIT_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=self.RABBIT_QUEUE)
        channel.basic_publish(exchange=self.RABBIT_EXCHANGE_,
                              routing_key=self.RABBIT_ROUNTING_KEY,
                              body=self.json_values)
        print("Sent to rabbit: " + self.json_values)
        connection.close()


if __name__ == '__main__':
    worker = SheetToRabbit()
    worker.get_config()
    worker.check_credentials()
    worker.send_request_to_google_sheet()
    worker.parse_values_to_json()
    worker.send_values_to_rabbit()