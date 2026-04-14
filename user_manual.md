# Manuel utilisateur

## Table des matières

- Installation
- Utilisation
- Désinstallation

# Installation
 
Tout d’abord il faut installer les dépendances. Assurez vous que le paquet `make`. Si ce n'est pas le cas exécutez la commande `sudo apt install make` avant de lancer l'installation automatique avec la commande `make install` dans la racine du projet.
Ensuite, vous devez configurer les capteurs et flasher le code sur les cartes. Tapez les commandes suivantes: `make flash TARGET=device` pour flasher le code des capteurs et `make flash TARGET=meshtastic` pour configurer les noeuds Meshtastic.

# Utilisation

Une fois les installations et la configuration effectuées, lancez les serveurs avec les commandes `make run` et `make server`. Après la première commande, il vous sera demandé votre mot de passe pour démarrer les services locaux de votre machine.
Lorsque tous les serveurs sont en cours d’exécution, il ne vous reste plus qu’à accéder au tableau de bord: ouvrez votre navigateur et saisissez l’adresse suivante `http://localhost:5001/`.
Pour arrêter proprement les serveurs, appuyez sur Ctrl+C dans les terminaux ouverts, puis exécutez: `make stop` pour arrêter les serveurs locaux de votre machine.

# Désintallation

Pour tout désinstaller, il suffit de taper la commande `make remove` à la racine du projet.
