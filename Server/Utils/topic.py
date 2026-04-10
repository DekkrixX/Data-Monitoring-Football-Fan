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

def getMQTTTopic(dataType, supporterId):
    ##
    # @brief Retourne le topic MQTT correspondant à un type de données et à un identifiant de supporter.
    #
    # @param dataType   Type de données (ex : "heart_rate").
    # @param supporterId Identifiant numérique du supporter.
    #
    # @return str Topic MQTT résolu.
    #
    # @throws RuntimeError Si le fichier est absent, invalide ou si le type est inconnu.
    ##

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
        if item["type"] == dataType:
            topic = item["topic"] + str(supporterId)

            logger.info(f"[Topic] Topic MQTT résolu : '{topic}' (type='{dataType}', id={supporterId})")

            return topic

    message = f"[Topic] Aucun topic MQTT défini pour le type de données '{dataType}'"
    logger.error(message)
    raise RuntimeError(message)


# =============================================================================
#  Construction du point InfluxDB
# =============================================================================

def buildPointInfluxDB(data):
    ##
    # @brief Sépare les champs d'un message en tags et fields pour InfluxDB.
    #
    # @param data Dictionnaire de données (modifié en place : "type" retiré).
    #
    # @return tuple (tags, fields) où tags et fields sont des dictionnaires.
    ##

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
