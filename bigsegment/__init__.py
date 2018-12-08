'LED Segment Mapper'

import click
import json
import logging
import paho.mqtt.client

__version__ = '1.0.0'

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
    '9': 'ABCDFG',
    'A': 'ABCEFG',
    'B': 'CDEFG',
    'C': 'ADEF',
    'D': 'BCDEG',
    'E': 'ADEFG',
    'F': 'EFAG',
    'H': 'CEFG',
    'I': 'E',
    'J': 'BCDE',
    'L': 'DEF',
    'N': 'CEG',
    'O': 'CDEG',
    'P': 'ABEFG',
    'R': 'EG',
    'S': 'ACDFG',
    'T': 'DEFG',
    'U': 'BCDEF',
    'Y': 'BCDFG',
    'Z': 'ABDEG',
    '-': 'G',
    ' ': 'G',
}

COLORS = {
    '0': '#ff0000',
    '1': '#ffaa00',
    '2': '#aaff00',
    '3': '#00ff00',
    '4': '#00ffaa',
    '5': '#00aaff',
    '6': '#2b00ff',
    '7': '#aa00ff',
    '8': '#ff00d4',
    '9': '#ff002b',
    'A': '#ff00d4',
    'B': '#ffff33',
    'C': '#ffff33',
    'D': '#00ffff',
    'E': '#883dff',
    'F': '#2b00ff',
    'H': '#883dff',
    'I': '#2b00ff',
    'J': '#aa00ff',
    'L': '#aaff00',
    'N': '#ff002b',
    'O': '#ff002b',
    'P': '#00ffff',
    'R': '#00ffff',
    'S': '#ffaa00',
    'T': '#ffaa00',
    'U': '#ffaa00',
    'Y': '#ffff33',
    'Z': '#ffff33',
    '-': '#ffffff',
    ' ': '#000000',
}

ORDER = 'FABGEDC'

logging.basicConfig(format='%(asctime)s <%(levelname)s> %(message)s',
                    level=logging.DEBUG, datefmt="%Y-%m-%dT%H:%M:%S")


def transform(letter):
    logging.debug('Transforming letter: ' + letter)
    if not letter in SEGMENTS:
        return None
    segments = SEGMENTS[letter]
    compound = []
    for segment in ORDER:
        if segment in segments:
            compound.append('15, "%s"' % COLORS[letter])
        else:
            compound.append('15, "#000000"')
    compound = '[%s]' % ', '.join(compound)
    logging.debug('Compound: ' + compound)
    return compound


def on_connect(client, userdata, flags, rc):
    logging.info('MQTT connected (code: %d)' % rc)
    client.subscribe(userdata['topic'])


def on_message(client, userdata, msg):
    logging.debug('Received topic: %s' % msg.topic)
    if msg.topic == userdata['topic']:
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
            client.publish('node/%s/led-strip/-/compound/set' % userdata['id'], qos=1, payload=compound)
    else:
        logging.warning('Unknown topic')


@click.command()
@click.option('--host', '-h', default='127.0.0.1', help='MQTT broker host.')
@click.option('--port', '-p', default='1883', help='MQTT broker port.')
@click.option('--topic', '-t', required=True, help='MQTT topic to listen to.')
@click.option('--id', '-i', default='power-controller:0', help='Identifier of Power Controller Kit.')
@click.version_option(version=__version__)
def main(host, port, topic, id):
    try:
        logging.info('Program started')
        mqtt = paho.mqtt.client.Client()
        mqtt.user_data_set({'topic': topic, 'id': id})
        mqtt.on_connect = on_connect
        mqtt.on_message = on_message
        mqtt.connect(host, int(port))
        while True:
            mqtt.loop()
    except KeyboardInterrupt:
        pass
