# Guide d'Utilisation Ultra-Simple

## En 3 étapes

### 1- Installation PC (une seule fois)

```bash
cd pc_central/
./install_complete.sh  
```

### 2- Configuration ESP32 (par capteur)

```bash
cd esp32/

# Éditer include/Config.h
# Ligne 18 : décommenter SUPPORTER_1 (ou 2, ou 3)
# Ligne 28 : mettre l'adresse MAC du Polar H10

# Upload
pio run -t upload
```

Câbler :

- ESP32 TX (43) → Meshtastic RX
- ESP32 RX (44) → Meshtastic TX
- ESP32 GND → Meshtastic GND
- ESP32 3V3 → Meshtastic 3V3

### 3 - Jour du match

```bash
# Terminal 1
python3 meshtastic_to_mqtt.py

# Terminal 2
python3 mqtt_to_influxdb.py

# Navigateur
open http://localhost:3000
```

## Flux de données

```
Polar H10 → BLE → ESP32 → UART → Meshtastic → LoRa → Gateway → USB → PC

Puis dans le PC :
USB → Script 1 → Mosquitto → Script 2 → InfluxDB → Grafana
```

## Checklist rapide

**Avant le match** :

- [ ]  Mosquitto lancé : `brew services list | grep mosquitto`
- [ ]  InfluxDB lancé : `docker ps | grep influxdb`
- [ ]  ESP32 uploadés (x2)
- [ ]  Gateway USB branché
- [ ]  Port USB trouvé : `ls /dev/tty.usb*`

**Pendant le match** :

- [ ]  Script 1 tourne (messages s'affichent)
- [ ]  Script 2 tourne (messages s'affichent)
- [ ]  Grafana ouvert (http://localhost:3000)

## En cas de problème

### ESP32 ne voit pas le Polar

1. Vérifier l'adresse MAC (minuscules)
2. Polar H10 en contact peau
3. Rapprocher ESP32

### Script Python erreur port

```bash
# Trouver le port
ls /dev/tty* | grep usb

# Éditer meshtastic_to_mqtt.py ligne 25
SERIAL_PORT = '/dev/cu.usbserial-XXXX'
```

### Mosquitto erreur

```bash
# Vérifier
brew services list | grep mosquitto

# Si pas démarré
brew services start mosquitto
```
