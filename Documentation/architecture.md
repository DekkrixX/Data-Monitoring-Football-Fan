# Architecture

## Description

Le projet de monitoring pour supporters de football a pour objectif de collecter des données sur les supporters pendant un match grâce à une solution IoT. L’architecture globale se compose des composants suivants :
- Capteurs : recueillent les données des supporters.
- Noeuds de données : collecte les données des capteurs et les envois au noeud serveur.
- Noeud serveur : assure la communication entre les noeuds de données et le serveur central.
- Serveur : stocke les données et fournit les services de monitoring et d’analyse.

## Schéma de l'architecture

| ![Schéma de l'architecture](../Resources/Images/architecture.png) |
|:-----------------------------------------------------------------:|
| Architecture du projet de monitoring pour supporters de football  |

## Protocole de communication

### LoRa

- Technologie radio longue portée pour IoT et communication machine to machine.
- Fréquences typiques : 868MHz (EU).
- Faible consommation énergétique, adaptée à capteurs distants alimentés par batterie.
- Communication point-à-multipoint avec portée jusqu’à plusieurs kilomètres.

### Bluetooth Low Energy

- Technologie sans fil pour communication courte distance à faible consommation d’énergie.
- Utilisée pour connecter smartphones, capteurs, périphériques IoT.
- Transmission de données via paquets numériques sur la bande 2,4GHz.
- Supporte topologies point-à-point, broadcast et mesh.
- Optimisée pour périodes d’inactivité longues, permettant une autonomie élevée.

### I2C

- Protocole filaire pour communication entre microcontrôleurs et périphériques sur courtes distances.
- Utilise 2 fils : SDA (données) et SCL (horloge).
- Permet de connecter plusieurs périphériques sur le même bus grâce aux adresses uniques.
- Communication maître-esclave : le maître initie les échanges, l’esclave répond.
- Supporte des vitesses standard (100kHz), rapide (400kHz), et haute vitesse (3,4MHz).

## Schéma de montage des capteurs

| ![Schéma module LoRa](../Resources/Images/schema_esp32_LoRa.png) |
|:----------------------------------------------------------------:|
| Schéma de montage du module LoRa                                 |

| ![Schéma MinIMU-9 v6](../Resources/Images/schema_MinIMU-9_v6.png) |
|:-----------------------------------------------------------------:|
| Schéma de montage du capteur MinIMU-9 v6                          |

| ![Schéma INMP441](../Ressources/Images/schema_INMP441.png) |
|:----------------------------------------------------------:|
| Schéma de montage du capteur INMP441                       |
