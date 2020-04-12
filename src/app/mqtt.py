import os, time, threading, random, string
import paho.mqtt.client as mqtt

from app.schemas import JournalRecord
from app.api.service import add_device_journal_record


# service function
def random_str(len: int):
    chars = string.ascii_uppercase
    return ''.join(random.choice(chars) for i in range(len))


def heartbeat(timeout: int = 10):
    if MQTTClient.connected_flag:
        print("mqtt heartbeat", time.ctime())
        mqtt_publish('status/journalize/state', 'CONNECTED')
        # TODO: publish statistic data
    else:
        print("mqtt is not connected...")
    threading.Timer(timeout, heartbeat).start()


# credentials
HOST = os.getenv('MQTT_HOST', 'sa100cloud.com')
PORT = os.getenv('MQTT_PORT', '1883')
USERNAME = os.getenv('MQTT_USERNAME', 'admin')
PASSWORD = os.getenv('MQTT_PASSWORD', 'adminpsw')
CLIENT_ID = os.getenv('MQTT_PASSWORD', 'Journalize_' + random_str(8))

# constants
device_journal_topic_mask = '+/+/journal/#'
client_journal_topic_mask = 'status/+/journal/#'


def on_message_callback(client, userdata, message):
    # print(f"topic: {message.topic}, payload: {str(message.payload.decode('utf-8'))}")
    # print("message qos:", message.qos)
    # print("message retain flag:", message.retain)
    path = str(message.topic).split('/')
    if path[2] == 'journal':
        print(f'device: "{path[0]}/{path[1]}", len:', path.__len__())
        if path.__len__() < 4 or not path[3]:
            print("key not defined!", path)
            return None
        value = str(message.payload.decode("utf-8"))
        data = JournalRecord(
            key=path[3],
            value=value
        )
        add_device_journal_record(device_type=path[0], device_uuid=path[1], data=data)


# Result codes:
# 0: Connection successful
# 1: Connection refused – incorrect protocol version
# 2: Connection refused – invalid client identifier
# 3: Connection refused – server unavailable
# 4: Connection refused – bad username or password
# 5: Connection refused – not authorised
# 6 - 255: Currently unused.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        print("MQTT: connected!")
        mqtt_subscribe(device_journal_topic_mask)
        mqtt_subscribe(client_journal_topic_mask)
    else:
        client.connected_flag = False
        print("MQTT: connect failed, rc=", rc)
        time.sleep(5)  # wait
        client.reconnect()


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("MQTT: Unexpected disconnection!")
    print("MQTT disconnected, rc=", rc)
    client.connected_flag = False
    time.sleep(5)  # wait
    client.reconnect()


# def on_subscribe(client, userdata, mid, granted_qos):
#     print("subscribed:", mid)


# https://www.eclipse.org/paho/clients/python/docs/
# on_publish(client, userdata, mid)
# on_unsubscribe(client, userdata, mid)
# on_log(client, userdata, level, buf)


def initialize_client(cname):
    client = mqtt.Client(cname, False)

    # callbacks
    client.on_message = on_message_callback
    # message_callback_add(sub, callback) / message_callback_remove(sub)
    # sub       the subscription filter to match against for this callback.
    #           Only one callback may be defined per literal sub string
    # callback  the callback to be used. Takes the same form as the on_message callback.

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    # client.on_subscribe = on_subscribe
    # client.on_unsubscribe = on_unsubscribe

    # flags
    client.run_flag = False
    client.connected_flag = False
    client.subscribe_flag = False

    return client


def mqtt_connect():
    print(f"MQTT: connecting to {HOST}:{PORT} as {USERNAME}/{CLIENT_ID}")
    MQTTClient.will_set('status/journalize/state', 'Disconnected', retain=True)
    MQTTClient.username_pw_set(username=USERNAME, password=PASSWORD)
    MQTTClient.connect_async(HOST, int(PORT))
    MQTTClient.loop_start()
    heartbeat()
    return None


def mqtt_disconnect():
    if MQTTClient.connected_flag:
        MQTTClient.disconnect()
    MQTTClient.loop_stop()
    return None


def mqtt_subscribe(topic: str, qos: int = 0):
    if MQTTClient.connected_flag:
        print(f"MQTT: subscribing to '{topic}', qos:", qos)
        MQTTClient.subscribe(topic, qos)


def mqtt_unsubscribe(topic: str):
    if MQTTClient.connected_flag:
        print(f"MQTT: unsubscribing from '{topic}'")
        MQTTClient.unsubscribe(topic)


def mqtt_publish(topic: str, payload: str, qos: int = 0, retain: bool = False):
    if MQTTClient.connected_flag:
        MQTTClient.publish(topic, payload, qos, retain)


# instance
MQTTClient = initialize_client(CLIENT_ID)
