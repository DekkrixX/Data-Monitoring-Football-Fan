##
# @file event.py
#
# @brief Gestion des évènements.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

import json
import os

from Server.Config.setting import Config
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/Event")

# =============================================================================
#  Charge une configuration
# =============================================================================

##
# @brief Charge un configuration de contôle d'évènement.
#
# @param config Le nom de la configuration à charger.
#
# @return La configuration de contrôle d'évènement.
##
def loadConfiguration(config):
    filePath = Config.PATH["data"] + "Event-Configuration/" + config + ".json"

    try:
        logger.info(f"[Event] Lecture du fichier de configuration : '{filePath}'")

        with open(filePath, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        message = f"[Event] Fichier de configuration introuvable : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message)

    except json.JSONDecodeError as e:
        message = f"[Event] Fichier de configuration invalide (JSON malformé) : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message) from e

    return ""



##
# @brief Renvoi la liste des configurations de contrôle d'évènement.
#
# @return La liste des configurations de contrôle d'évènement.
##
def getConfigurationList():
	configurationList = []
	
	for file in os.listdir(Config.PATH["data"] + "Event-Configuration"):
		config = loadConfiguration(file.replace(".json", ""))
		configurationList.append(config["name"])

	logger.info(f"[Event] Liste des configuration: {configurationList}")

	return configurationList
