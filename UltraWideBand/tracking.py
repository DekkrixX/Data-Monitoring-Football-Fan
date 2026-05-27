##
# @file tracking.py
#
# @brief Point d'entrée principal de la communication UWB pour le tracking.
#
# Lance la mesure de la distance en temps réel, calcul la position de l'objet tracké et le publie sur un topic MQTT.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

import sys
import subprocess
import argparse
import json
import numpy as np
from Server.Config.setting import Config
from Server.Utils.display import printBanner
from Server.Core.mqtt import MQTTClientWrapper
from Server.Utils.logger import Logger

# =============================================================================
#  ID du tracker
# =============================================================================

# À MODIFIER
ID = 1

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("UltraWideBand/Tracker")

# =============================================================================
#  Variable globale
# =============================================================================

## @brief Client MQTT partagé entre main() et les fonctions de messages MQTT.
mqttClient = None

# =============================================================================
#  Programme principal
# =============================================================================

##
# @brief Initialise le client MQTT et démarre la communication avec la carte UWB.
#
# @throws RuntimeError Si le démarrage du serveur SocketIO échoue.
##
def main():
    global mqttClient

    printBanner("   Communication avec la carte UltraWideBand")

    if Config.DEBUG:
        print("\nMQTT:")
        print(f"   Host      : {Config.MQTT_BROKER_HOST}")
        print(f"   Port      : {Config.MQTT_BROKER_PORT}")
        print(f"   KeepAlive : {Config.MQTT_BROKER_KEEPALIVE}")
        print(f"   QoS       : {Config.MQTT_BROKER_QOS}")

    mqttClient = MQTTClientWrapper(
        "MQTT_tracking",
        Config.MQTT_BROKER_HOST,
        Config.MQTT_BROKER_PORT,
        Config.MQTT_BROKER_KEEPALIVE,
        qos=Config.MQTT_BROKER_QOS
    )

    try:
        mqttClient.connect()

        # MQTT en mode non bloquant pour que la boucle de simulation puisse tourner ensuite
        mqttClient.start(blocking=False)

        # Démarrage de la communication avec la carte
        run()

    except KeyboardInterrupt:
        logger.info("[Tracking] Arrêt demandé par l'utilisateur (Ctrl+C)")

        mqttClient.stop()

    return None



##
# @brief Lance la communication avec la carte UWB.
##
def run():
    # Parsing de la ligne de commande
    baliseType, address, destAddress, port = checkCommandLine(sys.argv)

    # Lance le processus de communication avec la carte
    process = subprocess.Popen(buildCommand(baliseType, address, destAddress, port), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

    if destAddress:
        destAddress = normalizeAddress(destAddress)

        # Initialisation des valeurs des données
        data = {}
        flag = {}
        for macAddress in destAddress:
            data[macAddress] = {"distance": None,  "status": None}
            flag[macAddress] = {"distance": False, "status": False}
        distanceFlag   = False
        macAddressFlag = False
        statusFlag     = False
        distance   = None
        macAddress = None
        status     = None

        # Lecture des données
        for line in process.stdout:
            # Parsing des données
            if "distance" in line:
                distanceFlag = True
                distance = float(line.split("distance:")[1].split("cm")[0].strip())
            if "mac address" in line:
                macAddressFlag = True
                macAddress = line.split("mac address:")[1].split("hex")[0].strip()
            if "status" in line:
                statusFlag = True
                status = status = line.split("status:")[1].split("(")[0].strip()

            # Traitement des données
            if distanceFlag and macAddressFlag and statusFlag:
                data[macAddress]["distance"] = distance
                data[macAddress]["status"]   = status

                if status == "OK":
                    flag[macAddress]["distance"] = True
                    flag[macAddress]["status"]   = True
                    logger.info(f"Status: {status} Cible: {macAddress} Distance: {distance}")
                else:
                    logger.warning(f"Status: {status} Cible: {macAddress} Distance: {distance}")

                # Remise à zéro des flags
                distanceFlag   = False
                macAddressFlag = False
                statusFlag     = False

                # Traitement des données de toutes les ancres
                flagAllData = True
                for mac in flag:
                    if not flag[mac]["distance"] or not flag[mac]["status"]:
                        flagAllData = False

                if flagAllData:
                    # Construction de la liste des distances et des positions
                    positionList, distanceList = buildList(data)

                    # Calcul de la position de la carte tag
                    position = calculPosition(positionList, distanceList)

                    # Envoi sur MQTT les données
                    if baliseType == "tag":
                        positionMessage(position, ID)

                    # Remise à zéro des flags
                    for mac in flag:
                        flag[mac]["distance"] = False
                        flag[mac]["status"]   = False

    return None



##
# @brief Converti l'adresse hexa en format d'adresse de retour par la commande.
#
# @param addr Adresse en hexa.
#
# @return Adresse formater.
##
def normalizeAddress(addr):
    # "0x1" → 1 → "00:01" sur 2 octets
    # "[0x1,0x2]" → liste de "00:01", "00:02"
    addr = addr.strip("[]")
    result = []
    for a in addr.split(","):
        a = a.strip()
        val = int(a, 16)
        # Formatage en paires hex séparées par ":"
        hex_str = f"{val:04x}"  # ex: "0001"
        formatted = ":".join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))  # "00:01"
        result.append(formatted)

    return result



