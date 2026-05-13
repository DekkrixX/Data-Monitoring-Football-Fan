# Matériels

## Capteur Polar H10

| ID       | Adresse MAC       |
|----------|-------------------|
| 6315682D | C7:6F:37:F6:01:36 |
| 63028A2F | CF:5C:1E:1B:04:CE |
| 65AB7621 | FE:02:9D:9F:22:1F |
| 65C1312C | DA:DC:91:B1:19:19 |
| 6302862B | E3:BC:7E:55:74:C2 |

Description :
- Capteur cardiaque pectoral ECG, très haute précision
- Connexions : Bluetooth Low Energy, ANT+, 5 kHz (natation)
- Mémoire interne : enregistre une séance sans montre
- Étanchéité : jusqu’à 30 m
- Batterie : pile CR2025 remplaçable (~400 h)
- Compatibilité : montres Polar, smartphones, applis sport, appareils fitness

## Capteur MinIMU-9 v6

Description :
- Capteur combiné IMU 9 axes : Accéléromètre 3 axes + Gyroscope 3 axes + Magnétomètre 3 axes
- Mesures : Accélération linéaire, vitesse angulaire (rotation), orientation absolue par rapport au champ magnétique terrestre
- Puce intégrée : LSM6DS3 (accéléro/gyro) + LIS3MDL (magnétomètre) de STMicroelectronics
- Interface de communication : I2C (SDA, SCL) et SPI (optionnel)
- Tension d'alimentation : 2,4V à 3,6V (régulateur intégré permet l'alimentation jusqu'à 5V)
- Plages de mesure configurables :
    - Accéléromètre : ±2g, ±4g, ±8g, ±16g
    - Gyroscope : ±245, ±500, ±1000, ±2000 dps
    - Magnétomètre : ±4, ±8, ±12, ±16 gauss
- Fréquence d'échantillonnage : Jusqu'à 6,66 kHz (accéléro/gyro), 15 Hz (magnétomètre)
- Format : Module PCB 15,75 x 25,4 mm (taille compacte)
- Connecteurs : Broches 0,1" espacées pour breadboard ou soudure directe
- Consommation : ~1 mA (typique) en mode actif

## Capteur INMP441

Description:
- Capteur audio numérique : Microphone MEMS omnidirectionnel avec convertisseur analogique-numérique intégré
- Mesures : Captation du son  et conversion directe en signal numérique
- Puce intégrée : Microphone MEMS avec ADC et interface numérique I2S intégrés
- Interface de communication : I2S pour transmission audio numérique
- Tension d'alimentation : 1,8V à 3,3V
- Sensibilité : Typiquement -26 dBFS (±3 dB)
- Rapport signal/bruit : Environ 61 dB
- Réponse en fréquence : ~60 Hz à 15 kHz
- Fréquence d'échantillonnage : Jusqu’à ~48 kHz
- Directivité : Omnidirectionnelle
- Consommation : ~1,4 mA

## Noeuds LoRa

Description :
- Définition : petits appareils radio utilisant la technologie LoRa pour créer un réseau maillé décentralisé sans infrastructure (pas de réseau mobile/Wi-Fi).
- Fonction d’un noeud : chaque noeud peut envoyer, recevoir et relayer des messages à d’autres nœuds, prolongeant ainsi la portée de communication.
- Matériel typique : microcontrôleur (ex. ESP32 ou nRF52840) + modem LoRa.
- Communication : messages texte, données GPS et petites télémétries entre appareils du réseau.
- Réseau maillé (mesh) : auto-organisé et auto-réparant, les noeuds rebroadcastent les messages jusqu’à atteindre leur destination.
- Connectivité smartphone : configuration et utilisation via une app mobile (Bluetooth).
- LoRa (long range low power) : portée typique de plusieurs kilomètres avec très faible consommation.

# Serveur

| Service    | Port | Protocole      | Usage                                  |
|------------|------|----------------|----------------------------------------|
| Mosquitto  | 1883 | MQTT           | Transfert de messages au broker        |
| InfluxDB   | 8086 | HTTP           | API de la base de données              |
| Grafana    | 3000 | HTTP           | Interface de visualisation des données |
| Dashboard  | 5001 | HTTP/WebSocket | Interface de visualisation des données |
| PostgreSQL | 5432 | TCP/IP         | Base de données                        |
