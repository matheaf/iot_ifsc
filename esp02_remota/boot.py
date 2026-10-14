# boot.py - Executado na inicialização do ESP32
import gc
import network
import time

gc.collect()

WIFI_SSID = "ESP32_MQTT_Net"
WIFI_PASS = "senha_super_segura"

def conecta_wifi(ssid, senha):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print(f"Conectando à rede Wi-Fi '{ssid}'...", end="")
        sta_if.active(True)
        sta_if.connect(ssid, senha)
        
        tentativas = 0
        while not sta_if.isconnected() and tentativas < 30:
            print(".", end="")
            time.sleep(0.5)
            tentativas += 1

    if sta_if.isconnected():
        print("\nWi-Fi Conectado!")
        print("Configuração de Rede (IP/Masc/GW/DNS):", sta_if.ifconfig())
    else:
        print("\nFalha ao conectar no Wi-Fi do ESP32 Broker.")

conecta_wifi(WIFI_SSID, WIFI_PASS)
