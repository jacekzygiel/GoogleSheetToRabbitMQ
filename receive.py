import pika
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

RABBIT_HOST = config['RabbitMQ']['host']
QUEUE = config['RabbitMQ']['queue']
ROUNTING_KEY = config['RabbitMQ']['routingkey']

connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(callback,
                      queue=QUEUE,
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
