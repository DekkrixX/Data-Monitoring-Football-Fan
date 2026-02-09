**# Guide de Depannage - Troubleshooting Complet

## Methodologie Generale

Principe de debug systematique:

1. Isoler le composant defaillant
2. Verifier chaque couche independamment
3. Tester avec outils simples
4. Consulter logs detailles
5. Avancer par elimination

## Arbre de Decision

```
Probleme detecte
├── ESP32 ne demarre pas
│   └── Voir section "ESP32 Hardware"
├── BLE ne connecte pas
│   └── Voir section "BLE / Polar H10"
├── Pas de messages LoRa
│   └── Voir section "Meshtastic"
├── PC ne recoit rien
│   └── Voir section "Scripts Python"
├── Donnees non stockees
│   └── Voir section "InfluxDB"
└── Dashboard ne s'affiche pas
    └── Voir section "Visualisation"
```

## ESP32 - Hardware et Firmware

### ESP32 ne demarre pas

Symptomes:

- Aucun LED
- Pas de sortie Serial Monitor
- Upload impossible

Verifications:

```bash
# 1. Verifier connexion USB
ls /dev/cu.usbmodem* # macOS
ls /dev/ttyUSB* # Linux

# 2. Verifier driver CH340/CP2102 installe

# 3. Tester avec sketch basique
# File > Examples > 01.Basics > Blink

# 4. Verifier alimentation
# Mesurer 3.3V et 5V avec multimetre

# 5. Verifier bouton BOOT
# Maintenir BOOT pendant upload si necessaire
```

Solutions:

- Cable USB defectueux -> Changer cable
- Driver manquant -> Installer CH340/CP2102
- Carte endommagee -> Remplacer ESP32
- Mauvais port -> Essayer autre port USB

### ESP32 demarre mais pas de logs

Symptomes:

- LED ESP32 allumee
- Upload reussi
- Serial Monitor vide

Verifications:

```bash
# 1. Verifier baud rate Serial Monitor
# Doit etre 115200

# 2. Verifier Serial.begin() dans code
Serial.begin(115200);

# 3. Tester avec code minimal
void setup() {
    Serial.begin(115200);
    delay(2000);
    Serial.println("Test");
}

# 4. Verifier cable USB supporte data
# Certains cables sont charge only
```

Solutions:

- Mauvais baud rate -> 115200
- Serial.begin() manquant -> Ajouter
- Cable charge only -> Cable data
- Buffer Serial plein -> Redemarrer

### Erreurs de compilation

Erreur: Config.h not found

```bash
# Solution: Ajouter dans platformio.ini
build_flags = -Iinclude
```

Erreur: undefined reference

```bash
# Solution: Verifier .cpp dans src/
# PlatformIO compile automatiquement tous .cpp dans src/
```

Erreur: multiple definition

```bash
# Solution: Ne pas implementer fonctions dans .h
# Utiliser 'inline' ou deplacer dans .cpp
```

## BLE / Polar H10

### Polar H10 non detecte

Symptomes:

- ESP32 scan indefiniment
- Jamais de connexion
- Message "Searching..."

Verifications:

```cpp
// 1. Verifier adresse MAC correcte
#define POLAR_MAC_ADDRESS "c5:58:19:6c:3f:b2"  // Minuscules!

// 2. Activer logs debug BLE
void setup() {
    Serial.begin(115200);
    BLEDevice::init("");
  
    // Scanner actif
    BLEScan* pBLEScan = BLEDevice::getScan();
    BLEScanResults scanResults = pBLEScan->start(5);
  
    // Afficher tous devices detectes
    for (int i = 0; i < scanResults.getCount(); i++) {
        BLEAdvertisedDevice device = scanResults.getDevice(i);
        Serial.print("Found: ");
        Serial.print(device.getAddress().toString().c_str());
        Serial.print(" RSSI: ");
        Serial.println(device.getRSSI());
    }
}

// 3. Verifier Polar H10 actif
// - LED doit clignoter
// - Bande mouillée (contact peau)
// - Pile chargee (> 3V)
```

Solutions:

- MAC incorrecte -> Verifier avec scan
- Polar eteint -> Activer (contact peau)
- Pile faible -> Remplacer pile CR2025
- Trop loin -> Distance < 10m
- Interference -> Eloigner WiFi/Bluetooth
- Deja connecte -> Deconnecter app Polar

