# Matériels

## Capteur Polar H10

| ID       | Adresse MAC       |
|----------|-------------------|
| 6315682D | C7:6F:37:F6:01:36 |
| 63028A2F | CF:5C:1E:1B:04:CE |

Description :
- Capteur cardiaque pectoral ECG, très haute précision
- Connexions : Bluetooth Low Energy, ANT+, 5 kHz (natation)
- Mémoire interne : enregistre une séance sans montre
- Étanchéité : jusqu’à 30 m
- Batterie : pile CR2025 remplaçable (~400 h)
- Compatibilité : montres Polar, smartphones, applis sport, appareils fitness

## Capteur GY-521 MPU6050

Description :
- Capteur combiné accéléromètre 3 axes + gyroscope 3 axes
- Mesure l’accélération linéaire et la rotation angulaire
- Interface de communication : I2C (SDA, SCL)
- Tension d’alimentation : 3,3V / 5V
- Taille compacte, facile à intégrer dans les projets électroniques

## Noeuds LoRa

| Nom             | Adresse MAC       | Description physique             |
|-----------------|-------------------|----------------------------------|
| Meshtastic 9964 | 98:3D:AE:60:99:65 | Fils jaune, bleu, blanc, rouge   |
| Meshtastic 8ec8 | 98:3D:AE:60:8E:C9 | Fils jaune, orange, noir, marron |
| Meshtastic 4b98 | 98:3D:AE:61:4B:99 | Gateway                          |

Description :
- Définition : petits appareils radio utilisant la technologie LoRa pour créer un réseau maillé décentralisé sans infrastructure (pas de réseau mobile/Wi-Fi).
- Fonction d’un noeud : chaque noeud peut envoyer, recevoir et relayer des messages à d’autres nœuds, prolongeant ainsi la portée de communication.
- Matériel typique : microcontrôleur (ex. ESP32 ou nRF52840) + modem LoRa.
- Communication : messages texte, données GPS et petites télémétries entre appareils du réseau.
- Réseau maillé (mesh) : auto-organisé et auto-réparant, les noeuds rebroadcastent les messages jusqu’à atteindre leur destination.
- Connectivité smartphone : configuration et utilisation via une app mobile (Bluetooth).
- LoRa (long range low power) : portée typique de plusieurs kilomètres avec très faible consommation.

# Serveur

| Service   | Port | Protocole      | Usage                                  |
|-----------|------|----------------|----------------------------------------|
| Mosquitto | 1883 | MQTT           | Transfert de messages au broker        |
| InfluxDB  | 8086 | HTTP           | API de la base de données              |
| Grafana   | 3000 | HTTP           | Interface de visualisation des données |
| Dashboard | 5001 | HTTP/WebSocket | Interface de visualisation des données |
