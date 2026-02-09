# Code Monolithique vers Architecture Modulaire

## Comparaison Avant/Apres

### AVANT: Code Monolithique

```
main.cpp (590 lignes)
├── Defines de configuration
├── Variables globales partout
├── Fonctions WiFi melangees
├── Fonctions MQTT melangees
├── Fonctions BLE melangees
├── Fonctions UART melangees
├── Fonctions alertes melangees
├── setup()
└── loop()
```

Problemes:

- Difficile a lire (tout dans 1 fichier)
- Difficile a maintenir (modifications risquees)
- Impossible a tester unitairement
- Code duplique entre supporters
- Ajout capteur = reecriture complete

### APRES: Architecture Modulaire

```
project/
├── include/
│   ├── Config.h              Configuration centralisee
│   ├── SensorInterface.h     Interface abstraite
│   ├── PolarH10Sensor.h      Capteur Polar
│   ├── UARTManager.h         Communication serie
│   └── ...
└── src/
    ├── main.cpp              Orchestration (150 lignes)
    ├── PolarH10Sensor.cpp    Implementation BLE
    ├── UARTManager.cpp       Implementation UART
    └── ...
```

Avantages:

- Code organise et lisible
- Chaque module independant
- Testable unitairement
- Pas de duplication
- Extension facile

## Mapping des Fonctionnalites

### Configuration

AVANT:

```cpp
// Eparpille dans le fichier
#define SUPPORTER_1
const char* ssid = "Hillary";
const char* mqtt_server = "broker.hivemq.com";
#define RX_PIN 44
#define TX_PIN 43
#define ALERT_HIGH 165
```

APRES:

```cpp
// Tout dans Config.h
namespace Config {
    const char* SUPPORTER_ID = "supporter1";
  
    namespace UART {
        const int RX_PIN = 44;
        const int TX_PIN = 43;
        const unsigned long SEND_INTERVAL = 15000;
    }
  
    namespace Alerts {
        const uint16_t HIGH = 165;
    }
}
```

Migration:

1. Copier toutes les constantes dans Config.h
2. Organiser par namespace logique
3. Supprimer les defines globaux
4. Utiliser Config::UART::RX_PIN au lieu de RX_PIN

### Gestion BLE/Polar H10

AVANT:

```cpp
// Variables globales
BLEClient* pClient = nullptr;
bool connected = false;
uint16_t currentHR = 0;

// Callbacks eparpilles
class MyClientCallback : public BLEClientCallbacks {
    void onConnect(BLEClient* pclient) {
        connected = true;
        Serial.println("Connecte");
    }
    void onDisconnect(BLEClient* pclient) {
        connected = false;
        Serial.println("Deconnecte");
    }
};

// Dans loop()
if (!connected) {
    BLEScanResults foundDevices = pBLEScan->start(5, false);
    for (int i = 0; i < foundDevices.getCount(); i++) {
        BLEAdvertisedDevice device = foundDevices.getDevice(i);
        if (device.getAddress().toString() == POLAR_MAC) {
            // Connexion manuelle...
        }
    }
}

// Reception donnees eparpillee
static void notifyCallback(BLERemoteCharacteristic* pChar, uint8_t* pData, size_t length, bool isNotify) {
    if (length >= 2) {
        currentHR = pData[1];
        // Traitement immediat...
    }
}
```

APRES:

```cpp
// Creation
PolarH10Sensor* sensor = new PolarH10Sensor(MAC_ADDRESS, DEVICE_NAME);

// Configuration callbacks
sensor->onDataReceived([](const SensorData& data) {
    Serial.print("HR: ");
    Serial.println(data.value);
    // Traitement organise
});

sensor->onStatusChanged([](bool connected) {
    if (connected) {
        Serial.println("Polar connecte");
    } else {
        Serial.println("Polar deconnecte");
    }
});

// Setup
sensor->begin();

// Loop
sensor->update();  // Gere tout automatiquement
```

Migration:

1. Supprimer toutes les variables BLE globales
2. Supprimer les callbacks BLE manuels
3. Creer instance PolarH10Sensor
4. Configurer callbacks avec lambdas
5. Appeler begin() dans setup()
6. Appeler update() dans loop()

### Gestion UART/Meshtastic

AVANT:

```cpp
// Variables globales
HardwareSerial SerialMesh(1);
uint16_t hrBuffer[50];
uint8_t bufferIndex = 0;
uint8_t bufferCount = 0;
unsigned long lastSendTime = 0;

// Fonction manuelle
void addToBuffer(uint16_t hr) {
    hrBuffer[bufferIndex] = hr;
    bufferIndex = (bufferIndex + 1) % 50;
    if (bufferCount < 50) bufferCount++;
}

uint16_t getAverage() {
    uint32_t sum = 0;
    for (uint8_t i = 0; i < bufferCount; i++) {
        sum += hrBuffer[i];
    }
    return sum / bufferCount;
}

// Dans loop()
if (millis() - lastSendTime > 15000 && bufferCount >= 15) {
    uint16_t avg = getAverage();
    String json = "{\"id\":\"supporter1\",\"hr\":" + String(avg) + "}";
    SerialMesh.println(json);
    lastSendTime = millis();
    bufferCount = 0;
    bufferIndex = 0;
}
```

APRES:

```cpp
// Creation
UARTManager* uart = new UARTManager(RX_PIN, TX_PIN, BAUD_RATE);

// Setup
uart->begin();

// Utilisation
uart->addToBuffer(heartRate);

if (uart->canSend()) {
    uint16_t avg = uart->getAverageFromBuffer();
    String timestamp = getTimestamp();
    uart->sendHeartRate(SUPPORTER_ID, avg, timestamp, messageCounter++);
    uart->clearBuffer();
}
```

Migration:

1. Supprimer variables buffer globales
2. Supprimer fonctions buffer manuelles
3. Creer instance UARTManager
4. Remplacer addToBuffer() par uart->addToBuffer()
5. Remplacer getAverage() par uart->getAverageFromBuffer()
6. Utiliser canSend() au lieu de verifier millis()
7. Utiliser sendHeartRate() pour format JSON

## Avantages Post-Migration

Avant Migration:

- main.cpp: 590 lignes
- Modification risquee
- Tests impossibles
- Duplication code

Apres Migration:

- main.cpp: 150 lignes
- Modules independants
- Tests unitaires possibles
- Aucune duplication
- Extension facile

## Conclusion

Migration vers architecture modulaire:

- Ameliore qualite code
- Facilite maintenance
- Permet evolution
- Reduit bugs
- Augmente productivite
