# Manuel utilisateur

## Table des matières

- Installation
- Utilisation
- Désinstallation

# Installation
 
Tout d’abord il faut installer les dépendances. Assurez vous que le paquet `make` est installé. Si ce n'est pas le cas exécutez la commande `sudo apt install make` avant de lancer l'installation automatique avec la commande `make install` dans la racine du projet.
Attention l'installation des dépendances requirent une connexion à internet.
Ensuite, vous devez configurer les capteurs et flasher le code sur les cartes. Tapez les commandes suivantes: `make flash TARGET=device` pour flasher le code des capteurs et `make flash TARGET=meshtastic` pour configurer les noeuds Meshtastic.

Pour configurer le code des cartes ESP32 correctement il faut modifier certaine macros dans le fichier setting.hpp (SUPPORTER_ID, STADIUM_BLEACHER_ID, NB_SENSOR) et définir le type de capteur auquel la carte est connecté.

# Utilisation

Une fois les installations et la configuration effectuées, lancez les serveurs avec la commande `make run`. Lorsque tous les serveurs sont en cours d’exécution, il ne vous reste plus qu’à accéder au tableau de bord: ouvrez votre navigateur et saisissez l’adresse suivante `http://localhost:5001/` pour la visualisation des données et l'adresse `http://localhost:5001/event` pour le contrôle des évènements du match.
Pour arrêter proprement les serveurs exécutez la commande `make stop`.
Attention le premier lancement du serveur require une connexion internet, mais pour les lancements suivants tous fonctionnent localement.

# Désintallation

Pour tout désinstaller, il suffit de taper la commande `make remove` à la racine du projet.
