import json
from oauth2client import file, client, tools
from googleapiclient.discovery import build
from httplib2 import Http
import pika
from pprint import pprint

def check_credentials(creds_):
    if not creds_ or creds_.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds_ = tools.run_flow(flow, store)
    return build('sheets', 'v4', http=creds_.authorize(Http()))


def send_request(service_, spreadsheet_id_, range_):
    request = service_.spreadsheets().values().get(spreadsheetId=spreadsheet_id_, range=range_)
    return request.execute()


def parse_values_to_json(response_):
    return json.dumps(response_['values'])


def send_values_to_rabbit(connection_parameters, queue_, exchange_, routing_key_, json_values_):
    connection = pika.BlockingConnection(pika.ConnectionParameters(connection_parameters))
    channel = connection.channel()
    channel.queue_declare(queue=queue_)
    channel.basic_publish(exchange=exchange_,
                          routing_key=routing_key_,
                          body=json_values_)
    connection.close()


if __name__ == '__main__':
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('token.json')
    creds = store.get()

    service = check_credentials(creds)

    spreadsheet_id = '1v9YzGazewSYSNuNMp37b6MQf2QP64INIfrZ1lrrB3Nw'
    range = 'Arkusz1!A2:E'

    response = send_request(service, spreadsheet_id, range)
    json_values = parse_values_to_json(response)
    pprint(json_values)

    CONNECTION_PARAMETERS = ""
    QUEUE = ""
    EXCHANGE = ""
    ROUNTING_KEY = ""
    send_values_to_rabbit(CONNECTION_PARAMETERS, QUEUE, EXCHANGE, ROUNTING_KEY, json_values)