### Connexion instable

Symptomes:

- Connexion puis deconnexion rapide
- RSSI faible
- Donnees intermittentes

Verifications:

```cpp
// Afficher RSSI
void onDataReceived(const SensorData& data) {
    Serial.print("HR: ");
    Serial.print(data.value);
    Serial.print(" RSSI: ");
    Serial.println(sensor->getRSSI());
}

// RSSI interpretation:
// > -60 dBm: Excellent
// -60 a -70: Bon
// -70 a -80: Moyen
// < -80: Faible (problemes attendus)
```

Solutions:

- RSSI faible -> Reduire distance
- Obstacles metal -> Repositionner
- Batterie faible ESP32 -> Recharger
- Interference -> Changer canal WiFi
- Bande seche -> Mouiller electrodes

### Donnees incorrectes

Symptomes:

- HR = 0 ou 255
- HR oscillations extremes
- HR non realist

e (> 220)

Verifications:

```cpp
// Verifier parsing donnees
static void notifyCallback(BLERemoteCharacteristic* pChar, 
                          uint8_t* pData, 
                          size_t length, 
                          bool isNotify) {
    // Debug raw data
    Serial.print("Length: ");
    Serial.print(length);
    Serial.print(" Data: ");
    for (size_t i = 0; i < length; i++) {
        Serial.print(pData[i], HEX);
        Serial.print(" ");
    }
    Serial.println();
  
    // Format Polar H10:
    // Byte 0: Flags
    // Byte 1: HR value (si flags & 0x01 == 0)
    // Byte 1-2: HR value (si flags & 0x01 == 1)
}
```

Solutions:

- Parsing incorrect -> Verifier format
- Contact peau mauvais -> Mouiller
- Mouvement excessif -> Stabiliser
- Bande mal positionnee -> Reajuster

## UART / Meshtastic

### Pas de transmission UART

Symptomes:

- ESP32 envoie (logs) mais Meshtastic ne recoit pas
- Meshtastic --listen vide

Verifications:

```bash
# 1. Verifier cablage
# ESP32 TX (43) -> Meshtastic RX
# ESP32 RX (44) -> Meshtastic TX
# ESP32 GND -> Meshtastic GND

# 2. Verifier baud rate identique
# ESP32: 115200
# Meshtastic: 115200 (config serial)

# 3. Test loopback ESP32
# Connecter TX et RX ensemble
# Ce qui est envoye doit etre recu

# 4. Test Meshtastic reception
meshtastic --port /dev/cu.usbmodem* --seriallog

# 5. Verifier config Meshtastic serial
meshtastic --port /dev/cu.usbmodem* --set serial.enabled true
meshtastic --port /dev/cu.usbmodem* --set serial.mode SIMPLE
meshtastic --port /dev/cu.usbmodem* --set serial.baud 115200
```

Solutions:

- Cablage inverse -> TX->RX croise
- GND non connecte -> Connecter GND
- Baud rate different -> Unifier 115200
- Serial desactive -> Activer config
- Niveau tension -> Verifier 3.3V

### Messages corrompus

Symptomes:

- JSON incomplet
- Caracteres bizarres
- Parse error

Verifications:

```cpp
// Verifier envoi complet
uart->sendHeartRate(id, hr, ts, n);
delay(100);  // Attendre transmission complete

// Verifier format JSON
String json = "{\"id\":\"supporter1\",\"hr\":73,\"ts\":\"14:32:15\",\"n\":42}";
Serial.println(json);  // Preview avant envoi
```

Solutions:

- Buffer UART plein -> Augmenter buffer
- Envoi trop rapide -> Ajouter delay
- Caracteres speciaux -> Eviter accents
- Baud rate trop eleve -> Reduire si longues distances

## Meshtastic / LoRa

### Pas de reception Gateway

Symptomes:

- ESP32 envoie UART (verifie)
- Meshtastic terrain transmet (LED)
- Gateway ne recoit rien

Verifications:

```bash
# 1. Verifier config radio identique
meshtastic --port /dev/cu.usbmodem* --info

# Verifier:
# - Region: EU_868 (les 2)
# - Preset: LONG_FAST ou identique
# - Channel: Default ou meme custom

# 2. Test portee
# Commencer proche (< 10m)
# Augmenter progressivement

# 3. Verifier SNR et RSSI
meshtastic --port /dev/cu.usbmodem* --listen
# SNR > 0: Bon signal
# SNR < -10: Signal faible
# RSSI > -100: Acceptable
```

