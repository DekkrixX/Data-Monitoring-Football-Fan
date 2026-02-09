# Système de Monitoring Cardiaque pour Supporters de Football

## Vue d'ensemble

Ce projet permet de monitorer en temps reel la frequence cardiaque de plusieurs supporters pendant un match de football. Le systeme fonctionne entierement en LOCAL sans connexion Internet requise. L'architecture est entièrement locale, sans dépendance Internet.

## Architecture Globale

```
[Polar H10] --BLE--> [ESP32] --UART--> [Meshtastic] --LoRa--> [Gateway] --USB--> [PC Local]
  Capteur          Traitement        Radio LoRa      2-5 km    Réception     Visualisation
```

### Flux de données

1. **Polar H10** : Mesure fréquence cardiaque (1 Hz)
2. **ESP32-S3** : Réception BLE, buffering, formatage JSON
3. **Meshtastic** : Transmission radio LoRa 868 MHz
4. **Gateway** : Réception LoRa, liaison USB
5. **PC** : Traitement (MQTT, InfluxDB), visualisation (Web, Grafana)

## Choix Techniques Majeurs

### Format de Message : Buffer de Valeurs

**Ancien format** (moyenne) :

```json
{"id":"supporter1", "hr":72, "ts":"14:32:15", "n":42}
```

**Nouveau format** (buffer) :

```json
{"id":"supporter1", "hr":[68,70,72,71,69], "n":42}
```

**Justification** :

