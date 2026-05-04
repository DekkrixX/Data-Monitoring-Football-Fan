# Documentation du Projet de Monitoring pour Supporters de Football

## Description

Le projet de monitoring pour supporters de football est la réalisation d'une collaboration entre le Lab-STICC (le centre de recherche de Lorient) et le FCL (le Football Club de Lorient). L'objectif de ce projet est de développer une solution IoT performante, économique et à gestion locale des données pour analyser les données des supporters pendant les matchs de football. Les données collectées seront utilisées pour réaliser une vidéo promotionnelle valorisant le club, de la ville et du laboratoire de recherche de Lorient. Le projet est réalisé par des étudiants du Master Systèmes Embarqués - Systèmes Intégrés à Lorient sous la supervision de deux ingénieurs du Lab-STICC.

## Contributeurs

Le projet a été initialement lancé par un groupe d'étudiants du Master Systèmes Embarqués - Système Intégrés en deuxième années à Lorient et encadré par deux ingénieurs du Lab-STICC. Puis le projet a été repris par un étudiant du même Master en première années afin d'améliorer et ajouter des capteurs au dispositif existant.

Étudiants de 2ème années :
- NDIAYE Soukeye
- DOSSOU Hillary
- RATSIMBAZAFY Kiady Sandatra

Étudiant de 1ère années :
- GUILLEMOD Quentin

Ingénieur du Lab-STICC :
- DOUGUET Ronan
- EUSTACHE Yvan

## Table des matières

1. [Architecture](architecture.md)
2. [Matériels](equipment.md)
3. [Tests](test.md)
4. [Debug](debug.md)
5. [Développement](development.md)
6. [Données](data.md)

## Structure