Solutions:

- Regions differentes -> Unifier EU_868
- Presets differents -> Meme preset
- Trop loin -> Reduire distance
- Obstacles -> Ligne de vue
- Interference -> Changer canal

### Duty cycle depasse

Symptomes:

- Messages perdus
- Transmissions sautees
- Warning duty cycle

Verifications:

```cpp
// Calculer duty cycle
// ToA (Time on Air) ~250ms pour 60 bytes
// Intervalle actuel
const unsigned long interval = 15000;  // 15s

// Duty cycle = (ToA / interval) * 100
// = (0.25 / 15) * 100 = 1.67%

// Legal EU: < 1% par heure
// Safe: < 10% instantane
```

Solutions:

- Intervalle trop court -> Augmenter (20s)
- Trop de capteurs -> Reduire nombre
- Messages trop longs -> Reduire payload
- Retransmissions -> Desactiver ACK

## Scripts Python

### Script ne demarre pas

Symptomes:

- ImportError modules
- Permission denied port serie
- Connection refused MQTT/InfluxDB

Verifications:

```bash
# 1. Verifier modules installes
pip list | grep meshtastic
pip list | grep paho-mqtt
pip list | grep influxdb

# 2. Installer manquants
pip install meshtastic pypubsub paho-mqtt influxdb-client

# macOS
pip install --break-system-packages meshtastic pypubsub paho-mqtt influxdb-client

# 3. Verifier permissions port
ls -l /dev/cu.usbmodem*
# Si necessaire:
sudo chmod 666 /dev/cu.usbmodem*

# 4. Verifier services actifs
# Mosquitto
brew services list | grep mosquitto
# InfluxDB
docker ps | grep influxdb
```

Solutions:

- Module manquant -> Installer
- Permission port -> chmod ou sudo
- Mosquitto arrete -> brew services start
- InfluxDB arrete -> docker start influxdb

### meshtastic_to_mqtt.py erreurs

Erreur: Port not found

```bash
# Verifier port existe
ls /dev/cu.usbmodem*

# Si multiple ports, identifier le bon
meshtastic --port /dev/cu.usbmodem* --info

# Mettre a jour dans script
SERIAL_PORT = '/dev/cu.usbmodem983DAE614B981'
```

Erreur: MQTT connection refused

```bash
# Verifier Mosquitto actif
brew services list | grep mosquitto

# Tester connexion
mosquitto_sub -h localhost -t "#" -v

# Redemarrer si necessaire
brew services restart mosquitto
```

### mqtt_to_influxdb.py erreurs

Erreur: 401 Unauthorized

```bash
# Token invalide ou expire
# Recuperer nouveau token:
# 1. Ouvrir http://localhost:8086
# 2. Login admin/adminadmin
# 3. Load Data > API Tokens
# 4. Copier token
# 5. Mettre a jour dans script
INFLUX_TOKEN = "nouveau-token-ici"
```

Erreur: 404 Bucket not found

```bash
# Creer bucket
docker exec influxdb influx bucket create \
  --name heartrate \
  --org football \
  --token VOTRE_TOKEN

# Ou via UI:
# http://localhost:8086 > Load Data > Buckets > Create Bucket
```

## InfluxDB

### Container ne demarre pas

```bash
# Verifier Docker actif
docker ps

# Verifier logs
docker logs influxdb

# Redemarrer
docker restart influxdb

# Recréer si corrompu
docker stop influxdb
docker rm influxdb
# Relancer install_pc.sh
```

### Donnees non visibles

```bash
# Verifier bucket
docker exec influxdb influx bucket list --org football

# Verifier donnees
docker exec influxdb influx query '
  from(bucket:"heartrate")
    |> range(start:-1h)
    |> limit(n:10)
' --org football

# Si vide, verifier mqtt_to_influxdb.py actif
```

## Dashboard Web

### Page blanche

Verifications:

```bash
# 1. Verifier Flask actif
# Chercher erreurs dans terminal Python

# 2. Verifier port
# Par defaut 5001 (5000 occupe par AirPlay macOS)

# 3. Tester URL
curl http://localhost:5001

# 4. Verifier templates existent
ls pc_central/templates/
# Doit contenir: index.html, supporter.html, comparaison.html
```