- Conservation de toutes les valeurs mesurées (pas de perte d'information)
- Détection des pics de fréquence cardiaque lors d'événements marquants
- Résolution temporelle de 1 seconde au lieu de 5 secondes
- Même consommation de bande passante LoRa (payload ~50 bytes)

**Impact** :

- 5 fois plus de points de données dans InfluxDB
- Reconstruction des timestamps côté serveur (fiable)
- Graphiques plus précis et réactifs

### Gestion Duty Cycle LoRa

**Contrainte réglementaire EU868** : 10% maximum (36 secondes par heure)

**Solution** : Intervalle adaptatif automatique

```cpp
const uint32_t SEND_INTERVAL = 5000 * NB_NODES;  // Millisecondes
```


| Capteurs | Intervalle | Messages/min | Duty Cycle | Valeurs/min |
| -------- | ---------- | ------------ | ---------- | ----------- |
| 1        | 5s         | 12           | ~4%        | 60          |
| 2        | 10s        | 6×2 = 12    | ~4%        | 60          |
| 3        | 15s        | 4×3 = 12    | ~4%        | 60          |

**Avantages** :

- Respect automatique des limites légales
- Scalabilité transparente (ajout de capteurs)
- Aucune perte de résolution temporelle

### Architecture Modulaire ESP32

**Ancien code** : 590 lignes monolithiques (main.cpp)

**Nouveau code** : 15 fichiers modulaires

```
include/
├── Config.h              Configuration centralisée
├── SensorInterface.h     Interface abstraite capteurs
├── PolarH10Sensor.h      Implémentation Polar H10
└── UARTManager.h         Communication série + buffer

src/
├── main.cpp              Orchestration
├── PolarH10Sensor.cpp    Logique BLE
└── UARTManager.cpp       Logique UART + buffer
```

**Bénéfices** :

- Code lisible et maintenable
- Modules testables indépendamment
- Ajout de capteurs facilité (nouvelle classe héritant SensorInterface)
- Aucune duplication de code

### Communication Locale (localhost)

**Principe** : Tous les services en local, aucune sortie Internet

```
Mosquitto (1883)  <---->  Scripts Python  <---->  InfluxDB (8086)
                                                         |
                                                   Grafana (3000)
                                                   Dashboard (5001)
```

**Avantages** :

- Aucune dépendance réseau externe
- Latence minimale
- Sécurité des données (restent sur le PC)
- Fonctionnement en stade sans WiFi

## Composants Matériels

### Par Supporter

- 1× Capteur cardiaque Polar H10
- 1× ESP32-S3 (ou compatible)
- 1× Module Meshtastic (T-Beam, Heltec LoRa)
- Câbles de connexion (TX, RX, GND)
- Batterie portable (autonomie 6-8h)

### Station de Base

- 1× Module Meshtastic Gateway
- 1× Câble USB
- 1× Ordinateur (macOS ou Linux)

## Installation

### PC Central

```bash
cd pc_central/
chmod +x install_complete.sh
./install_complete.sh
```

Installe automatiquement :

- Mosquitto (broker MQTT)
- InfluxDB 2.7 (Docker)
- Grafana (Docker)
- Dépendances Python (environnement virtuel)

### ESP32

```bash
cd esp32/

# Éditer include/Config.h
# - Décommenter SUPPORTER_1, SUPPORTER_2 ou SUPPORTER_3
# - Mettre adresse MAC du Polar H10

pio run -t upload
```

### Câblage ESP32 → Meshtastic

```
ESP32 TX (GPIO 43) → Meshtastic RX
ESP32 RX (GPIO 44) → Meshtastic TX
ESP32 GND          → Meshtastic GND
```

## Utilisation

### Démarrage Système

```bash
# Activer environnement virtuel
source stade_env/bin/activate

# Terminal 1 : Bridge Meshtastic → MQTT
python3 meshtastic_to_mqtt.py

# Terminal 2 : Bridge MQTT → InfluxDB
python3 mqtt_to_influxdb.py

# Terminal 3 : Dashboard Web
python3 web_dashboard.py
```

### Accès Interfaces

- Dashboard Web : http://localhost:5001
- Grafana : http://localhost:3000 (admin/admin)
- InfluxDB : http://localhost:8086 (admin/adminadmin)

## Améliorations Apportées

### 1. Résolution Temporelle

**Avant** : 1 point toutes les 5 secondes (moyenne)
**Après** : 5-6 points toutes les 5 secondes (valeurs brutes)

**Impact** : Détection précise des variations de FC lors des actions de jeu

### 2. Reconstruction Timestamps

**Avant** : Timestamps générés par ESP32 (RTC imprécis, dérive temporelle)
**Après** : Timestamps reconstruits par le serveur à partir du moment de réception

**Algorithme** :

```python
base_timestamp = datetime.utcnow()  # Timestamp de réception
buffer = [68, 70, 72, 71, 69]       # 5 valeurs

for i, hr_value in enumerate(buffer):
    time_offset = (len(buffer) - 1 - i) * 1  # secondes
    point_timestamp = base_timestamp - timedelta(seconds=time_offset)
    # Point 1: T-4s → 68 BPM
    # Point 2: T-3s → 70 BPM
    # ...
    # Point 5: T-0s → 69 BPM
```

**Avantages** :

- Synchronisation précise entre capteurs
- Pas de dérive temporelle
- Timestamps fiables pour analyse

### 3. Visualisation Adaptative

**Scripts Python** : Détection dynamique des supporters

```python
# Ancien : 3 scripts séparés
monitor_supporter1.py
monitor_supporter2.py
monitor_comparaison.py

# Nouveau : 1 script adaptatif
monitor_multi.py
# - Détecte automatiquement les supporters actifs
# - Layout adaptatif (1-6 capteurs)
# - Graphique de comparaison si 2+ capteurs
```

**Dashboard Web** : Auto-détection + WebSocket temps réel

- Ajout automatique de cartes pour nouveaux supporters
- Mise à jour instantanée sans rechargement de page

### 4. Gestion du Buffer Circulaire

**Implémentation** (UARTManager.cpp) :

```cpp
class UARTManager {
private:
    uint16_t hrBuffer[BUFFER_SIZE];  // Buffer circulaire
    uint8_t bufferIndex;             // Position d'écriture
    uint8_t bufferCount;             // Nombre de valeurs

public:
    void addToBuffer(uint16_t value) {
        hrBuffer[bufferIndex] = value;
        bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;
        if (bufferCount < BUFFER_SIZE) bufferCount++;
    }

    bool sendHeartRateBuffer(const char* id, uint32_t msgNumber) {
        JsonArray hrArray = doc["hr"].to<JsonArray>();
        for (int i = 0; i < bufferCount; i++) {
            hrArray.add(hrBuffer[i]);
        }
        // Envoi JSON : {"id":"supporter1", "hr":[...], "n":42}
    }
};
```

**Avantages** :

- Pas de réallocation mémoire
- Complexité O(1) pour ajout/lecture
- Taille fixe adaptée à l'intervalle d'envoi

## Structure du Projet

```
STADE_FINAL/
├── esp32/
│   ├── include/            Headers (.h)
│   ├── src/                Implémentations (.cpp)
│   └── platformio.ini      Configuration PlatformIO
│
├── pc_central/
│   ├── meshtastic_to_mqtt.py     Bridge USB → MQTT
│   ├── mqtt_to_influxdb.py       Bridge MQTT → InfluxDB
│   ├── web_dashboard.py          Dashboard web Flask
│   ├── monitor_multi.py          Graphiques Matplotlib
│   ├── install_complete.sh       Installation automatique
│   └── templates/                Pages HTML
│
└── docs/
    ├── 1_README.md               Ce fichier
    ├── 2_ARCHITECTURE.md         Architecture détaillée
    ├── 3_STRUCTURE.md            Organisation du code
    └── 4_DEBUG.md                Guide dépannage
```

## Limitations et Contraintes

### Portée LoRa

- Ligne de vue : jusqu'à 10 km
- Environnement urbain/stade : 2-5 km
- Obstacles métalliques : réduction significative

### Autonomie

- ESP32 + Meshtastic : 6-8 heures (powerbank 10000mAh)
- Polar H10 : ~200 heures (pile CR2025)

### Duty Cycle LoRa

- Limite légale EU868 : 10% (36 secondes/heure)
- Configuration système : ~4% (marge de sécurité)

## Support et Documentation

### Fichiers de Documentation

- **1_README.md** : Ce fichier (vue d'ensemble)
- **2_ARCHITECTURE.md** : Architecture technique détaillée
- **3_STRUCTURE.md** : Organisation du code
- **4_DEBUG.md** : Guide de dépannage complet

### Vérification Système

```bash
# Mosquitto actif
brew services list | grep mosquitto

# Containers Docker actifs
docker ps

# Port USB Gateway
ls /dev/cu.usbmodem*  # macOS
ls /dev/ttyUSB*       # Linux

# Test MQTT
mosquitto_sub -h localhost -t "#" -v

# Test InfluxDB
curl http://localhost:8086/health
```

## Conclusion

Ce système offre un compromis optimal entre :

- **Précision** : Résolution de 1 seconde, conservation de toutes les valeurs
- **Fiabilité** : Architecture modulaire, reconnexions automatiques
- **Légalité** : Respect strict du duty cycle LoRa
- **Évolutivité** : Ajout de capteurs sans modification majeure
- **Autonomie** : Fonctionnement complet sans Internet

La transition du format "moyenne" au format "buffer" représente l'amélioration majeure, permettant une analyse beaucoup plus fine des variations cardiaques lors des événements du match.