```
Projet de Monitoring pour Supporters de Football
│
├── Documentation               // Fichiers de documentation du projet
│   ├── main.md
│   ├── architecture.md
│   ├── equipment.md
│   ├── development.md
│   ├── data.md
│   ├── test.md
│   └── debug.md
│
├── Resources                   // Fichiers de données
│   ├── Images
│   │   ├── schema_esp32_LoRa.png
│   │   ├── schema_INMP441.png
│   │   ├── schema_MinIMU-9_v6.png
│   │   └── architecture.png
│   │
│   ├── Images
│   │   └── postgreSQL.sql
│   │
│   └── Data
│       ├── Event-Configuration
│       │   ├── Amical.json
│       │   ├── Championat.json
│       │   ├── Coupe de France.json
│       │   └── Default.json
│       │
│       ├── capteur.json
│       ├── event.json
│       ├── supporter.json
│       ├── stadiumBleacher.json
│       └── topicMQTT.json
│
├── Logs                        // Fichiers de logs
│
├── Device                      // Code source du dispositif embarqué
│   ├── src
│   │   ├── Config
│   │   │   ├── Log
│   │   │   │   ├── Log.cpp
│   │   │   │   └── Log.hpp
│   │   │   │
│   │   │   ├── initSensor.hpp
│   │   │   └── setting.hpp
│   │   │
│   │   ├── Sensor
│   │   │   ├── AccelerometerGyroscope
│   │   │   │   ├── MinIMU-9_v6
│   │   │   │   │   ├── MinIMU-9_v6.cpp
│   │   │   │   │   └── MinIMU-9_v6.hpp
│   │   │   │   │
│   │   │   │   ├── AccelerometerGyroscope.cpp
│   │   │   │   └── AccelerometerGyroscope.hpp
│   │   │   │
│   │   │   ├── Acoustic
│   │   │   │   ├── INMP441
│   │   │   │   │   ├── INMP441.cpp
│   │   │   │   │   └── INMP441.hpp
│   │   │   │   │
│   │   │   │   ├── Acoustic.cpp
│   │   │   │   └── Acoustic.hpp
│   │   │   │
│   │   │   ├── HeartRate
│   │   │   │   ├── PolarH10
│   │   │   │   │   ├── PolarH10.cpp
│   │   │   │   │   └── PolarH10.hpp
│   │   │   │   │
│   │   │   │   ├── HeartRate.cpp
│   │   │   │   └── HeartRate.hpp
│   │   │   │
│   │   │   ├── Sensor.cpp
│   │   │   └── Sensor.hpp
│   │   │
│   │   ├── Utils
│   │   │   ├── BluetoothLowEnergyManager
│   │   │   │   ├── BluetoothLowEnergyManager.cpp
│   │   │   │   └── BluetoothLowEnergyManager.hpp
│   │   │   │
│   │   │   ├── Logger
│   │   │   │   ├── Logger.cpp
│   │   │   │   └── Logger.hpp
│   │   │   │
│   │   │   ├── UARTManager
│   │   │   │   ├── UARTManager.cpp
│   │   │   │   └── UARTManager.hpp
│   │   │   │
│   │   │   ├── sensorType.cpp
│   │   │   ├── sensorType.hpp
│   │   │   └── state.hpp
│   │   │
│   │   └── main.cpp
│   │
│   ├── platformio.ini          // Fichier de configuration de PlatformIO
│   ├── partition.csv           // Fichier de configuration de la partition de la carte ESP32
│   └── Doxyfile                // Fichier de configuration de Doxygen
│
├── Server
│   ├── Config
│   │   └── config.py
│   │
│   ├── Core
│   │   ├── Supporter
│   │   │   ├── supporter.py
│   │   │   └── Data
│   │   │       └── heartRate.py
│   │   │
│   │   ├── StadiumBleacher
│   │   │   ├── stadiumBleacher.py
│   │   │   └── Data
│   │   │       ├── accelerometer.py
│   │   │       └── acoustic.py
│   │   │
│   │   ├── influxdb.py
│   │   ├── meshtastic.py
│   │   ├── mqtt.py
│   │   ├── postgresql.py
│   │   └── exception.py
│   │
│   ├── Bridge
│   │   ├── bridge_Meshtastic_MQTT.py
│   │   └── bridge_MQTT_InfluxDB.py
│   │
│   ├── Dashboard
│   │   ├── templates               // Fichiers HTML pour le serveur web
│   │   │   ├── Control
│   │   │   │   ├── configuration.html
│   │   │   │   ├── error.html
│   │   │   │   ├── event.html
│   │   │   │   └── preparation.html
│   │   │   │
│   │   │   └── Dashboard
│   │   │       ├── index.html
│   │   │       ├── supporter.html
│   │   │       ├── stadiumBleacher.html
│   │   │       └── comparison.html
│   │   │
│   │   ├── static                  // Fichiers utilisé par le serveur web
│   │   │   ├── css
│   │   │   │   ├── Control
│   │   │   │   │   ├── configuration.css
│   │   │   │   │   ├── error.css
│   │   │   │   │   ├── event.css
│   │   │   │   │   └── preparation.css
│   │   │   │   │
│   │   │   │   ├── Dashboard
│   │   │   │   │   ├── comparison.css
│   │   │   │   │   ├── index.css
│   │   │   │   │   ├── stadiumBleacher.css
│   │   │   │   │   └── supporter.css
│   │   │   │   │
│   │   │   │   └── base.css
│   │   │   │
│   │   │   ├── js
│   │   │   │   ├── Control
│   │   │   │   │   ├── configuration.js
│   │   │   │   │   ├── event.js
│   │   │   │   │   └── preparation.js
│   │   │   │   │
│   │   │   │   ├── Dashboard
│   │   │   │   │   ├── comparison.js
│   │   │   │   │   ├── index.js
│   │   │   │   │   ├── stadiumBleacher.js
│   │   │   │   │   └── supporter.js
│   │   │   │   │
│   │   │   │   └── Utils
│   │   │   │       ├── time.js
│   │   │   │       ├── stringConversion.js
│   │   │   │       └── element.js
│   │   │   │
│   │   │   ├── icon
│   │   │   │   ├── delete-dark.png
│   │   │   │   ├── delete-light.png
│   │   │   │   ├── modify-dark.png
│   │   │   │   └── modify-light.png
│   │   │   │
│   │   │   └── lib                 // Fichiers de bibliothèque externe
│   │   │       ├── chart.umd.min.js
│   │   │       └── socket.io.min.js
│   │   │
│   │   ├── app.py
│   │   ├── routes.py
│   │   └── socketioHandlers.py
│   │
│   ├── Utils
│   │   ├── data.py
│   │   ├── display.py
│   │   ├── logger.py
│   │   ├── topic.py
│   │   ├── time.py
│   │   ├── event.py
│   │   └── state.py
│   │
│   ├── Dockerfile              // Fichier de configuration de Docker
│   └── Doxyfile                // Fichier de configuration de Doxygen
│
├── Tests
│   ├── DataSimulationServer
│   │   ├── Simulation
│   │   │   ├── heartRateSimulator.py
│   │   │   ├── acousticSimulator.py
│   │   │   └── accelerometerGyroscopeSimulator.py 
│   │   │
│   │   ├── run.py
│   │   └── Dockerfile
│   │
│   └── Distance
│       ├── Flash
│       │   ├── device.sh
│       │   └── meshtastic.sh
│       │
│       ├── Device
│       │   ├── src
│       │   │   ├── Config
│       │   │   │   └── setting.hpp
│       │   │   │
│       │   │   ├── Utils
│       │   │   │   └── UARTManager
│       │   │   │       ├── UARTManager.cpp
│       │   │   │       └── UARTManager.hpp
│       │   │   │
│       │   │   └── main.cpp
│       │   │
│       │   └── platformio.ini  // Fichier de configuration de PlatformIO
│       │
│       └── log.py
│
├── Scripts
│   ├── envcrypt.sh             // Script de chiffrement de fichier
│   ├── logviewer.sh            // Script de visualisation de log
│   ├── readSerialLog.sh        // Script de récupération des logs des cartes ESP32
│   ├── flash.sh                // Script de flash des cartes ESP32
│   └── out.sh
│
├── .Flash                      // Fichier de configuration des cartes
│   └── firmware-seeed-xiao-s3-2.7.15.567b8ea.bin
│
├── .env                        // Fichier de variables d'environnement
├── .env.encrypted              // Fichier de variables d'environnement chiffré
├── docker-compose.yml          // Fichier de configuration de docker
├── Makefile                    // Fichier de build automatique
├── user_manual.md              // Manuel utilisateur
└── README.md                   // Fichier principal d'information
```
