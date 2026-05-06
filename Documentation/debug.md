# Debug

## Problème de permissions

Si vous rencontrez des problèmes de permission lors de l'installation, du flash ou du lancement des serveurs. Ajouter l'utilisateur au groupe suivant:
- docker
- dialout
Pour cela utiliser les commandes suivante en remplaçant $USER par votre nom d'utilisateur.
- `sudo usermod -aG docker $USER`
- `sudo usermod -aG dialout $USER`
Une fois les commandes lancées il faut redémarrer l'ordinateur pour que les changements soit actif.

## Problème d'installation de docker

Si vous rencontrez des problèmes lors de l'installation automatique de docker. Installer docker manuellement en suivant la documentation en ligne : `https://docs.docker.com/engine/install/`.

## Problème de flash du firmware ou du code

Si vous rencontrez des problèmes lors du flash du firmware ou du code sur les cartes ESP32, activer le mode bootloader en maintenant le bouton B (BOOT) puis appuyer sur le bouton R (RESET) avant de relacher le bouton B. Puis relancer le flash.

## Problème de configuration Meshtastic

Si le script automatique de la configuration de Meshtastic ne configure pas entièrement la carte tapez la commande `.venv/meshtastic-env/bin/meshtastic --port $PORT --info` pour afficher la configuration et vérifier que les éléments suivants sont configurer :
- device role : CLIENT_MUTE ou CLIENT
- power isPowerSaving : true
- lora region : EU_868
- lora hopLimit : 3
- lora tx_power : 14
- lora modemPreset : LONG_FAST
- bluetooth enabled : false
- serial enabled : true
- serial txd : 43
- serial rxd : 44
- serial mode : TEXTMSG
- serial baude : BAUD_115200
- channel psk : 5Bqo...YA=
- channel name : monitoring
Si ce n'est pas le cas relancer la configuration ou ajouter la manuellemnt.
