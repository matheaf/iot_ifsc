# main.py - Cliente MicroPython conectado ao ESP32 Broker
import time
import network
from machine import Pin, time_pulse_us
import dht
from umqtt.simple import MQTTClient
import json

# Periféricos
sensor_dht = dht.DHT22(Pin(15))
trigger = Pin(4, Pin.OUT)
echo = Pin(2, Pin.IN)
led_actuator = Pin(23, Pin.OUT)

# Configurações do Broker Local (ESP32 #1)
MQTT_BROKER       = "192.168.4.1" # IP fixo do AP do ESP32 Broker
MQTT_CLIENT_ID    = "esp32_micropython_client"
MQTT_TOPIC_DATA   = "sensores/temperatura"
MQTT_TOPIC_JSON   = "sensores/telemetria"
MQTT_TOPIC_CMD    = "sensores/comando"

WIFI_SSID = "ESP32_MQTT_Net"
WIFI_PASS = "senha_super_segura"

def ao_receber_comando(topic, msg):
    comando = msg.decode("utf-8").strip().upper()
    print(f"Comando MQTT recebido: {comando}")
    if comando == "ON":
        led_actuator.value(1)
        print("LED GPIO 23 -> LIGADO")
    elif comando == "OFF":
        led_actuator.value(0)
        print("LED GPIO 23 -> DESLIGADO")

client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=1883, keepalive=60)
client.set_callback(ao_receber_comando)

def conectar_mqtt():
    while True:
        try:
            print("Conectando ao Broker MQTT no ESP32...")
            client.connect()
            client.subscribe(MQTT_TOPIC_CMD)
            print(f"Inscrito em [{MQTT_TOPIC_CMD}] com sucesso!")
            return
        except Exception as e:
            print(f"Falha MQTT: {e}. Tentando em 3s...")
            time.sleep(3)

def garante_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Wi-Fi caiu! Reconectando...")
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASS)
        while not sta_if.isconnected():
            time.sleep(0.5)

garante_wifi()
conectar_mqtt()

def ler_distancia_cm():
    trigger.value(0)
    time.sleep_us(2)
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)
    duracao = time_pulse_us(echo, 1, 30000)
    if duracao < 0:
        return 15.0
    dist = (duracao * 0.0343) / 2
    return round(min(max(dist, 0.0), 15.0), 1)

tempo_ultima_leitura = 0

while True:
    try:
        garante_wifi()
        
        # Checa mensagens MQTT recebidas do supervisório
        client.check_msg()

        # Envia telemetria a cada 2 segundos
        if time.time() - tempo_ultima_leitura >= 2:
            sensor_dht.measure()
            temp = sensor_dht.temperature()
            umi = sensor_dht.humidity()
            dist = ler_distancia_cm()

            # Envia a temperatura isolada para o card principal do supervisório
            client.publish(MQTT_TOPIC_DATA, str(temp))

            # Envia o JSON completo com todos os sensores
            payload = json.dumps({
                "temperatura": temp,
                "umidade": umi,
                "distancia_cm": dist
            })
            client.publish(MQTT_TOPIC_JSON, payload)

            print(f"Publicado -> Temp: {temp}°C | Umid: {umi}% | Dist: {dist}cm")
            tempo_ultima_leitura = time.time()

    except OSError as e:
        print(f"Erro de socket ({e}). Reconectando...")
        try:
            client.disconnect()
        except:
            pass
        conectar_mqtt()

    except Exception as e:
        print("Erro geral:", e)

    time.sleep_ms(50)
