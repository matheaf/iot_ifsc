#include <WiFi.h>
#include <PicoMQTT.h>
#include <WebServer.h>
#include <ArduinoJson.h>

const char* ssid = "ESP32_MQTT_Net";
const char* password = "senha_super_segura";

PicoMQTT::Server broker;
WebServer server(80);

// Variáveis numéricas para a telemetria do MicroPython
float valTemp = 0.0;
float valUmi = 0.0;
float valDist = 15.0; // Distância (representará o nível do tanque: 0 a 15 cm)
String statusAtuador = "OFF";

const char HTML_DASHBOARD[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Supervisório - INTERNET DAS COISAS</title>
  <style>
    /* Estilo Neutro ISA-101 (Cinza Industrial) */
    body {
      font-family: "Segoe UI", Arial, sans-serif;
      background-color: #c0c0c0;
      color: #000;
      margin: 0;
      padding: 15px;
      user-select: none;
    }

    h2 {
      margin: 5px 0 15px 0;
      font-size: 1.2em;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #111;
      border-bottom: 2px solid #808080;
      padding-bottom: 5px;
      text-align: left;
    }

    /* Process Display Workspace */
    .scada-container {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      justify-content: flex-start;
      align-items: flex-start;
    }

    /* Painel do Tanque de Processo */
    .pandid-section {
      background-color: #d8d8d8;
      border: 2px solid #808080;
      padding: 15px;
      border-radius: 4px;
      box-shadow: inset 1px 1px 0px #fff, inset -1px -1px 0px #777;
      position: relative;
    }

    /* Desenho do Tanque ISA-101 */
    .tank-wrapper {
      position: relative;
      width: 160px;
      height: 220px;
      border: 3px solid #333;
      border-radius: 20px / 10px;
      background: #e5e5e5;
      overflow: hidden;
      margin: 0 auto;
    }

    .tank-liquid {
      position: absolute;
      bottom: 0;
      width: 100%;
      height: 50%; /* Dinâmico via JS */
      background: #89b4db; /* Azul suave neutro ISA */
      transition: height 0.5s ease-in-out;
      border-top: 2px solid #205080;
    }

    .tank-label {
      position: absolute;
      top: 10px;
      width: 100%;
      text-align: center;
      font-weight: bold;
      font-size: 0.9em;
      color: #222;
      z-index: 2;
    }

    /* Medidores Verticais (Bar Gauges estilo ISA-101) */
    .bar-gauge-container {
      display: flex;
      gap: 25px;
      background: #d8d8d8;
      border: 2px solid #808080;
      padding: 15px;
      border-radius: 4px;
    }

    .bar-gauge {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 50px;
    }

    .bar-track {
      width: 20px;
      height: 180px;
      background: #b0b0b0;
      border: 2px solid #555;
      position: relative;
      margin: 8px 0;
    }

    .bar-fill {
      position: absolute;
      bottom: 0;
      width: 100%;
      background: #4a7ebb;
      height: 0%;
      transition: height 0.5s;
    }

    .bar-val {
      font-weight: bold;
      font-size: 1.1em;
      color: #000080; /* Azul Marinho Processo */
    }

    /* Tabela de Dados Numéricos ISA */
    .data-panel {
      background: #d8d8d8;
      border: 2px solid #808080;
      padding: 10px;
      font-family: monospace;
      font-size: 0.95em;
      min-width: 220px;
    }

    .data-row {
      display: flex;
      justify-content: space-between;
      padding: 4px 0;
      border-bottom: 1px solid #b0b0b0;
    }

    .data-title { font-weight: bold; color: #333; }
    .data-value { font-weight: bold; color: #000080; }

    /* Painel de Controle de Atuador */
    .control-panel {
      background: #d8d8d8;
      border: 2px solid #808080;
      padding: 15px;
      border-radius: 4px;
      margin-top: 15px;
      display: inline-block;
      min-width: 280px;
      text-align: left;
    }

    .btn-isa {
      background: #c0c0c0;
      border: 2px solid;
      border-color: #fff #666 #666 #fff;
      padding: 8px 18px;
      font-weight: bold;
      cursor: pointer;
      font-size: 0.9em;
      margin-right: 10px;
    }

    .btn-isa:active {
      border-color: #666 #fff #fff #666;
    }

    /* Linha de Status de Alarme */
    .status-bar {
      margin-top: 15px;
      background: #b0b0b0;
      border: 1px solid #777;
      padding: 5px 10px;
      font-size: 0.85em;
      color: #222;
      text-align: left;
    }
  </style>
</head>
<body>

  <h2>Supervisório - INTERNET DAS COISAS</h2>

  <div class="scada-container">
    
    <!-- Representação Gráfica do Tanque (P&ID) -->
    <div class="pandid-section">
      <div style="font-weight: bold; margin-bottom: 8px; font-size: 0.9em;">Reservatório 01</div>
      <div class="tank-wrapper">
        <div class="tank-label">Nível Proc.</div>
        <div id="tankLiquid" class="tank-liquid"></div>
      </div>
      <div style="margin-top: 8px;" class="bar-val" id="tankVal">-- cm</div>
    </div>

    <!-- Indicadores Analógicos por Coluna (Bar Gauges ISA) -->
    <div class="bar-gauge-container">
      
      <!-- Barra de Temperatura -->
      <div class="bar-gauge">
        <span style="font-size: 0.8em; font-weight: bold;">TEMP</span>
        <div class="bar-track">
          <div id="tempBar" class="bar-fill" style="background: #4a7ebb;"></div>
        </div>
        <span class="bar-val" id="tempDisp">--</span>
        <span style="font-size: 0.7em;">°C</span>
      </div>

      <!-- Barra de Umidade -->
      <div class="bar-gauge">
        <span style="font-size: 0.8em; font-weight: bold;">UMID</span>
        <div class="bar-track">
          <div id="umiBar" class="bar-fill" style="background: #5b9bd5;"></div>
        </div>
        <span class="bar-val" id="umiDisp">--</span>
        <span style="font-size: 0.7em;">%</span>
      </div>

    </div>

    <!-- Painel com Registros de Valores -->
    <div class="data-panel">
      <div style="font-weight: bold; border-bottom: 2px solid #555; padding-bottom: 4px; margin-bottom: 6px;">VARIÁVEIS DE PROCESSO</div>
      <div class="data-row">
        <span class="data-title">Temp. Ambiente:</span>
        <span class="data-value" id="textTemp">-- °C</span>
      </div>
      <div class="data-row">
        <span class="data-title">Umid. Relativa:</span>
        <span class="data-value" id="textUmi">-- %</span>
      </div>
      <div class="data-row">
        <span class="data-title">Nível Ultrassônico:</span>
        <span class="data-value" id="textDist">-- cm</span>
      </div>
      <div class="data-row">
        <span class="data-title">Bomba/Atuador (P-101):</span>
        <span class="data-value" id="textAtuador">OFF</span>
      </div>
    </div>

  </div>

  <!-- Painel de Controle de Operação -->
  <div class="control-panel">
    <div style="font-weight: bold; font-size: 0.85em; margin-bottom: 10px;">COMANDO DE PROCESSO (BOMBA P-101)</div>
    <button class="btn-isa" onclick="enviarComando('ON')">START (ON)</button>
    <button class="btn-isa" onclick="enviarComando('OFF')">STOP (OFF)</button>
  </div>

  <div id="statusBar" class="status-bar">Status: Conectando ao controlador de processo...</div>

  <script>
    function atualizar() {
      fetch('/api/dados')
        .then(res => res.json())
        .then(data => {
          let temp = parseFloat(data.temp) || 0;
          let umi = parseFloat(data.umi) || 0;
          let dist = parseFloat(data.dist) || 0;

          // Atualiza Textos
          document.getElementById("textTemp").innerText = temp.toFixed(1) + " °C";
          document.getElementById("textUmi").innerText = umi.toFixed(1) + " %";
          document.getElementById("textDist").innerText = dist.toFixed(1) + " cm";
          document.getElementById("tempDisp").innerText = temp.toFixed(0);
          document.getElementById("umiDisp").innerText = umi.toFixed(0);
          document.getElementById("tankVal").innerText = dist.toFixed(1) + " cm";

          // Nível do Tanque (Distância de 0 a 15 cm invertida para Simular Nível)
          let nivelPct = Math.max(0, Math.min(100, ((15 - dist) / 15) * 100));
          document.getElementById("tankLiquid").style.height = nivelPct + "%";

          // Percentual das Barras de Indicador
          let tempPct = Math.max(0, Math.min(100, (temp / 50) * 100)); // Escala 0 a 50°C
          let umiPct = Math.max(0, Math.min(100, umi));                // Escala 0 a 100%
          
          document.getElementById("tempBar").style.height = tempPct + "%";
          document.getElementById("umiBar").style.height = umiPct + "%";

          document.getElementById("statusBar").innerText = "Status: Operação Normal | Última atualização: " + new Date().toLocaleTimeString();
        })
        .catch(err => {
          document.getElementById("statusBar").innerText = "Status: FALHA DE COMUNICAÇÃO COM O BROKER";
        });
    }

    function enviarComando(cmd) {
      fetch('/api/comando?val=' + cmd)
        .then(() => {
          document.getElementById("textAtuador").innerText = cmd;
        });
    }

    setInterval(atualizar, 1000);
  </script>
</body>
</html>
)rawliteral";

void setup() {
  Serial.begin(115200);

  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();

  Serial.println("\n--- BROKER SCADA ISA-101 INICIADO ---");
  Serial.print("Acesse o Supervisório em: http://");
  Serial.println(IP);

  // Escuta o JSON completo publicado pelo MicroPython
  broker.subscribe("sensores/telemetria", [](const char* topic, const char* payload) {
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload);
    if (!error) {
      valTemp = doc["temperatura"].as<float>();
      valUmi = doc["umidade"].as<float>();
      valDist = doc["distancia_cm"].as<float>();
    }
  });

  broker.begin();

  // Rota HTTP do Dashboard ISA-101
  server.on("/", []() {
    server.send(200, "text/html", HTML_DASHBOARD);
  });

  // API JSON para o Front-end
  server.on("/api/dados", []() {
    String json = "{\"temp\":\"" + String(valTemp) + "\",\"umi\":\"" + String(valUmi) + "\",\"dist\":\"" + String(valDist) + "\"}";
    server.send(200, "application/json", json);
  });

  // Envia comando MQTT ao MicroPython
  server.on("/api/comando", []() {
    if (server.hasArg("val")) {
      String cmd = server.arg("val");
      broker.publish("sensores/comando", cmd.c_str());
      Serial.print("Comando ISA publicado: ");
      Serial.println(cmd);
    }
    server.send(200, "text/plain", "OK");
  });

  server.begin();
}

void loop() {
  broker.loop();
  server.handleClient();
}
