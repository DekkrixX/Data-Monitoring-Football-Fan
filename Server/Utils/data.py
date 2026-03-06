##
# @file data.py
#
# @brief Utilitaires de lecture des données supporters et de formatage pour le client web.
#
# Fournit les accesseurs getNameOfSupporter() et getColorOfSupporter() qui lisent le fichier supporter.json, ainsi que createDataForClient() qui formate les données pour l'envoi via SocketIO.
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

logger = Logger("Serveur/Data")

# =============================================================================
#  Lecture du fichier supporter.json
# =============================================================================

def _loadSupporterFile():
    ##
    # @brief Charge et retourne le contenu du fichier supporter.json.
    #
    # @return list Liste de dictionnaires représentant les supporters.
    #
    # @throws RuntimeError Si le fichier est absent ou malformé.
    ##

    filePath = Config.PATH["data"] + "supporter.json"

    try:
        logger.info(f"[Data] Lecture du fichier supporters : '{filePath}'")

        with open(filePath, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        message = f"[Data] Fichier supporters introuvable : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message)

    except json.JSONDecodeError as e:
        message = f"[Data] Fichier supporters invalide (JSON malformé) : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message) from e


def _getSupporterField(supporterId, field):
    ##
    # @brief Retourne la valeur d'un champ donné pour le supporter identifié.
    #
    # @param supporterId Identifiant du supporter recherché.
    # @param field       Nom du champ à retourner (ex : "name", "color").
    #
    # @return Valeur du champ pour le supporter correspondant.
    #
    # @throws RuntimeError Si aucun supporter ne correspond à l'identifiant.
    ##

    supporters = _loadSupporterFile()

    for item in supporters:
        if item["id"] == supporterId:
            return item[field]

    message = f"[Data] Aucun supporter trouvé avec l'id '{supporterId}'"
    logger.error(message)
    raise RuntimeError(message)


# =============================================================================
#  Accesseurs publics
# =============================================================================

def getNameOfSupporter(supporterId):
    ##
    # @brief Retourne le nom du supporter correspondant à l'identifiant donné.
    #
    # @param supporterId Identifiant numérique du supporter.
    #
    # @return str Nom du supporter.
    #
    # @throws RuntimeError Si aucun supporter ne correspond à l'identifiant.
    ##
    return _getSupporterField(supporterId, "name")


def getColorOfSupporter(supporterId):
    ##
    # @brief Retourne la couleur du supporter correspondant à l'identifiant
    #        donné.
    #
    # @param supporterId Identifiant numérique du supporter.
    #
    # @return str Couleur du supporter (ex : "#FF0000").
    #
    # @throws RuntimeError Si aucun supporter ne correspond à l'identifiant.
    ##
    return _getSupporterField(supporterId, "color")


# =============================================================================
#  Formatage pour le client web
# =============================================================================

def createDataForClient(supporterId, name, color, heartRate):
    ##
    # @brief Construit le dictionnaire de données envoyé au client web via SocketIO.
    #
    # @param supporterId Identifiant du supporter.
    # @param name        Nom du supporter.
    # @param color       Couleur associée au supporter.
    # @param heartRate   Dernière fréquence cardiaque en bpm.
    #
    # @return dict Données formatées pour le client. Format : { "id": …, "name": …, "color": …, "heartRate": … }
    ##

    return {
        "id":        supporterId,
        "name":      name,
        "color":     color,
        "heartRate": heartRate,
    }
