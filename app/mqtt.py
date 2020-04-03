import paho.mqtt.client as mqtt

broker_host = "test.mosquitto.org"
broker_port = 1883

username = "test_python_user"
password = "test_python_pass"
client_id = "PythonClient1"


def on_message(client, userdata, message):
    # print(f"topic: {message.topic}, payload: {str(message.payload.decode('utf-8'))}")
    print("message received:", str(message.payload.decode("utf-8")))
    print("message topic:", message.topic)
    print("message qos:", message.qos)
    print("message retain flag:", message.retain)


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
        print("connected OK!")
        mqtt_subscribe('+/test/status/#')
        mqtt_publish('Python/Test/status/state', 'CONNECTED; Hello, World!')
    else:
        client.connected_flag = False
        print("bad connection rc=", rc)
        client.reconnect()


def on_disconnect(client, userdata, rc):
    client.connected_flag = False
    print("disconnected, rc=", rc)
    if rc != 0:
        print("Unexpected disconnection.")
    client.reconnect()


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed:", mid)


# https://www.eclipse.org/paho/clients/python/docs/
# on_publish(client, userdata, mid)
# on_unsubscribe(client, userdata, mid)
# on_log(client, userdata, level, buf)


def initialize_client(cname):
    client = mqtt.Client(cname, False)

    # callbacks
    client.on_message = on_message
    # message_callback_add(sub, callback) / message_callback_remove(sub)
    # sub       the subscription filter to match against for this callback.
    #           Only one callback may be defined per literal sub string
    # callback  the callback to be used. Takes the same form as the on_message callback.

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    # client.on_unsubscribe = on_unsubscribe

    # flags
    client.run_flag = False
    client.connected_flag = False
    client.subscribe_flag = False

    return client


def mqtt_connect():
    # print(f"MQTT: connecting to  {broker_host}:{broker_port}")
    # MQTTClient.username_pw_set(username="test_python_user", password="test_python_pass")
    MQTTClient.connect_async(broker_host, broker_port)
    MQTTClient.loop_start()
    return None


def mqtt_disconnect():
    if MQTTClient.connected_flag:
        MQTTClient.disconnect()
    MQTTClient.loop_stop()
    return None


def mqtt_subscribe(topic: str, qos: int = 0):
    if MQTTClient.connected_flag:
        MQTTClient.subscribe(topic, qos)


def mqtt_publish(topic: str, payload: str, qos: int = 0, retain: bool = False):
    if MQTTClient.connected_flag:
        MQTTClient.publish(topic, payload, qos, retain)


# MQTTClient.username_pw_set(username="test_python_user", password="test_python_pass")
# MQTTClient.connect(host="sa100Cloud.com")
# MQTTClient.connect(broker_address)
# MQTTClient.loop_start()
# print("Subscribing to topic", "house/bulbs/bulb1")
# MQTTClient.subscribe("house/bulbs/bulb1")
# print("Publishing message to topic", "house/bulbs/bulb1")
# MQTTClient.publish("house/bulbs/bulb1", "123")
# # time.sleep(5)  # wait
# MQTTClient.loop_stop()  # stop the loop

# print("creating new instance")
# client = mqtt.Client("P1")  # create new instance
# client.on_message = mqtt_on_message  # attach function to callback
# print("connecting to broker")
# client.connect(broker_address)  # connect to broker
# client.loop_start()  # start the loop
# print("Subscribing to topic", "house/bulbs/bulb1")
# client.subscribe("house/bulbs/bulb1")
# print("Publishing message to topic", "house/bulbs/bulb1")
# client.publish("house/bulbs/bulb1", "OFF")
# time.sleep(4)  # wait
# client.loop_stop()  # stop the loop

# import time
#
# start = time.perf_counter()
# asyncio.run(main())
# elapsed = time.perf_counter() - start
# print(f"{__file__} executed in {elapsed:0.2f} seconds")

# instance
MQTTClient = initialize_client(client_id)
