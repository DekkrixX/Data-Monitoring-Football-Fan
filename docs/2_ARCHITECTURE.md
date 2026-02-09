# Architecture Technique Détaillée

## Vue d'Ensemble

Le système suit une architecture en couches avec séparation claire des responsabilités.

## Diagramme Complet

```
COUCHE PHYSIQUE (Stade)
├── Polar H10 (BLE) → ESP32 (traitement) → Meshtastic (LoRa)
└── Portée radio : 2-5 km

COUCHE TRANSPORT (Sans fil)
├── LoRa 868 MHz
├── Duty cycle : < 10% légal
└── Gateway Meshtastic (réception)

COUCHE TRAITEMENT (PC Local - localhost)
├── USB → meshtastic_to_mqtt.py → Mosquitto (port 1883)
├── Mosquitto → mqtt_to_influxdb.py → InfluxDB (port 8086)
└── Mosquitto → web_dashboard.py → Navigateur (port 5001)

COUCHE VISUALISATION
├── Dashboard Web Flask (temps réel, WebSocket)
└── Grafana (historique, analyse)
```

## Couche 1 : ESP32 (Acquisition)

### Responsabilités

- Connexion BLE avec Polar H10
- Réception FC toutes les secondes
- Buffer circulaire de valeurs
- Transmission UART format JSON

### Architecture Modulaire

```
include/
├── Config.h           : Configuration centralisée
├── SensorInterface.h  : Interface abstraite capteurs
├── PolarH10Sensor.h   : Implémentation Polar H10
└── UARTManager.h      : Gestion communication série

src/
├── main.cpp           : Orchestration principale
├── PolarH10Sensor.cpp : Logique BLE
└── UARTManager.cpp    : Logique UART + buffer
```

### Flux de Données

```
1. Polar H10 notification BLE (1 Hz)
2. PolarH10Sensor parse et callback
3. main.cpp ajoute au buffer UART
4. Après intervalle respecté : envoi buffer complet
5. Format JSON: {"id":"supporter1", "hr":[68,70,72,71,69], "n":42}
6. Envoi UART 115200 baud
```

### Gestion du Buffer

**Caractéristiques** :

- Buffer circulaire (pas de réallocation)
- Taille adaptée à l'intervalle d'envoi
- Toutes les valeurs conservées

## Couche 2 : Meshtastic (Radio LoRa)

### Protocole

- **Fréquence** : 868 MHz (EU868)
- **Modulation** : LoRa SF7-12
- **Puissance** : 20 dBm (100 mW)
- **Time on Air** : ~220ms par message (50 bytes)

### Format Paquet

```
Meshtastic Packet
├── Header (From, To, ID, Hop)
├── Payload (JSON texte)
└── Metadata (SNR, RSSI, timestamp)
```

### Gestion Duty Cycle

**Contrainte EU868** : 10% maximum (36 secondes/heure)

**Calcul** :

```
ToA = 220ms = 0.22s par message
Messages max/heure = 36s / 0.22s = 163 messages
Messages max/minute = 163 / 60 ≈ 12 messages
```

**Stratégie** : Distribuer les 12 messages/minute entre les noeuds

```cpp
const uint32_t SEND_INTERVAL = 5000 * NB_NODES;  // ms

// 1 noeud  : 5s  → 12 msg/min total
// 2 noeuds : 10s → 6×2 = 12 msg/min total
// 3 noeuds : 15s → 4×3 = 12 msg/min total
```

## Couche 3 : PC Scripts Python

### Script 1 : meshtastic_to_mqtt.py

**Rôle** : Pont USB → MQTT

**Fonctionnalités** :

- Détection automatique du port série
- Parse protobuf Meshtastic
- Extraction JSON du payload
- Publication MQTT avec topic dynamique

### Script 2 : mqtt_to_influxdb.py

**Rôle** : Pont MQTT → InfluxDB avec reconstruction timestamps

**Caractéristiques** :

- Subscribe à `polar/+/heartrate` (wildcard)
- Traite buffers ET valeurs uniques (compatibilité)
- Reconstruction temporelle précise
- Écriture synchrone pour garantir ordre

**Exemple de Reconstruction** :

```
Message reçu à 14:04:10 avec buffer [68, 70, 72, 71, 69]

Point 1 : 14:04:06 → 68 BPM  (T - 4 secondes)
Point 2 : 14:04:07 → 70 BPM  (T - 3 secondes)
Point 3 : 14:04:08 → 72 BPM  (T - 2 secondes)
Point 4 : 14:04:09 → 71 BPM  (T - 1 seconde)
Point 5 : 14:04:10 → 69 BPM  (T - 0 seconde)
```

### Script 3 : web_dashboard.py

**Rôle** : Interface web temps réel

**Fonctionnalités** :

- Détection automatique des supporters
- WebSocket pour mise à jour temps réel
- API REST pour données historiques
- Templates HTML embarqués

### Script 4 : monitor_multi.py

**Rôle** : Visualisation Matplotlib avec détection dynamique

**Caractéristiques** :

- Layout adaptatif
- Comparaison automatique si 2+ capteurs
- Mise à jour 1Hz
- Buffer 100 points

