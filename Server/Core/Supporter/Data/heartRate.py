##
# @file heartRate.py
#
# @brief Déclaration et implémentation de la classe HeartRateData.
#
# Stocke l'historique de fréquence cardiaque d'un supporter et calcule les statistiques en temps réel (dernière valeur, moyenne, minimum, maximum).
##


# =============================================================================
#  Données de fréquence cardiaque
# =============================================================================

##
# @class HeartRateData
#
# @brief Stocke l'historique de fréquence cardiaque et calcule les statistiques en temps réel.
##
class HeartRateData:

# =============================================================================
#  Constructeur
# =============================================================================

    ##
    # @brief Initialise une instance HeartRateData sans aucune mesure.
    ##
    def __init__(self):
        self._history  = []   ##< @brief Historique complet des mesures en bpm.
        self._lastData = []   ##< @brief Dernier envoi de données par le capteur.
        self._total    = 0    ##< @brief Somme cumulée des mesures pour le calcul de la moyenne.
        self._minimum  = None ##< @brief Valeur minimale enregistrée (None si aucune mesure).
        self._maximum  = None ##< @brief Valeur maximale enregistrée (None si aucune mesure).

        return

# =============================================================================
#  Accesseurs
# =============================================================================

    ##
    # @brief Retourne la dernière mesure reçue.
    #
    # @return int  Dernière fréquence cardiaque en bpm.
    # @return None Si aucune mesure n'a encore été reçue.
    ##
    def getLasted(self):
        return self._history[-1] if self._history else None



    ##
    # @brief Retourne la moyenne de toutes les mesures, arrondie à l'entier inférieur.
    #
    # @return int  Moyenne en bpm.
    # @return None Si aucune mesure n'a encore été reçue.
    ##
    def getAverage(self):
        if not self._history:
            return None
        return round(self._total / len(self._history), 1)



    ##
    # @brief Retourne la valeur minimale enregistrée.
    #
    # @return int  Minimum en bpm.
    # @return None Si aucune mesure n'a encore été reçue.
    ##
    def getMinimum(self):
        return self._minimum



    ##
    # @brief Retourne la valeur maximale enregistrée.
    #
    # @return int  Maximum en bpm.
    # @return None Si aucune mesure n'a encore été reçue.
    ##
    def getMaximum(self):
        return self._maximum



    ##
    # @brief Retourne le dernier envoi de donnée du capteur.
    #
    # @return [int] Dernier envoi de la fréquence cardiaque en bpm.
    ##
    def getHeartRate(self):
        return self._lastData

# =============================================================================
#  Ajout de données de fréquence cardiaque
# =============================================================================

    ##
    # @brief Enregistre une nouvelle mesure et met à jour les statistiques.
    #
    # @param heartRate Fréquence cardiaque en bpm (entier).
    ##
    def addData(self, heartRate):
        for hr in heartRate:
            if hr != None:
                self._history.append(hr)
                self._total += hr

                if self._minimum is None or hr < self._minimum:
                    self._minimum = hr

                if self._maximum is None or hr > self._maximum:
                    self._maximum = hr

        self._lastData = heartRate

        return
