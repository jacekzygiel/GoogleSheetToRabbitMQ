import json
from oauth2client import file, client, tools
from googleapiclient.discovery import build
from httplib2 import Http
import pika
from configparser import ConfigParser


class RabbitSender:
    def __init__(self, rabbit_host, rabbit_queue, rabbit_exchange, rabbit_routing_key):
        self.connection = None
        self.channel = None
        self.queue = None

        self.rabbit_host = rabbit_host
        self.rabbit_queue = rabbit_queue
        self.rabbit_exchange = rabbit_exchange
        self.rabbit_routing_key = rabbit_routing_key

    def create_connection(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbit_host))

    def close_connection(self):
        self.connection.close()

    def create_channel(self):
        self.channel = self.connection.channel()

    def declare_queue(self):
        self.queue = self.channel.queue_declare(queue=self.rabbit_queue)

    def simple_prepare_to_publish(self):
        self.create_connection()
        self.create_channel()
        self.declare_queue()

    def publish_json(self, json_):
        self.channel.basic_publish(exchange=self.rabbit_exchange,
                                   routing_key=self.rabbit_routing_key,
                                   body=json_)
        print("Sent to rabbit: " + json)


class GoogleSheet:
    def __init__(self, spreadsheet_id, spreadsheet_range):
        self.service = None
        self.response = None
        self.json = None
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet_range = spreadsheet_range

    def pass_credentials(self):
        scopes = 'https://www.googleapis.com/auth/spreadsheets.readonly'
        store = file.Storage('token.json')
        creds = store.get()

        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', scopes)
            creds = tools.run_flow(flow, store)
        self.service = build('sheets', 'v4', http=creds.authorize(Http()))

    def read_data_from_sheet(self):
        request = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id,
                                                           range=self.spreadsheet_range)
        self.response = request.execute()

    def parse_field_to_json(self, field_name):
        self.json = json.dumps(self.response[field_name])

    def get_json(self):
        return self.json


class Config:
    def __init__(self, path):
        self.path = path
        self.config = None

    def parse_config(self):
        self.config = ConfigParser()
        self.config.read(self.path)

    def get_value(self, section, field):
        return self.config[section][field]


if __name__ == '__main__':
    config = Config("config.ini")
    config.parse_config()

    SPREADSHEET_ID = config.get_value("Spreadsheet", "id")
    SPREADSHEET_RANGE = config.get_value("Spreadsheet", "range")

    RABBIT_HOST = config.get_value("RabbitMQ", "host")
    RABBIT_QUEUE = config.get_value("RabbitMQ", "queue")
    RABBIT_EXCHANGE = config.get_value("RabbitMQ", "exchange")
    RABBIT_ROUTINGKEY = config.get_value("RabbitMQ", "routingkey")

    sheet = GoogleSheet(SPREADSHEET_ID, SPREADSHEET_RANGE)
    sheet.pass_credentials()
    sheet.read_data_from_sheet()
    sheet.parse_field_to_json("values")
    json = sheet.get_json()

    rabbit = RabbitSender(RABBIT_HOST, RABBIT_QUEUE, RABBIT_EXCHANGE, RABBIT_ROUTINGKEY)
    rabbit.simple_prepare_to_publish()
    rabbit.publish_json(json)
    rabbit.close_connection()