## Couche 4 : Stockage (InfluxDB)

### Schéma de Données

**Measurement** : `heartrate`

**Tags** (indexés) :

- `supporter` : ID du supporter (supporter1, supporter2, ...)
- `source` : Origine des données (`buffer` ou `single`)

**Fields** :

- `hr` : Fréquence cardiaque (integer)
- `msg_number` : Numéro de message (integer)
- `buffer_index` : Position dans le buffer (integer)
- `buffer_size` : Taille du buffer original (integer)

**Timestamp** : Nanoseconds epoch UTC

### Requête Flux Typique

```flux
from(bucket: "heartrate")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "heartrate")
  |> filter(fn: (r) => r.supporter == "supporter1")
  |> filter(fn: (r) => r._field == "hr")
  |> filter(fn: (r) => r.source == "buffer")
```

### Avantages du Schéma

- **Traçabilité** : `msg_number` et `buffer_index` permettent reconstruction
- **Filtrage** : Tag `source` sépare ancien/nouveau format
- **Analyse** : `buffer_size` indique densité de données
- **Performance** : Tags indexés pour requêtes rapides

## Couche 5 : Visualisation

### Dashboard Web (Flask)

**Technologies** :

- Backend : Flask + SocketIO
- Frontend : HTML + Chart.js + Socket.IO client
- Mise à jour : Temps réel via WebSocket

**Pages** :

- `/` : Accueil avec cartes dynamiques
- `/supporter/<id>` : Dashboard individuel
- `/comparaison` : Graphique comparé
- `/api/data` : API REST données

### Grafana

**Configuration Source de Données** :

```
Type     : InfluxDB (Flux)
URL      : http://localhost:8086
Org      : football
Token    : stade-token-123456789
Bucket   : heartrate
```

**Panels Types** :

- Time series : Courbes FC
- Stat : Valeurs actuelles
- Table : Historique détaillé
- Gauge : Indicateurs visuels

**Variables** :

```
supporter : from(bucket:"heartrate") |> distinct(column: "supporter")
timerange : -5m, -15m, -1h, -6h, -24h
```

## Communication Localhost

### Principe

Tous les services communiquent via `localhost` :

- Aucune sortie réseau externe
- Communication inter-process (IPC)
- Latence minimale
- Sécurité maximale

### Ports Utilisés


| Service   | Port | Protocole | Usage                   |
| --------- | ---- | --------- | ----------------------- |
| Mosquitto | 1883 | MQTT      | Broker messages         |
| InfluxDB  | 8086 | HTTP      | API base de données    |
| Grafana   | 3000 | HTTP      | Interface visualisation |
| Dashboard | 5001 | HTTP/WS   | Dashboard web           |


## Gestion des Pannes

### Reconnexion Automatique

**BLE** :

```cpp
void PolarH10Sensor::update() {
    if (!connected) {
        // Scan automatique toutes les 3 secondes
        if (millis() - lastScanTime > 3000) {
            BLEScanResults results = pBLEScan->start(scanTime, false);
            // Connexion si trouvé
        }
    }
}
```

**MQTT** :

```python
def on_disconnect(client, userdata, rc):
    print("Déconnecté. Reconnexion...")
    while True:
        try:
            client.reconnect()
            break
        except:
            time.sleep(5)
```

**InfluxDB** :

```python
try:
    write_api.write(bucket=INFLUX_BUCKET, record=point)
except InfluxDBError as e:
    print(f"Erreur InfluxDB : {e}")
    # Reconnexion automatique à la prochaine écriture
```

### Tolérance aux Pannes

**Perte BLE** :

- Détection : Callback `onDisconnect`
- Récupération : Scan automatique < 30s
- Impact : Perte temporaire de données

**Perte LoRa** :

- Détection : Absence de messages
- Récupération : Aucune (fire-and-forget)
- Impact : Trous dans les données

**Crash Script Python** :

- Détection : Supervision externe recommandée
- Récupération : Redémarrage manuel
- Impact : Perte pendant arrêt

## Sécurité

### Données Locales

- Tout reste sur `localhost`
- Aucune sortie Internet
- Accès limité à la machine locale

### Authentification

- InfluxDB : Token requis
- Grafana : Login + password
- Dashboard Web : Aucune (localhost)
- MQTT : Aucune (localhost)

### Recommandations Production

- Activer authentification MQTT si accès réseau
- Configurer firewall pour limiter accès ports
- Chiffrer communications si multi-machines
- Sauvegarder régulièrement InfluxDB

## Conclusion

Architecture en 5 couches bien séparées :

1. **Acquisition** : ESP32 modulaire, buffer circulaire
2. **Transport** : LoRa avec gestion duty cycle
3. **Traitement** : Scripts Python spécialisés
4. **Stockage** : InfluxDB time-series optimisé
5. **Visualisation** : Multi-interfaces (Web, Grafana, Matplotlib)

Points forts :

- Modularité et séparation des responsabilités
- Robustesse (reconnexions automatiques)
- Évolutivité (ajout capteurs facilité)
- Performance (latence <500ms bout-en-bout)
