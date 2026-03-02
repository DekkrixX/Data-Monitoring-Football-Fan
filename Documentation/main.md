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

## Structure

```
Projet de Monitoring pour Supporters de Football
│
├── Documentation               // Fichiers de documentation du projet
│   ├── main.md
│   ├── architecture.md
│   ├── equipment.md
│   ├── development.md
│   ├── test.md
│   └── debug.md
│
├── Resources                   // Fichiers de données
│   ├── Images
│   │   └── architecture.png
│   │
│   └── Data
│       ├── supporter.json
│       └── topicMQTT.json
│
├── Logs                        // Fichiers de logs
│
├── Device                      // Code source du dispositif embarqué
│   ├── src
│   │   ├── Config
│   │   │   ├── initSensor.hpp
│   │   │   └── setting.hpp
│   │   │
│   │   ├── Sensor
│   │   │   ├── AccelerometerGyroscope
│   │   │   │   ├── GY521MPU6050
│   │   │   │   │   ├── GY521MPU6050.cpp
│   │   │   │   │   └── GY521MPU6050.hpp
│   │   │   │   │
│   │   │   │   ├── AccelerometerGyroscope.cpp
│   │   │   │   └── AccelerometerGyroscope.hpp
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
│   │   ├── influxdb.py
│   │   ├── meshtastic.py
│   │   ├── mqtt.py
│   │   └── exception.py
│   │
│   ├── Bridge
│   │   ├── bridge_Meshtastic_MQTT.py
│   │   └── bridge_MQTT_InfluxDB.py
│   │
│   ├── Dashboard
│   │   ├── templates               // Fichiers HTML pour le serveur web
│   │   │   ├── index.html
│   │   │   ├── supporter.html
│   │   │   ├── comparaison.html
│   │   │   └── error.html
│   │   │
│   │   ├── static                  // Fichiers utilisé par le serveur web
│   │   │   ├── css
│   │   │   │   ├── base.css
│   │   │   │   ├── index.css
│   │   │   │   ├── supporter.css
│   │   │   │   ├── comparaison.css
│   │   │   │   └── error.css
│   │   │   │
│   │   │   ├── js
│   │   │   │   ├── index.js
│   │   │   │   ├── supporter.js
│   │   │   │   ├── comparaison.js
│   │   │   │   └── Utils
│   │   │   │       └── board.js
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
│   │   ├── topic.py
│   │   └── state.py
│   │
│   └── Doxyfile                // Fichier de configuration de Doxygen
│
├── .Flash                      // Fichier de configuration des cartes
│   ├── device.sh
│   ├── meshtastic.sh
│   └── firmware-seeed-xiao-s3-2.7.15.567b8ea.bin
│
├── .env                        // Fichier des variables d'environnement
├── Makefile                    // Fichier de build automatique
├── user_manual.md              // Manuel utilisateur
└── README.md                   // Fichier principal d'information
```
