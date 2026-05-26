##
# @file tracker.py
#
# @brief Déclaration et implémentation de la classe Tracker.
#
# Regroupe les positions l'objet suivi en temps réel.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

from Server.Config.setting import Config
from Server.Utils.logger import Logger

# =============================================================================
#  Logger
# =============================================================================

logger = Logger("Serveur/Tracker")

# =============================================================================
#  Tracker
# =============================================================================

##
# @class Tracker
#
# @brief Suivi d'un objet avec ses positions en temps réel.
##
class Tracker:

# =============================================================================
#  Constructeur
# =============================================================================

    ##
    # @brief Construit un Tracker.
    #
    # @param trackingName Nom de l'objet tracké.
    # @param trackingZone Liste de point de la délimitation de la zone de tracking.
    ##
    def __init__(self, trackerId, trackingName, trackingZone):
        self.trackerId = trackerId       ##< @brief Id du tracker.
        self.trackingName = trackingName ##< @brief Nom de l'objet tracké.
        self.trackingZone = trackingZone ##< @brief Liste de point de la délimitation de la zone de tracking.
        self.currentPosition = None      ##< @brief Position courante de l'objet tracké.
        self.lastPositions = []          ##< @brief Liste des dernières position de l'objet tracké.

        return

# =============================================================================
#  Accesseurs
# =============================================================================

    ##
    # @brief Retourne l'id du tracker.
    #
    # @return int Id du tracker.
    ##
    def getId(self):
        return self.trackerId


    ##
    # @brief Retourne le nom de l'objet tracké.
    #
    # @return str Nom de l'objet tracké.
    ##
    def getName(self):
        return self.trackingName



    ##
    # @brief Retourne la position courante de l'objet.
    #
    # @return (int, int) Position de l'objet.
    ##
    def getPosition(self):
        return self.currentPosition



    ##
    # @brief Retourne les dernières positions de l'objet.
    #
    # @return List Dernière positions de l'objet.
    ##
    def getLastPositions(self):
        return self.lastPositions

# ==============================================================================
#  Nouvelle position
# ==============================================================================

    ##
    # @brief Met à jour la position de l'objet tracké.
    #
    # @param position La nouvelle position de l'objet.
    ##
    def addPosition(self, position):
        # Mise à jour de l'historique si la position courante existe
        if self.currentPosition:
            self.lastPositions.append(self.currentPosition)
        self.currentPosition = position
        # Suppression des données d'historique si la taille maximum est atteinte
        if len(self.lastPositions) > Config.MAX_POINTS_TRACKING:
            self.lastPositions.pop(0)

        logger.info(f"[Tracker] Nouvelle position courante: {self.currentPosition}")
        logger.info(f"[Tracker] Mise à jour de l'historique des positions: {self.lastPositions}")

        return