Solutions:

- Flask crash -> Voir erreur terminal
- Port occupe -> Changer WEB_PORT
- Templates manquants -> Copier templates/
- Firewall -> Autoriser port 5001

### Graphiques ne se mettent pas a jour

Verifications:

```bash
# 1. Verifier WebSocket connecte
# Console navigateur (F12) > Network > WS

# 2. Verifier MQTT actif dans script
# Doit voir thread mqtt_loop actif

# 3. Verifier donnees arrivent
mosquitto_sub -h localhost -t "polar/+/heartrate" -v

# 4. Verifier console JavaScript
# F12 > Console
# Chercher erreurs JavaScript
```

Solutions:

- WebSocket failed -> Reinstaller flask-socketio
- MQTT thread crash -> Redemarrer script
- JavaScript error -> Vider cache navigateur
- Donnees non recues -> Verifier chaine complete

## Grafana

### Cannot connect to InfluxDB

Verifications:

```bash
# 1. Tester connexion InfluxDB
curl http://localhost:8086/health

# 2. Verifier token Grafana
# Settings > Data Sources > InfluxDB > Token

# 3. Verifier URL correcte
# http://localhost:8086 (pas https)

# 4. Verifier organisation et bucket
# football et heartrate
```

### No data in graph

Verifications:

```flux
# Tester requete directement dans InfluxDB UI
from(bucket: "heartrate")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "heartrate")
  |> filter(fn: (r) => r._field == "hr")
  |> limit(n: 10)

# Si vide:
# - Verifier mqtt_to_influxdb.py actif
# - Verifier donnees arrivent sur MQTT
```

## Outils de Debug

### Logs Serie ESP32

```bash
# PlatformIO
pio device monitor

# Avec filtre
pio device monitor | grep "HR:"
```

### MQTT Monitor

```bash
# Tout voir
mosquitto_sub -h localhost -t "#" -v

# Topic specifique
mosquitto_sub -h localhost -t "polar/supporter1/heartrate" -v

# Avec timestamp
mosquitto_sub -h localhost -t "#" -v | ts
```

### Meshtastic Debug

```bash
# Info device
meshtastic --port /dev/cu.usbmodem* --info

# Listen messages
meshtastic --port /dev/cu.usbmodem* --listen

# Serial log
meshtastic --port /dev/cu.usbmodem* --seriallog

# Envoyer test
meshtastic --port /dev/cu.usbmodem* --sendtext "Test message"
```

### InfluxDB Query

```bash
# Via CLI
docker exec influxdb influx query '
  from(bucket:"heartrate")
    |> range(start:-10m)
    |> filter(fn: (r) => r._measurement == "heartrate")
' --org football

# Via UI
# http://localhost:8086 > Explore > Entrer requete Flux
```

## Checklist Complete Systeme Fonctionnel

```
[ ] ESP32 demarre et affiche logs
[ ] ESP32 connecte Polar H10 BLE
[ ] ESP32 recoit FC toutes les secondes
[ ] ESP32 envoie JSON via UART
[ ] Meshtastic recoit UART (seriallog)
[ ] Meshtastic transmet LoRa (LED)
[ ] Gateway recoit LoRa (--listen)
[ ] Gateway transmet USB vers PC
[ ] meshtastic_to_mqtt.py recoit et affiche
[ ] Messages apparaissent sur MQTT
[ ] mqtt_to_influxdb.py ecrit dans DB
[ ] Donnees visibles dans InfluxDB
[ ] Dashboard web affiche graphiques
[ ] Grafana affiche donnees historiques
[ ] Systeme stable pendant 5 minutes
```

## Ressources Supplementaires

Documentation officielle:

- ESP32: https://docs.espressif.com
- Meshtastic: https://meshtastic.org/docs
- InfluxDB: https://docs.influxdata.com
- Grafana: https://grafana.com/docs
- Polar H10: https://www.polar.com/en/sensors/h10

Forums support:

- ESP32: https://esp32.com
- Meshtastic: https://meshtastic.discourse.group
- PlatformIO: https://community.platformio.org

## Conclusion

Debug systematique:

1. Isoler composant defaillant
2. Tester independamment
3. Verifier logs detailles
4. Consulter cette doc
5. Demander aide si bloque

s
