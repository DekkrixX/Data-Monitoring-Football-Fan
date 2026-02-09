# Organisation du Code

## Vue d'Ensemble

Le projet est organisé en 2 parties principales avec séparation claire :

1. **esp32/** : Code embarqué C++ pour microcontrôleur
2. **pc_central/** : Scripts Python pour ordinateur

## Structure Complète

```
STADE_FINAL/
├── esp32/                          Code embarqué ESP32
│   ├── include/                    Headers (.h)
│   │   ├── Config.h               Configuration centralisée
│   │   ├── SensorInterface.h      Interface abstraite capteurs
│   │   ├── PolarH10Sensor.h       Capteur Polar H10 BLE
│   │   └── UARTManager.h          Communication série
│   │
│   ├── src/                        Implémentations (.cpp)
│   │   ├── main.cpp               Point d'entrée programme
│   │   ├── PolarH10Sensor.cpp     Logique BLE Polar
│   │   └── UARTManager.cpp        Logique UART + buffer
│   │
│   ├── platformio.ini              Configuration PlatformIO
│   └── .gitignore                  Exclusions Git
│
├── pc_central/                     Scripts ordinateur
│   ├── meshtastic_to_mqtt.py      Bridge USB → MQTT
│   ├── mqtt_to_influxdb.py        Bridge MQTT → InfluxDB
│   ├── web_dashboard.py           Dashboard web Flask
│   ├── monitor_multi.py           Graphiques Matplotlib
│   │
│   ├── install_complete.sh        Script installation auto
│   └── uninstall.sh               Script désinstallation
│  
│
└── docs/                           Documentation
    ├── 1_README.md                Vue d'ensemble
    ├── 2_ARCHITECTURE.md          Architecture détaillée
    ├── 3_STRUCTURE.md             Ce fichier
    └── 4_DEBUG.md                 Guide dépannage
```

## Partie ESP32 (Code Embarqué)

### include/Config.h

**Responsabilité** : Configuration centralisée du système

**Organisation par namespaces** :

```cpp
namespace Config {
    // Sélection supporter
    #define SUPPORTER_1
    const char* SUPPORTER_ID = "supporter1";
  
    // UART/Meshtastic
    namespace UART {
        const int RX_PIN = 44;
        const int TX_PIN = 43;
        const uint32_t BAUD_RATE = 115200;
        const uint8_t NB_NODES = 1;
        const uint32_t SEND_INTERVAL = 5000 * NB_NODES;
    }
  
    // BLE/Polar H10
    namespace BLE {
        const char* HR_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb";
        const char* HR_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb";
        const int SCAN_TIME = 5;
        const uint16_t SCAN_INTERVAL = 100;
        const uint16_t SCAN_WINDOW = 99;
    }
  
    // Système
    namespace System {
        const uint32_t HEARTBEAT_INTERVAL = 60000;
        const uint16_t VALID_HR_MIN = 30;
        const uint16_t VALID_HR_MAX = 220;
    }
}
```

**Points de configuration** :

- Sélection supporter (1 seul décommenté)
- Adresse MAC Polar H10 associée
- Pins UART selon câblage
- Nombre de noeuds (intervalle automatique)

### include/SensorInterface.h

**Responsabilité** : Interface abstraite pour tous types de capteurs

**Conception orientée objet** :

```cpp
class SensorInterface {
public:
    // Méthodes virtuelles pures
    virtual bool begin() = 0;
    virtual void update() = 0;
    virtual SensorData getData() = 0;
    virtual bool isConnected() = 0;
    virtual int getRSSI() = 0;
    virtual void resetStats() = 0;
  
    // Callbacks
    void onDataReceived(std::function<void(const SensorData&)> callback);
    void onStatusChanged(std::function<void(bool)> callback);

protected:
    std::function<void(const SensorData&)> dataCallback;
    std::function<void(bool)> statusCallback;
};

// Structure de données
struct SensorData {
    uint16_t value;
    uint16_t min;
    uint16_t max;
    float average;
    uint32_t sampleCount;
    uint32_t timestamp;
    bool valid;
};
```

**Avantage** : Ajout de nouveaux capteurs facilité.

### include/PolarH10Sensor.h

**Responsabilité** : Implémentation complète du capteur Polar H10

**Architecture** :

```cpp
class PolarH10Sensor : public SensorInterface {
private:
    // BLE
    BLEClient* pClient;
    BLEScan* pBLEScan;
    BLEAdvertisedDevice* targetDevice;
  
    // État
    bool connected;
    bool doConnect;
    SensorData sensorData;
  
    // Callbacks internes (classes imbriquées)
    class AdvertisedDeviceCallbacks;
    class ClientCallbacks;
  
    // Méthodes privées
    bool connectToDevice();
    void processHeartRate(uint16_t bpm);
    static void notifyCallback(...);

public:
    PolarH10Sensor(const String& macAddress, const String& deviceName);
    ~PolarH10Sensor();
  
    // Implémentation interface
    bool begin() override;
    void update() override;
    SensorData getData() override;
    bool isConnected() override;
    int getRSSI() override;
    void resetStats() override;
};
```

**Fonctionnalités** :

- Scan BLE automatique
- Connexion/reconnexion robuste
- Subscription aux notifications
- Parsing des données Heart Rate
- Statistiques (min/max/avg)

### include/UARTManager.h

**Responsabilité** : Communication série + gestion buffer

**Architecture** :

```cpp
class UARTManager {
private:
    // Configuration
    int rxPin, txPin;
    uint32_t baudRate;
    HardwareSerial* serial;
  
    // Buffer circulaire
    static const uint8_t BUFFER_SIZE = 50;
    uint16_t hrBuffer[BUFFER_SIZE];
    uint8_t bufferIndex;
    uint8_t bufferCount;
  
    // Contrôle envoi
    uint32_t sendInterval;
    unsigned long lastSendTime;
    uint32_t sentCount;

public:
    UARTManager(int rxPin, int txPin, uint32_t baudRate);
  
    // Initialisation
    bool begin();
    void end();
  
    // Buffer
    void addToBuffer(uint16_t value);
    uint16_t getAverageFromBuffer();
    void clearBuffer();
    int getBufferCount();
    int getBufferCopy(uint16_t* outBuffer, int maxSize);
  
    // Envoi
    bool canSend();
    bool sendHeartRateBuffer(const char* id, uint32_t msgNumber);
  
    // Statistiques
    uint32_t getSentCount();
};
```

**Caractéristiques clés** :

- Buffer circulaire (pas de réallocation)
- Gestion intervalle automatique
- Formatage JSON intégré
- Accès lecture seule au buffer (debug)

### src/main.cpp

**Responsabilité** : Orchestration générale

**Structure** :

```cpp
// Variables globales
UARTManager* uartManager = nullptr;
PolarH10Sensor* heartRateSensor = nullptr;
uint32_t messageCounter = 1;
unsigned long lastHeartbeatTime = 0;

// Callbacks capteur
void onSensorDataReceived(const SensorData& data) {
    uint16_t heartRate = data.value;
  
    // Validation
    if (heartRate < Config::System::VALID_HR_MIN || 
        heartRate > Config::System::VALID_HR_MAX) {
        return;
    }
  
    // Ajout au buffer
    uartManager->addToBuffer(heartRate);
  
    // Envoi si intervalle respecté
    if (uartManager->canSend()) {
        bool success = uartManager->sendHeartRateBuffer(
            SUPPORTER_ID,
            messageCounter
        );
    
        if (success) {
            messageCounter++;
            uartManager->clearBuffer();
        }
    }
}

void onSensorStatusChanged(bool connected) {
    if (connected) {
        Serial.println("Polar H10 CONNECTÉ");
    } else {
        Serial.println("Polar H10 DÉCONNECTÉ");
    }
}

// Setup
void setup() {
    Serial.begin(115200);
  
    // Init UART
    uartManager = new UARTManager(
        Config::UART::RX_PIN,
        Config::UART::TX_PIN,
        Config::UART::BAUD_RATE
    );
    uartManager->begin();
  
    // Init capteur
    heartRateSensor = new PolarH10Sensor(POLAR_MAC_ADDRESS, POLAR_DEVICE_NAME);
    heartRateSensor->onDataReceived(onSensorDataReceived);
    heartRateSensor->onStatusChanged(onSensorStatusChanged);
    heartRateSensor->begin();
}

// Loop
void loop() {
    heartRateSensor->update();
    systemHeartbeat();  // Affichage status
    delay(1000);
}
```

**Flux** :

1. Reception BLE (1 Hz)
2. Ajout buffer
3. Envoi périodique (5-15s)
4. Incrémentation compteur

### platformio.ini

**Configuration PlatformIO** :

```ini
[env:esp32-s3-devkitc-1]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino

build_flags = 
    -Iinclude
    -DCORE_DEBUG_LEVEL=3

lib_deps = 
    bblanchon/ArduinoJson@^6.21.3
    h2zero/NimBLE-Arduino@^1.4.1

monitor_speed = 115200
upload_speed = 921600
```

**Points clés** :

- Board adaptable (changer selon ESP32)
- Dépendances automatiques
- Flags de debug configurables

## Partie PC (Scripts Python)

### meshtastic_to_mqtt.py

**Responsabilité** : Bridge USB → MQTT

**Structure** :

```python
# Configuration
SERIAL_PORT = '/dev/cu.usbmodem983DAE614B981'
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883

# Statistiques
stats = {
    'total': 0,
    'by_supporter': {},
    'errors': 0
}

# Callback réception Meshtastic
def onReceive(packet, interface):
    if 'decoded' in packet and 'text' in packet['decoded']:
        text = packet['decoded']['text']
        data = json.loads(text)
    
        supporter_id = data.get('id', 'unknown')
        hr = data.get('hr', 0)
    
        topic = f"polar/{supporter_id}/heartrate"
        mqtt_client.publish(topic, json.dumps(data))
    
        stats['total'] += 1
        stats['by_supporter'][supporter_id] = stats['by_supporter'].get(supporter_id, 0) + 1
    
        # Affichage formaté
        print_message(supporter_id, hr, stats['total'])

# Main
def main():
    mqtt_client = connect_mqtt()
    interface = meshtastic.serial_interface.SerialInterface(SERIAL_PORT)
    pub.subscribe(onReceive, "meshtastic.receive.text")
  
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_statistics()
        interface.close()
```

**Fonctionnalités** :

- Détection automatique messages TEXT_MESSAGE_APP
- Support ancien/nouveau format (rétrocompatibilité)
- Statistiques temps réel

### mqtt_to_influxdb.py

**Responsabilité** : Bridge MQTT → InfluxDB avec reconstruction

**Structure** :

```python
# Configuration
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "stade-token-123456789"
INFLUX_ORG = "football"
INFLUX_BUCKET = "heartrate"

HEART_RATE_INTERVAL = 1  # secondes entre mesures

# Traitement buffer
def process_buffer(supporter_id, hr_buffer, msg_number, base_timestamp, write_api):
    nb_values = len(hr_buffer)
  
    for i, hr_value in enumerate(hr_buffer):
        # Timestamp rétro-actif
        time_offset = (nb_values - 1 - i) * HEART_RATE_INTERVAL
        point_timestamp = base_timestamp - timedelta(seconds=time_offset)
    
        # Point InfluxDB
        point = Point("heartrate") \
            .tag("supporter", supporter_id) \
            .tag("source", "buffer") \
            .field("hr", hr_value) \
            .field("msg_number", msg_number) \
            .field("buffer_index", i) \
            .field("buffer_size", nb_values) \
            .time(point_timestamp)
    
        write_api.write(bucket=INFLUX_BUCKET, record=point)
  
    return nb_values

# Callback MQTT
def on_message(client, userdata, message):
    data = json.loads(message.payload)
    base_timestamp = datetime.utcnow()
  
    hr_data = data.get("hr", 0)
  
    if isinstance(hr_data, list):
        # Format buffer
        process_buffer(data["id"], hr_data, data["n"], base_timestamp, write_api)
    else:
        # Format ancien (compatibilité)
        write_single_value(data, base_timestamp, write_api)
```

**Caractéristiques** :

- Double format (buffer + single)
- Reconstruction précise timestamps
- Métadonnées complètes (msg_number, buffer_index)
- Écriture synchrone

### web_dashboard.py

**Responsabilité** : Dashboard web temps réel

**Structure** :

```python
# Flask + SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Stockage mémoire
class SupporterData:
    def __init__(self):
        self.times = deque(maxlen=100)
        self.values = deque(maxlen=100)
        self.stats = {'min': 999, 'max': 0, 'avg': 0, 'count': 0}
  
    def add_value(self, hr, timestamp):
        self.times.append(timestamp)
        self.values.append(hr)
        self.update_stats()

data_store = {}

# Thread MQTT
def mqtt_loop():
    client = mqtt.Client()
    client.on_message = on_mqtt_message
    client.connect('localhost', 1883)
    client.subscribe('polar/+/heartrate')
    client.loop_forever()

# Callback MQTT
def on_mqtt_message(client, userdata, message):
    data = json.loads(message.payload)
    supporter_id = data['id']
  
    # Créer supporter si nouveau
    if supporter_id not in data_store:
        data_store[supporter_id] = SupporterData()
        socketio.emit('new_supporter', {'id': supporter_id})
  
    # Traiter buffer
    if isinstance(data['hr'], list):
        base_time = datetime.now()
        for i, hr in enumerate(data['hr']):
            time_offset = len(data['hr']) - i - 1
            timestamp = base_time - timedelta(seconds=time_offset)
            data_store[supporter_id].add_value(hr, timestamp)
  
    # Broadcast WebSocket
    socketio.emit('heartrate_update', data)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return jsonify({k: v.get_dict() for k, v in data_store.items()})

# Main
if __name__ == '__main__':
    mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
    mqtt_thread.start()
    socketio.run(app, port=5001)
```

**Fonctionnalités** :

- Détection automatique supporters
- WebSocket temps réel
- API REST historique
- Templates HTML embarqués

### monitor_multi.py

**Responsabilité** : Visualisation Matplotlib adaptative

**Structure** :

```python
# Gestion données
class SupporterData:
    def __init__(self, supporter_id, color):
        self.id = supporter_id
        self.color = color
        self.times = deque(maxlen=MAX_POINTS)
        self.values = deque(maxlen=MAX_POINTS)
        self.stats = {'min': 999, 'max': 0, 'avg': 0}

class DataManager:
    def __init__(self):
        self.supporters = {}
  
    def get_or_create_supporter(self, supporter_id):
        if supporter_id not in self.supporters:
            color = COLORS[len(self.supporters) % len(COLORS)]
            self.supporters[supporter_id] = SupporterData(supporter_id, color)
        return self.supporters[supporter_id]
  
    def get_all_supporters(self):
        return list(self.supporters.values())

# Animation
def animate(frame, fig, axes):
    all_supporters = data_manager.get_all_supporters()
    nb_supporters = len(all_supporters)
  
    # Layout adaptatif
    if nb_supporters != previous_count:
        fig.clear()
        recreate_layout(nb_supporters)
  
    # Graphiques individuels
    for i, supporter in enumerate(all_supporters):
        plot_individual(supporter, axes[i])
  
    # Comparaison si 2+
    if nb_supporters >= 2:
        plot_comparison(all_supporters, axes[-1])

# Main
def main():
    fig = plt.figure(figsize=(12, 8))
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    mqtt_client.connect('localhost', 1883)
    mqtt_client.subscribe('polar/+/heartrate')
    mqtt_client.loop_start()
  
    ani = animation.FuncAnimation(fig, animate, 
                                  fargs=(fig, None),
                                  interval=1000)
    plt.show()
```

**Caractéristiques** :

- Layout dynamique (1-6 capteurs)
- Comparaison automatique
- Mise à jour 1Hz
- Rolling window 100 points

### install_complete.sh

**Responsabilité** : Installation automatique

**Structure** :

```bash
#!/bin/bash

# Détection OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
fi

# Installation Mosquitto
if [[ "$OS" == "macos" ]]; then
    brew install mosquitto
    brew services start mosquitto
else
    sudo apt install -y mosquitto mosquitto-clients
    sudo systemctl start mosquitto
fi

# Installation Docker containers
docker run -d --name influxdb \
  -p 8086:8086 \
  -v influxdb-data:/var/lib/influxdb2 \
  -e DOCKER_INFLUXDB_INIT_MODE=setup \
  -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
  -e DOCKER_INFLUXDB_INIT_PASSWORD=adminadmin \
  -e DOCKER_INFLUXDB_INIT_ORG=football \
  -e DOCKER_INFLUXDB_INIT_BUCKET=heartrate \
  -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=stade-token-123456789 \
  influxdb:2.7

docker run -d --name grafana \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana:latest

# Environnement virtuel Python
python3 -m venv stade_env
source stade_env/bin/activate
pip install --upgrade pip
pip install pyserial paho-mqtt influxdb-client meshtastic pypubsub \
            flask flask-socketio matplotlib numpy
```

**Fonctionnalités** :

- Détection OS automatique
- Installation complète services
- Environnement virtuel isolé
- Configuration initiale InfluxDB/Grafana

## Organisation Logique

### Séparation des Responsabilités

**ESP32** :

- Acquisition physique
- Traitement temps réel
- Buffering local
- Communication radio

**PC** :

- Routage messages
- Stockage persistant
- Reconstruction temporelle
- Visualisation multi-formats

### Modularité

**Ajout Supporter** :

1. Dupliquer matériel (ESP32 + Meshtastic)
2. Modifier Config.h (ID + MAC)
3. Aucune modification scripts PC (détection automatique)

**Ajout Capteur** :

1. Créer classe héritant SensorInterface
2. Implémenter méthodes virtuelles
3. Modifier main.cpp instantiation
4. Aucune modification reste système

**Ajout Métrique** :

1. Ajouter champ JSON ESP32
2. Parser dans mqtt_to_influxdb.py
3. Créer field InfluxDB
4. Ajouter panel Grafana

## Gestion des Dépendances

### ESP32 (PlatformIO)

```ini
lib_deps = 
    bblanchon/ArduinoJson@^6.21.3
    h2zero/NimBLE-Arduino@^1.4.1
```

Installation : Automatique par PlatformIO lors de `pio run`

### Python (pip)

```bash
# Installation dans environnement virtuel
source stade_env/bin/activate
pip install pyserial paho-mqtt influxdb-client meshtastic pypubsub \
            flask flask-socketio matplotlib numpy
```

Installation : Via install_complete.sh ou manuelle

## Points d'Entrée

### Compilation ESP32

```bash
cd esp32/
pio run            # Compilation
pio run -t upload  # Upload
pio device monitor # Logs série
```

### Lancement PC

```bash
cd pc_central/

# Activer environnement virtuel
source stade_env/bin/activate

# Terminal 1
python3 meshtastic_to_mqtt.py

# Terminal 2
python3 mqtt_to_influxdb.py

# Terminal 3
python3 web_dashboard.py
```

### Accès Interfaces

- Dashboard : http://localhost:5001
- Grafana : http://localhost:3000
- InfluxDB : http://localhost:8086

## Conclusion

Structure claire et modulaire facilitant :

- Compréhension rapide du code
- Maintenance et debug
- Extension fonctionnalités
- Tests unitaires
- Collaboration équipe

Séparation nette ESP32/PC permet évolution indépendante des parties.
