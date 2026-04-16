# Développement

## Description

Cette partie décrit l’ensemble des éléments nécessaires au développement, à l’installation et à la maintenance du projet. Elle a pour objectif de permettre à un développeur ou un nouvel intervenant de prendre en main le projet rapidement et de manière autonome.

Elle détaille notamment :
- L’installation des dépendances logicielles requises pour le bon fonctionnement du projet.
- Les différentes méthodes pour lancer et exécuter les programmes.
- La procédure pour flasher les cartes matérielles utilisées par le système.
- Les outils et méthodes permettant de tester et valider le code.
- Les règles et bonnes pratiques à suivre pour ajouter des modifications ou de nouvelles fonctionnalités sans compromettre la stabilité du projet.

Cette section constitue la référence technique principale pour toute intervention sur le code ou l’infrastructure logicielle du projet.

## Installation des dépendances

Pour installer toutes les dépendances il suffit d'exécuter la commande `make install` à la racine du projet. Et pour les désinstaller il faut utiliser la commande `make remove`.
Si `make` n'est pas installé exécutez la commande `sudo apt install make`.

## Lancement des scripts de démarrage des serveurs

Pour démarrer les différents serveurs nécessaire à la communication et visualisation des données il faut exécuter la commande `make run` à la racine du projet. Cette commande va lancer les conteneurs Docker et éxécuter les srcipts. Pour les arrêter utilisez la commande `make stop`.
Attention seul le premier lancement du serveur nécessite une connexion à internet pour le téléchargement des images Docker.

## Procédure de flash

Pour flash une carte utiliser la commande `bash Scripts/flash.sh` à la racine du projet. Attention à bien entrer le bon port série USB pour ne pas flasher malencontreusement la mauvaise carte.

## Tests

TODO

## Collaboration sur le projet

Règles et bonnes pratiques à suivre pour ajouter des modifications ou de nouvelles fonctionnalités sans compromettre la stabilité du projet.

Utilisation du projet:
- Toutes installations doit être automatisées ou très bien documentées.
- L'utilisation du projet doit être simple et documentée.

Organisation du projet:
- Chaque composant doit pouvoir être remplacé ou étendu sans modifier les autres.
- Chaque module doit être testable indépendament.

Gestion du code:
- Le code doit respecter certaine conventions de nommage (nom explicite, code aéré).
- Les fonctions, les classes et les modules doivent être documentés.
- Les fonctions doivent être le plus simple possible et traiter une seule problématique.

Tests et stabilité
- Les nouvelles fonctionnalités doivent être accompagnées de tests appropriés lorsque cela est pertinent.
- Aucune modification ne doit dégrader les fonctionnalités existantes.

Sécurité et configuration
- Les informations sensibles (clé, token, mot de passe) ne doivent jamais être stockées dans le code.
- Les paramètres de configuration doivent tous être défini au même endroit (.env) ou fichier de configuration spécifique si besoin.

Documentation
- Toute modification impactant le fonctionnement du projet doit être documentée.
- La documentation doit rester à jour et cohérente avec l'état du code.
- Les exemples fournis doivent être fonctionnels et vérifiables.

### Topic MQTT

Pour l'ajout d'un topic MQTT utilisez le format suivant: monitoring/[type général du capteur]/[id du supporter]

### Ajout d'un nouveau capteur

Si un capteur implémente les mêmes caractéristiques que le nouveau capteur, alors créez un nouveau dossier dans le dossier général du capteur. Puis ajoutez le code de votre nouveau capteur dans le dossier que vous avez créé. Respectez les conventions pour la transmission de données et adaptez les paramètres pour l’utilisation de votre capteur.

Sinon, créez un dossier général dans le dossier Sensor et codez une classe générale pour le type du capteur, puis ajoutez ce nouveau type au fichier sensorType dans le dossier Utils. Ensuite, créez un dossier avec le code de votre capteur dans le dossier général que vous avez créé. Adaptez les paramètres pour l’utilisation de votre capteur.
Pour la partie serveur, il vous faudra modifier la fonction addData du fichier supporter.py et ajouter le type de donnée général du capteur dans le dossier Data. Enfin, adaptez le code du client et du serveur afin que les données soient utilisées.

### Documentation du projet

Documentation du code du device:
Pour générer la documentation tapez `make doc` à la racine du projet puis ouvrez dans un navigateur le fichier `Device/doc/html/index.hml`.

Documentation du code du serveur:
Pour générer la documentation tapez `make doc` à la racine du projet puis ouvrez dans un navigateur le fichier `Server/doc/html/index.html`.

### Documentation externe

Matériel:
- [Esp32-S3](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)

Platforme de développement:
- [PlatformIO](https://docs.platformio.org/en/latest/)

Firmware:
- [Meshtastic](https://registry.platformio.org/libraries/bblanchon/ArduinoJson)

Bibliothèque:
- [NimBLE](https://h2zero.github.io/NimBLE-Arduino/md__new__user__guide.html)
- [UART](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/serial.html)
- [JSON](https://registry.platformio.org/libraries/bblanchon/ArduinoJson)
