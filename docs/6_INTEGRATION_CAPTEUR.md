# Intégration de Nouveaux Capteurs

## Vue d'Ensemble

L'intégration d'un nouveau capteur suit une méthodologie standardisée en 7 étapes. Le principe fondamental est : **un capteur = une classe autonome** communiquant avec le système via des interfaces standardisées.

## Architecture Modulaire

### Principe de Conception

```
[Capteur A] ────┐
[Capteur B] ────┼──> [Gestionnaire] ──> [Transmission] ──> [Stockage]
[Capteur C] ────┘
```

**Avantages** :

- **Isolation** : Une erreur sur un capteur n'affecte pas les autres
- **Réutilisabilité** : Code écrit une fois, utilisable partout
- **Évolutivité** : Ajout sans refonte du code existant
- **Testabilité** : Test indépendant avant intégration

## Étape 1 : Analyse du Capteur

### Types d'Interface Physique

**Analogique** : Tension variable 0-3.3V mesurée par ADC

- Simple mais moins précis
- Exemples : photorésistance, potentiomètre

**I2C** : Protocole numérique 2 fils (SDA, SCL)

- Adressage multiple capteurs sur même bus
- Exemples : accéléromètres, capteurs de pression

**SPI** : Protocole numérique 4 fils (MOSI, MISO, SCK, CS)

- Plus rapide que I2C
- Exemples : cartes SD, écrans TFT

**UART** : Série 2 fils (TX, RX)

- Communication point à point
- Exemples : GPS, modules GSM

**1-Wire** : Un seul fil pour données et alimentation

- Exemples : DS18B20 (température)

### Questions Clés

1. Quelle interface de communication?
2. Quelle tension d'alimentation?
3. Quelle fréquence de mesure?
4. Quel format de données?
5. Quelle précision requise?

## Étape 2 : Conception de la Classe

### Structure Standard

```cpp
class MonCapteur {
private:
    // Configuration
    int pin;
    uint8_t adresse;
  
    // État interne
    float valeur;
    bool initialized;
  
    // Buffers
    float buffer[10];

public:
    // Constructeur
    MonCapteur(int pin, uint8_t adresse);
  
    // Initialisation
    bool begin();
  
    // Mise à jour
    void update();
  
    // Accesseurs
    float getValue();
    bool isReady();
  
    // Export
    String getJSON();
};
```

### Méthodes Essentielles

