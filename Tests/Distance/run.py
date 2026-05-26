##
# @file run.py
#
# @brief Point d'entrée du test de distance.
#
# Reçoit les paquets du noeud Meshtastic, décode leur payload JSON et vérifie la bonne réception des paquets.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

import json
from colorama import Fore, Style

from Server.Config.setting import Config
from Server.Core.meshtastic import MeshtasticClientWrapper
from Server.Utils.display import printBanner
from Server.Utils.topic import getMQTTTopic
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Tests/Meshtastic")

# =============================================================================
#  Variable global
# =============================================================================

listPackage = [] ##< @brief Liste des paquets reçus.
lastPackage = -1 ##< @brief Dernier message reçus.

# =============================================================================
#  Programme principal
# =============================================================================

##
# @brief Initialise le bridge Meshtastic vers MQTT et démarre la boucle d'attente de paquets.
##
def main():
    printBanner("   Test de distance des paquets Meshtastic")

    if Config.DEBUG:
        print("\nMeshtastic:")
        print(f"   Host  : {Config.MESHTASTIC_HOST}")
        print(f"   Topic : {Config.MESHTASTIC_TOPIC}")
        print()

    meshtasticClient = MeshtasticClientWrapper(Config.MESHTASTIC_HOST, Config.MESHTASTIC_TOPIC, onReceiveCallback=_onReceive)

    try:
        meshtasticClient.connect()

        meshtasticClient.waitForever()

    except KeyboardInterrupt:
        logger.info("[Test] Arrêt demandé par l'utilisateur (Ctrl+C)")

        meshtasticClient.close()

        printBanner("   Résultat du test de distance des paquets Meshtastic")
        check = -1
        for package in listPackage.sort():
        	if package != check + 1:
        		print(f"Paquet n°{package} a été perdu.")

    except Exception as e:
        logger.error(f"Erreur fatale: {e}", exc_info=True)

    return

# =============================================================================
#  Callback Meshtastic
# =============================================================================

##
# @brief Décode le payload JSON du champ "text", détermine le topic MQTT correspondant au type de données et vérifie le message. Appelé à chaque paquet reçu depuis le noeud Meshtastic.
#
# @param packet    Paquet Meshtastic reçu (dict).
# @param interface Interface série source.
##
def _onReceive(packet, interface):
    global listPackage
    global lastPackage

    logger.info(f"[Test] Paquet brut reçu : {packet}")

    # Seuls les paquets décodés avec un champ texte nous intéressent
    if "decoded" not in packet:
        logger.warning("[Test] Paquet sans champ 'decoded' ignoré")
        return

    try:
        data = json.loads(packet["decoded"].get("text", ""))

    except (json.JSONDecodeError, TypeError):
        logger.warning("[Test] Champ 'text' absent ou non-JSON, paquet ignoré")
        return

    channelIndex = data.get("t")
    topic        = getMQTTTopic(channelIndex, data.get("id"))
    message      = data.get("msg")

    if message == lastPackage + 1:
    	print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Paquet n°{message} reçus.")
    else:
    	print(f"{Fore.RED}[ERREUR]{Style.RESET_ALL} Paquet n°{message} reçus, paquet n°{lastPackage} attendu.")

    return

# =============================================================================
#  Point d'entrée
# =============================================================================

if __name__ == "__main__":
    main()
