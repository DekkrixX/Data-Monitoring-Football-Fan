##
# @file topic.py
#
# @brief Gestion des topics MQTT et construction des points InfluxDB.
#
# Fournit getMQTTTopic() pour résoudre le topic MQTT d'un type de données, et buildPointInfluxDB() pour séparer les champs d'un message en tags et fields destinés à InfluxDB.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

import json

from Server.Config.setting import Config
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/Topic")

# =============================================================================
#  Résolution du topic MQTT
# =============================================================================

##
# @brief Retourne le topic MQTT correspondant à un type de données et à un identifiant de supporter.
#
# @param channelIndex Index du channel de communication.
# @param supporterId  Identifiant numérique du supporter.
#
# @return str Topic MQTT résolu.
#
# @throws RuntimeError Si le fichier est absent, invalide ou si le type est inconnu.
##
def getMQTTTopic(channelIndex, supporterId):
    filePath = Config.PATH["data"] + "topicMQTT.json"

    try:
        logger.info(f"[Topic] Lecture du fichier de topics MQTT : '{filePath}'")

        with open(filePath, "r") as file:
            topicList = json.load(file)

    except FileNotFoundError:
        message = f"[Topic] Fichier de topics MQTT introuvable : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message)

    except json.JSONDecodeError as e:
        message = f"[Topic] Fichier de topics MQTT invalide (JSON malformé) : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message) from e

    for item in topicList:
        if item["index"] == channelIndex:
            topic = item["topic"] + str(supporterId)

            logger.info(f"[Topic] Topic MQTT résolu : '{topic}' (channel='{channelIndex}', id={supporterId})")

            return topic

    message = f"[Topic] Aucun topic MQTT défini pour le channel '{channelIndex}'"
    logger.error(message)
    raise RuntimeError(message)

    return ""

# =============================================================================
#  Construction du point InfluxDB
# =============================================================================

##
# @brief Sépare les champs d'un message en tags et fields pour InfluxDB.
#
# @param data Dictionnaire de données (modifié en place : "type" retiré).
#
# @return tuple (tags, fields) où tags et fields sont des dictionnaires.
##
def buildPointInfluxDB(data):
    tags   = {}
    fields = {}

    # "type" est utilisé comme nom de mesure, pas comme tag ni field
    data.pop("t", None)

    ## @brief Clés identifiant le supporter ou la tribune, utilisées comme tags InfluxDB.
    TAG_KEYS = {"id", "n"}

    for key, value in data.items():
        if key in TAG_KEYS:
            tags[key] = value
        else:
            fields[key] = value

    return tags, fields
