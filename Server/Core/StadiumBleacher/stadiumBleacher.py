##
# @file stadiumBleacher.py
#
# @brief Déclaration et implémentation de la classe StadiumBleacher.
#
# Regroupe l'identité d'une tribune du stade et l'ensemble de ses données collectées en temps réel.
##


# =============================================================================
#  Import des bibliothèques
# =============================================================================

from Server.Config.setting import Config
from Server.Core.stadiumBleacher.Data.accelermeterData import AccelermeterData
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/Stadium_Bleacher")

# =============================================================================
#  Tribune du stade
# =============================================================================

class StadiumBleacher:
    ##
    # @class StadiumBleacher
    #
    # @brief Représente une tribune du stade identifié et ses données.
    ##

# =============================================================================
#  Constructeur
# ==============================================================================

    def __init__(self, stadiumBleacherId, name):
        ##
        # @brief Construit une tribune de stade avec son identifiant et son nom.
        #
        # @param stadiumBleacherId  Identifiant unique de la tribune du stade (correspond à l'id dans stadiumBleacher.json).
        # @param name        Nom d'affichage de la tribune du stade.
        ##

        self.stadiumBleacherId = stadiumBleacherId  ##< @brief Identifiant unique de la tribune du stade.
        self.name              = name               ##< @brief Nom d'affichage de la tribune du stade.
        self.accelermeter      = AccelermeterData() ##< @brief Données de fréquence cardiaque du supporter.

# =============================================================================
#  Accesseurs
# =============================================================================

    def getId(self):
        ##
        # @brief Retourne l'identifiant unique de la tribune du stade.
        #
        # @return int Identifiant de la tribune du stade.
        ##
        return self.stadiumBleacherId


    def getName(self):
        ##
        # @brief Retourne le nom d'affichage de la tribune du stade.
        #
        # @return str Nom de la tribune du stade.
        ##
        return self.name

# ==============================================================================
#  Ajout de données
# =============================================================================

    def addData(self, data):
        ##
        # @brief Distribue une nouvelle mesure vers le bon objet de données selon son type.
        #
        # @param data Dictionnaire contenant au minimum les clés "type" et la valeur associée.
        ##

        dataType = data.get("t")

        if dataType == "accelermeter_gyroscope":
            self.accelermeter.addData(data["a"])
        else:
            # Type inconnu : logué mais non bloquant
            logger.warning(f"[StadiumBleacher] Type de données inconnu ignoré : '{dataType}'")
