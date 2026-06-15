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
import statistics
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

listPackage  = [] ##< @brief Liste des paquets non reçus.
lastPackage  = {} ##< @brief Dernier message reçus par identifiant.
listLastSNR  = [] ##< @brief Dernière mesure du SNR.
listAllSNR   = [] ##< @brief Liste des mesures du SNR.
listLastRSSI = [] ##< @brief Dernière mesure du RSSI.
listAllRSSI  = [] ##< @brief Liste des mesures du RSSI.

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
        for nodeId, nbPackets in lastPackage.items():
            print(f"Nombre de paquets envoyé par le noeud {nodeId}: {nbPackets}.")
            print(f"Nombre de paquets reçus depuis le noeud {nodeId}: {nbPackets - len(listPackage)}.")
        print(f"Moyenne globale du SNR: {statistics.mean(listAllSNR)}.")
        print(f"Moyenne globale du RSSI: {statistics.mean(listAllRSSI)}.")
        if listPackage:
            for package in listPackage.sort():
        	    print(f"Paquet n°{package} a été perdu.")

    except Exception as e:
        logger.error(f"Erreur fatale: {e}")

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
    global listLastSNR
    global listAllSNR
    global listLastRSSI
    global listAllRSSI

    logger.info(f"[Test] Paquet brut reçu : {packet}")

    # Seuls les paquets décodés avec un champ texte nous intéressent
    if "decoded" not in packet:
        logger.warning("[Test] Paquet sans champ 'decoded' ignoré")
        return

    try:
        data = json.loads(packet["decoded"].get("text", ""))
        if packet.get("rxSnr") and packet.get("rxRssi"):
            listLastSNR.append(packet.get("rxSnr"))
            listAllSNR.append(packet.get("rxSnr"))
            listLastRSSI.append(packet.get("rxRssi"))
            listAllRSSI.append(packet.get("rxRssi"))

    except (json.JSONDecodeError, TypeError):
        logger.warning("[Test] Champ 'text' absent ou non-JSON, paquet ignoré")
        return

    channelIndex = data.get("t")
    topic        = getMQTTTopic(channelIndex, data.get("id"))
    message      = data.get("msg")

    if data.get("id") not in lastPackage:
        lastPackage[data.get("id")] = 0

    if message == lastPackage[data.get("id")] + 1:
    	print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} Paquet n°{message} reçus du noeud n°{data.get('id')}.")
    else:
    	print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Paquet n°{message} reçus du noeud n°{data.get('id')}, paquet n°{lastPackage[data.get('id')] + 1} attendu.")
    if listLastSNR[-1] <= -5:
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} SNR faible : {listLastSNR[-1]}.")
    if listLastRSSI[-1] <= -110:
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} RSSI faible : {listLastRSSI[-1]}.")

    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Moyenne du snr sur les dix derniers paquets : {statistics.mean(listLastSNR)}.")
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Moyenne du rssi sur les dix derniers paquets : {statistics.mean(listLastRSSI)}.")

    if len(listLastSNR) >= 10:
        listLastSNR.pop(0)
    if len(listLastRSSI) >= 10:
        listLastRSSI.pop(0)

    lastPackage[data.get("id")] = message

    return

# =============================================================================
#  Point d'entrée
# =============================================================================

if __name__ == "__main__":
    main()
