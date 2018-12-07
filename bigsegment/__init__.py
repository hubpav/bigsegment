'LED Segment Mapper'

import click
import json
import logging
import paho.mqtt.client

__version__ = '1.0.0'

TOPICS = ['bigsegment/0/set', 'bigsegment/1/set', 'bigsegment/2/set', 'bigsegment/3/set']

SEGMENTS = {
    '0': 'ABCDEF',
    '1': 'BC',
    '2': 'ABDEG',
    '3': 'ABCDG',
    '4': 'BCFG',
    '5': 'ACDFG',
    '6': 'ACDEFG',
    '7': 'ABC',
    '8': 'ABCDEFG',
    '9': 'ABCFG'
}

SEQUENCE = 'FABGEDC'

logging.basicConfig(format='%(asctime)s <%(levelname)s> %(message)s',
                    level=logging.DEBUG, datefmt="%Y-%m-%dT%H:%M:%S")


def transform(letter):
    logging.debug('Transforming letter: ' + letter)
    if not letter in SEGMENTS:
        return None
    segments = SEGMENTS[letter]
    compound = []
    for segment in SEQUENCE:
        if segment in segments:
            compound.append('15, "#ff0000"')
        else:
            compound.append('15, "#000000"')
    compound = '[%s]' % ', '.join(compound)
    logging.debug('Compound: ' + compound)
    return compound


def on_connect(client, userdata, flags, rc):
    logging.info('MQTT connected (code: %d)' % rc)
    for topic in TOPICS:
        client.subscribe(topic)


def on_message(client, userdata, msg):
    logging.debug('Received topic: %s' % msg.topic)
    if msg.topic in TOPICS:
        try:
            letter = json.loads(msg.payload.decode('utf-8'))
            if type(letter) is not str:
                raise
            if len(letter) != 1:
                raise
        except:
            logging.warning('Incorrect payload')
        compound = transform(letter)
        if compound is not None:
            client.publish('node/%s/led-strip/-/compound/set' % userdata, qos=1, payload=compound)
    else:
        logging.warning('Unknown topic')


@click.command()
@click.option('--host', '-h', default='127.0.0.1', help='MQTT broker host.')
@click.option('--port', '-p', default='1883', help='MQTT broker port.')
@click.option('--id', '-i', default='power-controller:0', help='Identifier of Power Controller Kit.')
@click.version_option(version=__version__)
def main(host, port, id):
    try:
        logging.info('Program started')
        mqtt = paho.mqtt.client.Client()
        mqtt.user_data_set(id)
        mqtt.on_connect = on_connect
        mqtt.on_message = on_message
        mqtt.connect(host, int(port))
        while True:
            mqtt.loop()
    except KeyboardInterrupt:
        pass
