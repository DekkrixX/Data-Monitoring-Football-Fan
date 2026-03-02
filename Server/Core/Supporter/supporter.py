##
# @file supporter.py
#
# @brief Déclaration et implémentation de la classe Supporter.
#
# Regroupe l'identité d'un supporter et l'ensemble de ses données biométriques collectées en temps réel.
##


# =============================================================================
#  Import des bibliothèques
# =============================================================================

from Server.Core.Supporter.Data.heartRate import HeartRateData

# =============================================================================
#  Supporter
# =============================================================================

class Supporter:
    ##
    # @class Supporter
    #
    # @brief Représente un supporter identifié et ses données biométriques.
    ##

# =============================================================================
#  Constructeur
# ==============================================================================

    def __init__(self, supporterId, name):
        ##
        # @brief Construit un Supporter avec son identifiant et son nom.
        #
        # @param supporterId Identifiant unique du supporter (correspond à l'id
        #                    dans supporter.json).
        # @param name        Nom d'affichage du supporter.
        ##

        self.supporterId = supporterId  ##< @brief Identifiant unique du supporter.
        self.name        = name         ##< @brief Nom d'affichage du supporter.
        self.heartRate   = HeartRateData() ##< @brief Données de fréquence cardiaque du supporter.

# =============================================================================
#  Accesseurs
# =============================================================================

    def getId(self):
        ##
        # @brief Retourne l'identifiant unique du supporter.
        #
        # @return int Identifiant du supporter.
        ##
        return self.supporterId


    def getName(self):
        ##
        # @brief Retourne le nom d'affichage du supporter.
        #
        # @return str Nom du supporter.
        ##
        return self.name

# ==============================================================================
#  Ajout de données biométriques
# =============================================================================

    def addData(self, data):
        ##
        # @brief Distribue une nouvelle mesure vers le bon objet de données selon son type.
        #
        # @param data Dictionnaire contenant au minimum les clés "type" et la valeur associée.
        ##

        dataType = data.get("type")

        if dataType == "heart_rate":
            self.heartRate.addData(data["heart rate"])
        else:
            # Type inconnu : logué mais non bloquant
            from Server.Config.setting import Config
            if Config.DEBUG:
                print(f"[Supporter] Type de données inconnu ignoré : '{dataType}'")
