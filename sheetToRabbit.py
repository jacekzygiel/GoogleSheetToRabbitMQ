import json
from oauth2client import file, client, tools
from googleapiclient.discovery import build
from httplib2 import Http
import pika
from configparser import ConfigParser


def get_config():
    config = ConfigParser()
    config.read("config.ini")
    return config

def check_credentials():
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('token.json')
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    return build('sheets', 'v4', http=creds.authorize(Http()))


def send_request(service_, spreadsheet_id_, range_):
    request = service_.spreadsheets().values().get(spreadsheetId=spreadsheet_id_, range=range_)
    return request.execute()


def parse_values_to_json(response_):
    return json.dumps(response_['values'])


def send_values_to_rabbit(host_, queue_, exchange_, routing_key_, json_values_):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host_))
    channel = connection.channel()
    channel.queue_declare(queue=queue_)
    channel.basic_publish(exchange=exchange_,
                          routing_key=routing_key_,
                          body=json_values_)
    print("Sent to rabbit: " + json_values)
    connection.close()


if __name__ == '__main__':
    config = get_config()

    SPREADSHEET_ID = config['Spreadsheet']['id']
    SPREADSHEET_RANGE = config['Spreadsheet']['range']
    RABBIT_HOST = config['RabbitMQ']['host']
    QUEUE = config['RabbitMQ']['queue']
    EXCHANGE = config['RabbitMQ']['exchange']
    ROUNTING_KEY = config['RabbitMQ']['routingkey']

    service = check_credentials()
    response = send_request(service, SPREADSHEET_ID, SPREADSHEET_RANGE)
    json_values = parse_values_to_json(response)
    send_values_to_rabbit(RABBIT_HOST, QUEUE, EXCHANGE, ROUNTING_KEY, json_values)
