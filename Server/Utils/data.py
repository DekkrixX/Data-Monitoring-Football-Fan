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

##
# @brief Charge et retourne le contenu du fichier supporter.json.
#
# @return list Liste de dictionnaires représentant les supporters.
#
# @throws RuntimeError Si le fichier est absent ou malformé.
##
def _loadSupporterFile():
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

    return



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
def _getSupporterField(supporterId, field):
    supporters = _loadSupporterFile()

    for item in supporters:
        if item["id"] == supporterId:
            return item[field]

    message = f"[Data] Aucun supporter trouvé avec l'id '{supporterId}'"
    logger.error(message)
    raise RuntimeError(message)

    return

# =============================================================================
#  Lecture du fichier stadiumBleacher.json
# =============================================================================

##
# @brief Charge et retourne le contenu du fichier stadiumBleacher.json.
#
# @return list Liste de dictionnaires représentant les tribunes.
#
# @throws RuntimeError Si le fichier est absent ou malformé.
##
def _loadStadiumBleacherFile():
    filePath = Config.PATH["data"] + "stadiumBleacher.json"

    try:
        logger.info(f"[Data] Lecture du fichier tribunes du stade : '{filePath}'")

        with open(filePath, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        message = f"[Data] Fichier tribunes du stade introuvable : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message)

    except json.JSONDecodeError as e:
        message = f"[Data] Fichier tribunes du stade invalide (JSON malformé) : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message) from e

    return



##
# @brief Retourne la valeur d'un champ donné pour la tribune identifié.
#
# @param stadiumBleacherId Identifiant de la tribune recherché.
# @param field             Nom du champ à retourner.
#
# @return Valeur du champ pour la tribune correspondant.
#
# @throws RuntimeError Si aucune tribune ne correspond à l'identifiant.
##
def _getStadiumBleacherField(stadiumBleacherId, field):
    stadiumBleachers = _loadStadiumBleacherFile()

    for item in stadiumBleachers:
        if item["id"] == stadiumBleacherId:
            return item[field]

    message = f"[Data] Aucune tribune de stade trouvé avec l'id '{stadiumBleacherId}'"
    logger.error(message)
    raise RuntimeError(message)

    return

# =============================================================================
#  Accesseurs publics
# =============================================================================

##
# @brief Retourne le nom du supporter correspondant à l'identifiant donné.
#
# @param supporterId Identifiant numérique du supporter.
#
# @return str Nom du supporter.
#
# @throws RuntimeError Si aucun supporter ne correspond à l'identifiant.
##
def getNameOfSupporter(supporterId):
    return _getSupporterField(supporterId, "name")



##
# @brief Retourne la couleur du supporter correspondant à l'identifiant donné.
#
# @param supporterId Identifiant numérique du supporter.
#
# @return str Couleur du supporter.
#
# @throws RuntimeError Si aucun supporter ne correspond à l'identifiant.
##
def getColorOfSupporter(supporterId):
    return _getSupporterField(supporterId, "color")



##
# @brief Retourne le nom de la tribune correspondant à l'identifiant donné.
#
# @param stadiumBleacherId Identifiant numérique de la tribune.
#
# @return str Nom de la tribune.
#
# @throws RuntimeError Si aucune tribune ne correspond à l'identifiant.
##
def getNameOfStadiumBleacher(stadiumBleacherId):
    return _getStadiumBleacherField(stadiumBleacherId, "name")



##
# @brief Retourne la couleur de la tribune correspondant à l'identifiant donné.
#
# @param stadiumBleacher Identifiant numérique de la tribune.
#
# @return str Couleur de la tribune.
#
# @throws RuntimeError Si aucune tribune ne correspond à l'identifiant.
##
def getColorOfStadiumBleacher(stadiumBleacherId):
    return _getStadiumBleacherField(stadiumBleacherId, "color")


# =============================================================================
#  Formatage pour le client web
# =============================================================================

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
def createSupporterHeartRateForClient(supporterId, name, color, heartRate):
    return {
        "id":        supporterId,
        "name":      name,
        "color":     color,
        "heartRate": heartRate,
    }



##
# @brief Construit le dictionnaire de données envoyé au client web via SocketIO.
#
# @param stadiumBleacherId Identifiant de la tribune.
# @param name              Nom de la tribune.
# @param color             Couleur associée à la tribune.
# @param accelerometer     Dernière mesure de l'accéléromètre.
#
# @return dict Données formatées pour le client. Format : { "id": …, "name": …, "color": …, "accelerometer": … }
##
def createStadiumBleacherAccelerometerForClient(stadiumBleacherId, name, color, accelerometer):
    return {
        "id":        stadiumBleacherId,
        "name":      name,
        "color":     color,
        "accelerometer": accelerometer,
    }



##
# @brief Construit le dictionnaire de données envoyé au client web via SocketIO.
#
# @param stadiumBleacherId Identifiant de la tribune.
# @param name              Nom de la tribune.
# @param color             Couleur associée à la tribune.
# @param acostic           Dernière mesure acoustic.
#
# @return dict Données formatées pour le client. Format : { "id": …, "name": …, "color": …, "acoustic": … }
##
def createStadiumBleacherAcousticForClient(stadiumBleacherId, name, color, acoustic):
    return {
        "id":        stadiumBleacherId,
        "name":      name,
        "color":     color,
        "acoustic":  acoustic,
    }
