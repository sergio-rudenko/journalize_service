import os, time, threading, random, string
import paho.mqtt.client as mqtt
# import httpx

from app.db import SessionLocal
from app.schemas import JournalCreate
from app.api.crud_journal import add_journal_record


# credentials
HOST = os.getenv('MQTT_HOST', 'sa100cloud.com')
PORT = os.getenv('MQTT_PORT', '1883')
USERNAME = os.getenv('MQTT_USER', 'admin')
PASSWORD = os.getenv('MQTT_PASS', 'adminpsw')

# constants
reconnect_timeout = 5
heartbeat_timeout = 10


# random string generator ----------------------------------------------------
def random_str(len: int):
    chars = string.ascii_uppercase
    return ''.join(random.choice(chars) for i in range(len))


CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'Journalize_' + random_str(8))

# constants
device_journal_topic_mask = '+/+/journal/#'
client_journal_topic_mask = 'status/+/journal/#'


# heartbeat function ---------------------------------------------------------
def heartbeat(timeout: int = heartbeat_timeout):
    if MQTTClient.connected_flag:
        print("Service heartbeat:", time.ctime())
        mqtt_publish('status/journalize/state', 'CONNECTED')
        # TODO: publish statistic data
    else:
        print("mqtt is not connected...")

    MQTTClient.heartbeat_timer = threading.Timer(timeout, heartbeat)
    MQTTClient.heartbeat_timer.start()


# MQTT callbacks -------------------------------------------------------------
def on_message_callback(client, userdata, message):
    print(f"MQTT: topic '{message.topic}', payload '{str(message.payload.decode('utf-8'))}'")
    # print("message qos:", message.qos)
    # print("message retain flag:", message.retain)
    path = str(message.topic).split('/')
    if path[2] == 'journal':
        print(f'device: "{path[0]}/{path[1]}"')
        if path.__len__() < 4 or not path[3]:
            print("key not defined!", path)
            return None
        value = str(message.payload.decode("utf-8"))
        print(f'key: "{path[3]}" -> "{value}"')

        record = JournalCreate(
            key=path[3],
            value=value
        )
        session = SessionLocal()  # create session
        result = add_journal_record(session,
                                    record=record,
                                    type_title=path[0],
                                    device_title=path[1])
        session.close()  # close session

        if result:
            print("journal record created, id:", result.id)

        # result = httpx.post(f'http://127.0.0.1:8000/api/v1/{path[0]}/{path[1]}/journal/',
        #                     json={
        #                         "key": path[3],
        #                         "value": value
        #                     })
        # if result.status_code == 201:
        #     print("posted ok!")
        # else:
        #     print("post failed!", result)


def on_connect_callback(client, userdata, flags, rc):
    # Result codes:
    # 0: Connection successful
    # 1: Connection refused – incorrect protocol version
    # 2: Connection refused – invalid client identifier
    # 3: Connection refused – server unavailable
    # 4: Connection refused – bad username or password
    # 5: Connection refused – not authorised
    # 6 - 255: Currently unused.
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


def on_disconnect_callback(client, userdata, rc):
    if rc != 0:
        print("MQTT: Unexpected disconnection, rc =", rc)
    else:
        print("MQTT: disconnected.")

    if not MQTTClient.shutdown_flag:
        client.connected_flag = False
        time.sleep(reconnect_timeout)
        client.reconnect()


# def on_subscribe(client, userdata, mid, granted_qos):
#     print("subscribed:", mid)


# https://www.eclipse.org/paho/clients/python/docs/
# on_publish(client, userdata, mid)
# on_unsubscribe(client, userdata, mid)
# on_log(client, userdata, level, buf)


# MQTT -----------------------------------------------------------------------
def initialize_client(cname):
    client = mqtt.Client(cname, False)

    # callbacks
    client.on_message = on_message_callback
    # message_callback_add(sub, callback) / message_callback_remove(sub)
    # sub       the subscription filter to match against for this callback.
    #           Only one callback may be defined per literal sub string
    # callback  the callback to be used. Takes the same form as the on_message callback.

    client.on_connect = on_connect_callback
    client.on_disconnect = on_disconnect_callback
    # client.on_subscribe = on_subscribe
    # client.on_unsubscribe = on_unsubscribe

    # flags
    client.shutdown_flag = False
    client.connected_flag = False
    client.subscribe_flag = False

    # timer
    client.heartbeat_timer = None

    return client


def mqtt_connect():
    print(f"MQTT: connecting to {HOST}:{PORT} as {USERNAME}/{CLIENT_ID}")
    MQTTClient.will_set('status/journalize/state', 'Disconnected', retain=True)
    MQTTClient.username_pw_set(username=USERNAME, password=PASSWORD)
    MQTTClient.connect_async(HOST, int(PORT))
    MQTTClient.loop_start()

    MQTTClient.heartbeat_flag = True
    heartbeat()
    return True


def mqtt_disconnect():
    print("MQTT: disconnecting...")

    if MQTTClient.heartbeat_timer:
        MQTTClient.heartbeat_timer.cancel()

    if MQTTClient.connected_flag:
        MQTTClient.disconnect()

    MQTTClient.shutdown_flag = True
    MQTTClient.loop_stop()
    return True


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


# instance -------------------------------------------------------------------
MQTTClient = initialize_client(CLIENT_ID)