##
# @brief Vérifie les arguments de la ligne de commande.
#
# @param args Arguments du programme.
#
# @return Les valeurs des arguments données au programme.
##
def checkCommandLine(args):
    parser = argparse.ArgumentParser(description="Tracking de position d'un objet")

    # Options
    parser.add_argument("--destAddress", nargs="?", type=str, help="Adresse des ancres")

    # Arguments
    parser.add_argument("port", type=str, help="Port série de la carte")
    parser.add_argument("baliseType", type=str, choices=["anchor", "tag"], help="Type de la carte")
    parser.add_argument("address", type=str, help="Adresse de la carte")

    parsed = parser.parse_args(args[1:])

    if not parsed.destAddress and parsed.baliseType == "tag":
        print("Erreur: Il faut spécifier les adresses de destination pour une carte de type tag.")
        sys.exit()

    return parsed.baliseType, parsed.address, parsed.destAddress, parsed.port



##
# @brief Contruit la commande à exécuter pour récupérer les données de distances.
#
# @param baliseType  Type de la balise.
# @param address     Adresse de la carte.
# @param destAddress Adresses des cartes ancres.
# @param port        Port série de la carte.
#
# @return La commande à exécuter.
##
def buildCommand(baliseType, address, destAddress, port):
    # Commande
    cmd = ["python3.10", "UltraWideBand/uwb-qorvo-tools/scripts/fira/run_fira_twr/run_fira_twr.py", "-p", f"uart:{port}", "-t", "-1", "-c", "5", "--mac", address]

    match baliseType:
        case "tag":
            cmd.extend(["--dest-mac", destAddress])
            nbBalise = len(destAddress.strip("[]").split(","))
            if nbBalise > 1:
                cmd.extend(["--n_controlees", str(nbBalise)])
                cmd.extend(["--node", "onetomany"])
        case "anchor":
            cmd.append("--controlee")

    return cmd



##
# @brief Construiction des listes de positions et de distances.
#
# @param data Données récupéré par la carte tag.
#
# @return Les listes de positions et de distances.
##
def buildList(data):
    positionList = []
    distanceList = []

    filePath = Config.PATH["data"] + "tracker.json"

    try:
        logger.info(f"[Tracking] Lecture du fichier tracker : '{filePath}'")

        with open(filePath, "r") as file:
            for tracker in json.load(file):
                if tracker["id"] == ID:
                    for index in range(len(tracker["zone"])):
                        positionList.append({"x": tracker["zone"][index]["x"], "y": tracker["zone"][index]["y"]})
                        distanceList.append(data[tracker["zone"][index]["address"]]["distance"])


    except FileNotFoundError:
        message = f"[Tracking] Fichier tracker introuvable : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message)

    except json.JSONDecodeError as e:
        message = f"[Tracking] Fichier tracker invalide (JSON malformé) : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message) from e

    return positionList, distanceList



##
# @brief Envoi un message sur le topic MQTT
##
def positionMessage(position, idf):
    topic    = f"monitoring/tracker/{idf}"
    message  = json.dumps({"n": "DWM3001CDK", "p": [position]})
            
    if not mqttClient.publish(topic, message):
        logger.warning(f"[Tracking] Échec de la publication sur le topic '{topic}'")
    else:
        logger.info(f"[Tracking] Publication du message '{message}' sur le topic '{topic}'")

    return None



##
# @brief Calcul la position de la carte tag à partir du point d'intersection des distances des ancres.
#
# @param positionList Liste des positions des cartes ancres.
# @param distanceList Liste des distances de la carte tag aux cartes ancres.
#
# @return La position de la carte tag.
##
def calculPosition(positionList, distanceList):
    positions = np.array([[p['x'], p['y']] for p in positionList])
    distances = np.array(distanceList)

    # Référence : premier cercle
    x1, y1 = positions[0]
    r1 = distances[0]

    # Construction du système Ax = b
    A = []
    b = []
    for i in range(1, len(positions)):
        xi, yi = positions[i]
        ri = distances[i]
        A.append([2 * (xi - x1), 2 * (yi - y1)])
        b.append(ri**2 - xi**2 - yi**2 - r1**2 + x1**2 + y1**2)

    A = np.array(A)
    b = np.array(b)

    # Résolution : moindres carrés si sur-déterminé, exacte si 2 équations
    result, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

    return {'x': result[0], 'y': result[1]}

# =============================================================================
#  Point d'entrée
# =============================================================================

if __name__ == "__main__":
    main()