**Constructeur** : Stockage paramètres (pas d'accès matériel)

```cpp
MonCapteur::MonCapteur(int pin, uint8_t adresse) 
    : pin(pin), adresse(adresse), valeur(0), initialized(false) {
    // Initialisation variables uniquement
}
```

**begin()** : Initialisation matérielle

```cpp
bool MonCapteur::begin() {
    // Configuration pins
    pinMode(pin, INPUT);
  
    // Initialisation bus (I2C, SPI, etc.)
    Wire.begin();
  
    // Vérification présence capteur
    if (!checkPresence()) {
        return false;
    }
  
    // Configuration paramètres
    configure();
  
    initialized = true;
    return true;
}
```

**update()** : Lecture périodique (appelée dans loop)

```cpp
void MonCapteur::update() {
    if (!initialized) return;
  
    // Lecture capteur
    valeur = readSensor();
  
    // Traitement (filtrage, calibration)
    valeur = filter(valeur);
}
```

**getJSON()** : Export données standardisé

```cpp
String MonCapteur::getJSON() {
    JsonDocument doc;
    doc["type"] = "mon_capteur";
    doc["id"] = SENSOR_ID;  // ID du capteur (pas de supporter)
    doc["valeur"] = valeur;
    doc["unite"] = "unité";
    doc["n"] = messageCounter;
  
    String output;
    serializeJson(doc, output);
    return output;
}
```

## Étape 3 : Création du Fichier Header

### Emplacement

```
esp32/
  └── include/
      ├── Config.h
      ├── PolarH10Sensor.h
      ├── UARTManager.h
      └── MonCapteur.h          <-- Nouveau fichier
```

### Structure Fichier

```cpp
#ifndef MON_CAPTEUR_H
#define MON_CAPTEUR_H

#include <Arduino.h>
#include <Wire.h>  // Si I2C

class MonCapteur {
private:
    // Variables privées
    int pin;
    float valeur;
  
    // Méthodes privées
    float readSensor();
    bool checkPresence();

public:
    // Constructeur
    MonCapteur(int pin);
  
    // Méthodes publiques
    bool begin();
    void update();
    float getValue();
    String getJSON();
};

#endif
```

### Implémentation

```cpp
// Si simple, dans le même fichier .h
// Si complexe, créer MonCapteur.cpp dans src/

MonCapteur::MonCapteur(int pin) : pin(pin), valeur(0) {}

bool MonCapteur::begin() {
    pinMode(pin, INPUT);
    return true;
}

void MonCapteur::update() {
    valeur = analogRead(pin) * 3.3 / 4095.0;
}

float MonCapteur::getValue() {
    return valeur;
}

String MonCapteur::getJSON() {
    return "{\"type\":\"mon_capteur\",\"id\":\"" + String(SENSOR_ID) + 
           "\",\"valeur\":" + String(valeur) + "}";
}
```

## Étape 4 : Intégration dans main.cpp

### Inclusion

```cpp
#include <Arduino.h>
#include "Config.h"
#include "PolarH10Sensor.h"
#include "UARTManager.h"
#include "MonCapteur.h"        // Ajout
```

### Déclaration Globale

```cpp
// Objets globaux
PolarH10Sensor* heartRateSensor = nullptr;
UARTManager* uartManager = nullptr;
MonCapteur* monCapteur = nullptr;    // Ajout
```

### Initialisation dans setup()

```cpp
void setup() {
    Serial.begin(115200);
    delay(2000);
  
    // Initialisation UART
    uartManager = new UARTManager(RX_PIN, TX_PIN, BAUD_RATE);
    uartManager->begin();
  
    // Initialisation capteurs existants
    heartRateSensor = new PolarH10Sensor(MAC, NAME);
    heartRateSensor->begin();
  
    // Initialisation nouveau capteur
    monCapteur = new MonCapteur(GPIO_PIN);
    if (monCapteur->begin()) {
        Serial.println("[CAPTEUR] Initialisé");
    } else {
        Serial.println("[CAPTEUR] ERREUR initialisation");
    }
}
```

### Utilisation dans loop()

**Option 1 : Transmission séparée**

```cpp
void loop() {
    // Mise à jour capteurs
    heartRateSensor->update();
    monCapteur->update();
  
    // Transmission indépendante
    if (shouldSendMonCapteur()) {
        String json = monCapteur->getJSON();
        uartManager->send(json);
    }
  
    delay(1000);
}
```

**Option 2 : Transmission groupée**

```cpp
void loop() {
    heartRateSensor->update();
    monCapteur->update();
  
    if (shouldSendAll()) {
        // JSON combiné
        JsonDocument doc;
        doc["hr"] = heartRateSensor->getData().value;
        doc["capteur"] = monCapteur->getValue();
      
        String output;
        serializeJson(doc, output);
        uartManager->send(output);
    }
  
    delay(1000);
}
```

## Étape 5 : Compilation et Tests

### Compilation

```bash
cd esp32/
pio run
```

**Erreurs Courantes** :

- `'MonCapteur' was not declared` → Include manquant
- `undefined reference` → Implémentation manquante
- `no matching function` → Mauvais paramètres

### Upload

```bash
pio run -t upload
```

### Monitoring

```bash
pio device monitor

# Sortie attendue :
# [CAPTEUR] Initialisé
# [CAPTEUR] Valeur : 23.5
# [CAPTEUR] Données envoyées
```

## Étape 6 : Réception PC

### Script Python

```python
#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from datetime import datetime

# Configuration
MQTT_BROKER = 'localhost'
MQTT_TOPIC = 'polar/+/capteur'

INFLUX_URL = 'http://localhost:8086'
INFLUX_TOKEN = 'stade-token-123456789'
INFLUX_ORG = 'football'
INFLUX_BUCKET = 'capteurs'

# Client InfluxDB
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
      
        if data.get('type') == 'mon_capteur':
            point = Point("mon_capteur") \
                .tag("supporter", data.get('id', 'unknown')) \
                .field("valeur", float(data.get('valeur', 0))) \
                .field("unite", data.get('unite', '')) \
                .time(datetime.utcnow())
          
            write_api.write(bucket=INFLUX_BUCKET, record=point)
          
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"{data['id']} : {data['valeur']} {data.get('unite', '')}")
          
    except Exception as e:
        print(f"[ERREUR] {e}")

def main():
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, 1883, 60)
    mqtt_client.subscribe(MQTT_TOPIC)
  
    print("[CAPTEUR] En écoute...")
    mqtt_client.loop_forever()

if __name__ == "__main__":
    main()
```

### Lancement

```bash
cd pc_central/
source stade_env/bin/activate
python3 mon_capteur_to_influxdb.py
```

## Étape 7 : Visualisation Grafana

### Création Panel

1. Ouvrir Grafana : http://localhost:3000
2. Créer ou ouvrir dashboard
3. Add panel
4. Configurer requête

### Requête Flux

```flux
from(bucket: "capteurs")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "mon_capteur")
  |> filter(fn: (r) => r._field == "valeur")
  |> filter(fn: (r) => r.supporter == "supporter1")
```

### Types de Visualisation

**Time series** : Évolution temporelle (température, humidité)
**Gauge** : Valeur instantanée avec seuils (niveau batterie)
**Stat** : Nombre simple avec évolution (dernière valeur)
**Table** : Données tabulaires (logs, historique)
**Geomap** : Positions GPS
**Heatmap** : Densités (caméra thermique)

## Exemple Complet : Accéléromètre MPU6050 (I2C)

### Contexte d'Utilisation

Contrairement au système de monitoring cardiaque des supporters, ce capteur peut servir à :

- Détecter les mouvements/vibrations du stade
- Mesurer l'activité physique d'un objet (ballon équipé)
- Analyser les impacts lors d'entraînements
- Surveiller la stabilité d'équipements

**Chaque capteur possède un ID unique** au lieu d'un ID de supporter.

### Hardware

**Capteur** : MPU6050 (accéléromètre + gyroscope 6 axes)
**Interface** : I2C
**Connexions** :

- VCC → 3.3V
- GND → GND
- SDA → GPIO21 (ESP32)
- SCL → GPIO22 (ESP32)

**Adresse I2C** : 0x68 (par défaut)

### Implémentation Complète

**Fichier : include/MPU6050Sensor.h**

```cpp
#ifndef MPU6050_SENSOR_H
#define MPU6050_SENSOR_H

#include <Arduino.h>
#include <Wire.h>
#include <ArduinoJson.h>

// Registres MPU6050
#define MPU6050_ADDR      0x68
#define MPU6050_PWR_MGMT  0x6B
#define MPU6050_ACCEL_X   0x3B
#define MPU6050_GYRO_X    0x43
#define MPU6050_WHO_AM_I  0x75

class MPU6050Sensor {
private:
    // Identifiant du capteur
    String sensorId;
  
    // Données brutes
    int16_t ax, ay, az;  // Accélération (raw)
    int16_t gx, gy, gz;  // Gyroscope (raw)
  
    // Données converties
    float accelX, accelY, accelZ;  // en g
    float gyroX, gyroY, gyroZ;     // en °/s
  
    // État
    bool initialized;
    uint32_t lastUpdate;
    uint32_t messageCounter;
  
    // Configuration
    static const float ACCEL_SCALE = 16384.0;  // ±2g
    static const float GYRO_SCALE = 131.0;     // ±250°/s
  
    /**
     * Écrire dans un registre MPU6050
     */
    void writeRegister(uint8_t reg, uint8_t value) {
        Wire.beginTransmission(MPU6050_ADDR);
        Wire.write(reg);
        Wire.write(value);
        Wire.endTransmission();
    }
  
    /**
     * Lire un registre 16 bits
     */
    int16_t readRegister16(uint8_t reg) {
        Wire.beginTransmission(MPU6050_ADDR);
        Wire.write(reg);
        Wire.endTransmission(false);
        Wire.requestFrom(MPU6050_ADDR, 2);
      
        if (Wire.available() >= 2) {
            int16_t value = Wire.read() << 8 | Wire.read();
            return value;
        }
        return 0;
    }
  
    /**
     * Vérifier présence du capteur
     */
    bool checkPresence() {
        Wire.beginTransmission(MPU6050_ADDR);
        Wire.write(MPU6050_WHO_AM_I);
        Wire.endTransmission(false);
        Wire.requestFrom(MPU6050_ADDR, 1);
      
        if (Wire.available()) {
            uint8_t whoAmI = Wire.read();
            return (whoAmI == 0x68);
        }
        return false;
    }

public:
    /**
     * Constructeur
     * @param sensorId Identifiant unique du capteur (ex: "accel_01")
     */
    MPU6050Sensor(const String& sensorId) 
        : sensorId(sensorId),
          ax(0), ay(0), az(0),
          gx(0), gy(0), gz(0),
          accelX(0), accelY(0), accelZ(0),
          gyroX(0), gyroY(0), gyroZ(0),
          initialized(false),
          lastUpdate(0),
          messageCounter(1) {
    }
  
    /**
     * Initialisation du capteur
     */
    bool begin() {
        Serial.println("[MPU6050] Initialisation...");
      
        // Initialiser I2C
        Wire.begin();
        Wire.setClock(400000);  // 400kHz
      
        delay(100);
      
        // Vérifier présence
        if (!checkPresence()) {
            Serial.println("[MPU6050] ERREUR : Capteur non détecté");
            return false;
        }
      
        Serial.println("[MPU6050] Capteur détecté (WHO_AM_I = 0x68)");
      
        // Réveiller le MPU6050 (sort du mode sleep)
        writeRegister(MPU6050_PWR_MGMT, 0x00);
        delay(100);
      
        // Configuration :
        // - Accéléromètre : ±2g
        // - Gyroscope : ±250°/s
        // - Filtre passe-bas : 94Hz
        writeRegister(0x1C, 0x00);  // ACCEL_CONFIG (±2g)
        writeRegister(0x1B, 0x00);  // GYRO_CONFIG (±250°/s)
        writeRegister(0x1A, 0x02);  // CONFIG (DLPF 94Hz)
      
        delay(100);
      
        initialized = true;
        Serial.println("[MPU6050] Initialisé avec succès");
        Serial.print("[MPU6050] ID capteur : ");
        Serial.println(sensorId);
      
        return true;
    }
  
    /**
     * Mise à jour des données (à appeler dans loop)
     */
    void update() {
        if (!initialized) return;
      
        // Lire accéléromètre (6 registres)
        ax = readRegister16(MPU6050_ACCEL_X);
        ay = readRegister16(MPU6050_ACCEL_X + 2);
        az = readRegister16(MPU6050_ACCEL_X + 4);
      
        // Lire gyroscope (6 registres)
        gx = readRegister16(MPU6050_GYRO_X);
        gy = readRegister16(MPU6050_GYRO_X + 2);
        gz = readRegister16(MPU6050_GYRO_X + 4);
      
        // Conversion en unités physiques
        accelX = ax / ACCEL_SCALE;
        accelY = ay / ACCEL_SCALE;
        accelZ = az / ACCEL_SCALE;
      
        gyroX = gx / GYRO_SCALE;
        gyroY = gy / GYRO_SCALE;
        gyroZ = gz / GYRO_SCALE;
      
        lastUpdate = millis();
    }
  
    /**
     * Obtenir accélération X (en g)
     */
    float getAccelX() const { return accelX; }
  
    /**
     * Obtenir accélération Y (en g)
     */
    float getAccelY() const { return accelY; }
  
    /**
     * Obtenir accélération Z (en g)
     */
    float getAccelZ() const { return accelZ; }
  
    /**
     * Obtenir magnitude de l'accélération
     */
    float getAccelMagnitude() const {
        return sqrt(accelX*accelX + accelY*accelY + accelZ*accelZ);
    }
  
    /**
     * Obtenir rotation X (en °/s)
     */
    float getGyroX() const { return gyroX; }
  
    /**
     * Obtenir rotation Y (en °/s)
     */
    float getGyroY() const { return gyroY; }
  
    /**
     * Obtenir rotation Z (en °/s)
     */
    float getGyroZ() const { return gyroZ; }
  
    /**
     * Vérifier si initialisé
     */
    bool isInitialized() const { return initialized; }
  
    /**
     * Obtenir dernière mise à jour (timestamp)
     */
    uint32_t getLastUpdate() const { return lastUpdate; }
  
    /**
     * Export JSON pour transmission
     */
    String getJSON() {
        JsonDocument doc;
      
        doc["type"] = "mpu6050";
        doc["id"] = sensorId;
        doc["n"] = messageCounter++;
      
        // Accéléromètre (en g)
        JsonObject accel = doc["accel"].to<JsonObject>();
        accel["x"] = round(accelX * 1000) / 1000.0;  // 3 décimales
        accel["y"] = round(accelY * 1000) / 1000.0;
        accel["z"] = round(accelZ * 1000) / 1000.0;
        accel["mag"] = round(getAccelMagnitude() * 1000) / 1000.0;
      
        // Gyroscope (en °/s)
        JsonObject gyro = doc["gyro"].to<JsonObject>();
        gyro["x"] = round(gyroX * 10) / 10.0;  // 1 décimale
        gyro["y"] = round(gyroY * 10) / 10.0;
        gyro["z"] = round(gyroZ * 10) / 10.0;
      
        String output;
        serializeJson(doc, output);
        return output;
    }
  
    /**
     * Affichage debug
     */
    void printValues() {
        Serial.print("[MPU6050] Accel (g): X=");
        Serial.print(accelX, 3);
        Serial.print(" Y=");
        Serial.print(accelY, 3);
        Serial.print(" Z=");
        Serial.print(accelZ, 3);
        Serial.print(" | Gyro (°/s): X=");
        Serial.print(gyroX, 1);
        Serial.print(" Y=");
        Serial.print(gyroY, 1);
        Serial.print(" Z=");
        Serial.println(gyroZ, 1);
    }
};

#endif
```

### Configuration

**Fichier : include/Config.h**

```cpp
#ifndef CONFIG_H
#define CONFIG_H

// =====================================================
// CONFIGURATION CAPTEUR
// =====================================================

// ID unique du capteur (à personnaliser)
#define SENSOR_ID "accel_01"  // ou "accel_02", "accel_ballon", etc.

// =====================================================
// CONFIGURATION I2C
// =====================================================
namespace Config {
    namespace I2C {
        const int SDA_PIN = 21;
        const int SCL_PIN = 22;
        const uint32_t FREQUENCY = 400000;  // 400kHz
    }

    // =====================================================
    // CONFIGURATION UART/MESHTASTIC
    // =====================================================
    namespace UART {
        const int RX_PIN = 44;
        const int TX_PIN = 43;
        const uint32_t BAUD_RATE = 115200;
        const uint32_t SEND_INTERVAL = 5000;  // 5 secondes
    }
  
    // =====================================================
    // SYSTÈME
    // =====================================================
    namespace System {
        const uint32_t HEARTBEAT_INTERVAL = 60000;  // 1 minute
    }
}

#endif
```

### Intégration main.cpp

**Fichier : src/main.cpp**

```cpp
#include <Arduino.h>
#include "Config.h"
#include "MPU6050Sensor.h"
#include "UARTManager.h"

// ═══════════════════════════════════════════════════════
// OBJETS GLOBAUX
// ═══════════════════════════════════════════════════════

MPU6050Sensor* accelerometer = nullptr;
UARTManager* uartManager = nullptr;

unsigned long lastSendTime = 0;
unsigned long lastHeartbeatTime = 0;

// ═══════════════════════════════════════════════════════
// FONCTIONS UTILITAIRES
// ═══════════════════════════════════════════════════════

void printBanner() {
    Serial.println("\n╔════════════════════════════════════════════╗");
    Serial.println("║    SYSTÈME MONITORING ACCÉLÉROMÈTRE        ║");
    Serial.println("║         MPU6050 + Meshtastic               ║");
    Serial.println("╚════════════════════════════════════════════╝");
    Serial.println();
    Serial.print("Capteur ID   : ");
    Serial.println(SENSOR_ID);
    Serial.print("I2C SDA/SCL  : GPIO ");
    Serial.print(Config::I2C::SDA_PIN);
    Serial.print(" / GPIO ");
    Serial.println(Config::I2C::SCL_PIN);
    Serial.print("UART TX/RX   : GPIO ");
    Serial.print(Config::UART::TX_PIN);
    Serial.print(" / GPIO ");
    Serial.println(Config::UART::RX_PIN);
    Serial.print("Intervalle   : ");
    Serial.print(Config::UART::SEND_INTERVAL / 1000);
    Serial.println(" secondes");
    Serial.println("════════════════════════════════════════════\n");
}

void systemHeartbeat() {
    unsigned long now = millis();
  
    if (now - lastHeartbeatTime >= Config::System::HEARTBEAT_INTERVAL) {
        lastHeartbeatTime = now;
      
        Serial.println("\n╔═══════════════════════════════════════════╗");
        Serial.print("║  STATUS - ");
        Serial.print(SENSOR_ID);
        Serial.println("                        ║");
        Serial.println("╠═══════════════════════════════════════════╣");
      
        Serial.print("║    Uptime        : ");
        Serial.print(now / 1000 / 60);
        Serial.println(" minutes           ║");
      
        if (accelerometer->isInitialized()) {
            Serial.println("║  ✓ MPU6050 Actif                          ║");
            Serial.print("║   Dernière MAJ  : ");
            Serial.print((now - accelerometer->getLastUpdate()) / 1000);
            Serial.println(" s ago         ║");
        } else {
            Serial.println("║  ✗ MPU6050 Inactif                        ║");
        }
      
        Serial.print("║   Messages UART : ");
        Serial.print(uartManager->getSentCount());
        Serial.println("                    ║");
      
        Serial.println("╚═══════════════════════════════════════════╝\n");
    }
}

// ═══════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════

void setup() {
    Serial.begin(115200);
    delay(2000);
  
    printBanner();
  
    // Initialisation UART
    Serial.println("[1/2] Initialisation UART/Meshtastic...");
    uartManager = new UARTManager(
        Config::UART::RX_PIN,
        Config::UART::TX_PIN,
        Config::UART::BAUD_RATE
    );
  
    if (uartManager->begin()) {
        Serial.println("       ✓ UART OK");
    } else {
        Serial.println("       ✗ ERREUR UART");
    }
  
    Serial.println();
  
    // Initialisation MPU6050
    Serial.println("[2/2] Initialisation MPU6050...");
    accelerometer = new MPU6050Sensor(SENSOR_ID);
  
    if (accelerometer->begin()) {
        Serial.println("       ✓ MPU6050 OK");
    } else {
        Serial.println("       ✗ ERREUR MPU6050");
    }
  
    Serial.println();
    Serial.println("════════════════════════════════════════════");
    Serial.println(" ✓ INITIALISATION TERMINÉE");
    Serial.println(" Envoi des données toutes les 5 secondes...");
    Serial.println("════════════════════════════════════════════");
    Serial.println();
}

// ═══════════════════════════════════════════════════════
// LOOP
// ═══════════════════════════════════════════════════════

void loop() {
    // Mise à jour capteur
    if (accelerometer->isInitialized()) {
        accelerometer->update();
      
        // Affichage debug (toutes les secondes)
        static unsigned long lastDebug = 0;
        if (millis() - lastDebug >= 1000) {
            lastDebug = millis();
            accelerometer->printValues();
        }
    }
  
    // Envoi périodique via UART
    unsigned long now = millis();
    if (now - lastSendTime >= Config::UART::SEND_INTERVAL) {
        lastSendTime = now;
      
        if (accelerometer->isInitialized()) {
            String json = accelerometer->getJSON();
          
            Serial.println("\n┌──────────────────────────────────────┐");
            Serial.println("│  ENVOI MESHTASTIC                    │");
            Serial.println("├──────────────────────────────────────┤");
            Serial.print("│ ");
            Serial.print(json);
            Serial.println();
            Serial.println("└──────────────────────────────────────┘\n");
          
            uartManager->send(json);
        }
    }
  
    // Heartbeat système
    systemHeartbeat();
  
    delay(100);  // 100ms
}
```

### Format JSON Transmis

```json
{
  "type": "mpu6050",
  "id": "accel_01",
  "n": 142,
  "accel": {
    "x": 0.012,
    "y": -0.034,
    "z": 1.003,
    "mag": 1.004
  },
  "gyro": {
    "x": -1.2,
    "y": 0.8,
    "z": 0.3
  }
}
```

### Script Python Réception

**Fichier : pc_central/mpu6050_to_influxdb.py**

```python
#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from datetime import datetime

# Configuration
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPICS = ['sensors/+/mpu6050']

INFLUX_URL = 'http://localhost:8086'
INFLUX_TOKEN = 'stade-token-123456789'
INFLUX_ORG = 'football'
INFLUX_BUCKET = 'sensors'

# Client InfluxDB
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Statistiques
stats = {
    'total': 0,
    'by_sensor': {},
    'errors': 0
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✓ Connecté au broker MQTT : {MQTT_BROKER}:{MQTT_PORT}")
        for topic in MQTT_TOPICS:
            client.subscribe(topic)
            print(f"  ✓ Abonné : {topic}")
        print("\n✓ En attente des données MPU6050...\n")
    else:
        print(f"✗ Erreur connexion MQTT (code {rc})")

def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())
      
        if data.get('type') == 'mpu6050':
            sensor_id = data.get('id', 'unknown')
            msg_number = data.get('n', 0)
          
            # Extraire données
            accel = data.get('accel', {})
            gyro = data.get('gyro', {})
          
            # Point InfluxDB pour accéléromètre
            point_accel = Point("mpu6050_accel") \
                .tag("sensor", sensor_id) \
                .field("x", float(accel.get('x', 0))) \
                .field("y", float(accel.get('y', 0))) \
                .field("z", float(accel.get('z', 0))) \
                .field("magnitude", float(accel.get('mag', 0))) \
                .field("msg_number", msg_number) \
                .time(datetime.utcnow())
          
            # Point InfluxDB pour gyroscope
            point_gyro = Point("mpu6050_gyro") \
                .tag("sensor", sensor_id) \
                .field("x", float(gyro.get('x', 0))) \
                .field("y", float(gyro.get('y', 0))) \
                .field("z", float(gyro.get('z', 0))) \
                .field("msg_number", msg_number) \
                .time(datetime.utcnow())
          
            # Écriture
            write_api.write(bucket=INFLUX_BUCKET, record=[point_accel, point_gyro])
          
            # Statistiques
            stats['total'] += 1
            stats['by_sensor'][sensor_id] = stats['by_sensor'].get(sensor_id, 0) + 1
          
            # Affichage
            now = datetime.now().strftime('%H:%M:%S')
            print(f"[{now}] #{stats['total']:04d} | {sensor_id:12s} : "
                  f"Accel({accel['x']:+.3f}, {accel['y']:+.3f}, {accel['z']:+.3f})g "
                  f"Gyro({gyro['x']:+.1f}, {gyro['y']:+.1f}, {gyro['z']:+.1f})°/s "
                  f"→ InfluxDB ✓")
          
    except json.JSONDecodeError as e:
        stats['errors'] += 1
        print(f"  [ERREUR] JSON invalide : {e}")
    except Exception as e:
        stats['errors'] += 1
        print(f"  [ERREUR] {e}")

def main():
    print("\n" + "="*70)
    print("  BRIDGE : MQTT → InfluxDB (MPU6050)")
    print("="*70 + "\n")
  
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
  
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("  ARRÊT DU BRIDGE")
        print("="*70 + "\n")
        print(f"Messages traités : {stats['total']}")
        print(f"Erreurs          : {stats['errors']}")
        if stats['by_sensor']:
            print("\nRépartition par capteur :")
            for sensor, count in sorted(stats['by_sensor'].items()):
                print(f"  {sensor:15s} : {count:4d} messages")
        mqtt_client.disconnect()
        influx_client.close()
        print("\n✓ Déconnexion propre\n")

if __name__ == "__main__":
    main()
```

### Requêtes Grafana

**Accélération (magnitude)**

```flux
from(bucket: "sensors")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "mpu6050_accel")
  |> filter(fn: (r) => r._field == "magnitude")
  |> filter(fn: (r) => r.sensor == "accel_01")
```

**Rotation (axe Z)**

```flux
from(bucket: "sensors")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "mpu6050_gyro")
  |> filter(fn: (r) => r._field == "z")
  |> filter(fn: (r) => r.sensor == "accel_01")
```

**Tous les axes accélération**

```flux
from(bucket: "sensors")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "mpu6050_accel")
  |> filter(fn: (r) => r._field == "x" or r._field == "y" or r._field == "z")
  |> filter(fn: (r) => r.sensor == "accel_01")
```

## Considérations Importantes

### Gestion de l'Intervalle d'Envoi

**Problème** : Trop de capteurs surchargent le réseau LoRa

**Solution** : Adapter l'intervalle

### Gestion de la Mémoire

**Problème** : ESP32 a une RAM limitée

**Solution** : Libérer ressources

```cpp
// Dans loop()
if (sensor->hasFailed()) {
    delete sensor;
    sensor = nullptr;
}
```

### Gestion des Erreurs

**Toujours vérifier** :

```cpp
if (!sensor->begin()) {
    Serial.println("[ERREUR] Capteur non initialisé");
    // Désactiver capteur
    delete sensor;
    sensor = nullptr;
}

// Dans loop()
if (sensor != nullptr) {
    sensor->update();
}
```

## Méthodologie Récapitulative

### Checklist d'Intégration

```
[ ] Étape 1 : Analyser capteur (interface, specs)
[ ] Étape 2 : Concevoir classe (méthodes standard)
[ ] Étape 3 : Créer fichier header (include/)
[ ] Étape 4 : Intégrer main.cpp (include, global, setup, loop)
[ ] Étape 5 : Compiler et tester (pio run, upload, monitor)
[ ] Étape 6 : Script Python réception (MQTT → InfluxDB)
[ ] Étape 7 : Dashboard Grafana (requête Flux, panels)
[ ] Validation : Test bout-en-bout 15 minutes
```

### Points Clés

**Isolation** : Chaque capteur indépendant
**Standardisation** : Mêmes méthodes (begin, update, getJSON)
**Robustesse** : Gestion systématique erreurs
**Documentation** : Code commenté, logs explicites

## Conclusion

L'architecture modulaire garantit :

- Code maintenable et évolutif
- Facilité de debug
- Réutilisabilité des composants
- Robustesse du système global

Avec cette méthodologie, l'intégration d'un nouveau capteur devient une opération standardisée et fiable.
