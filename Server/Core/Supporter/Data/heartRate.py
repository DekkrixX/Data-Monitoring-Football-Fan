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

class HeartRateData:
    ##
    # @class HeartRateData
    #
    # @brief Stocke l'historique de fréquence cardiaque et calcule les statistiques en temps réel.
    ##

# =============================================================================
#  Constructeur
# =============================================================================

    def __init__(self):
        ##
        # @brief Initialise une instance HeartRateData sans aucune mesure.
        ##

        self._history = []    ##< @brief Historique complet des mesures en bpm.
        self._total   = 0     ##< @brief Somme cumulée des mesures pour le calcul de la moyenne.
        self._minimum = None  ##< @brief Valeur minimale enregistrée (None si aucune mesure).
        self._maximum = None  ##< @brief Valeur maximale enregistrée (None si aucune mesure).

# =============================================================================
#  Accesseurs
# =============================================================================

    def getLatest(self):
        ##
        # @brief Retourne la dernière mesure reçue.
        #
        # @return int  Dernière fréquence cardiaque en bpm.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        return self._history[-1] if self._history else None


    def getAverage(self):
        ##
        # @brief Retourne la moyenne de toutes les mesures, arrondie à l'entier inférieur.
        #
        # @return int  Moyenne en bpm.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        if not self._history:
            return None
        return self._total // len(self._history)


    def getMinimum(self):
        ##
        # @brief Retourne la valeur minimale enregistrée.
        #
        # @return int  Minimum en bpm.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        return self._minimum


    def getMaximum(self):
        ##
        # @brief Retourne la valeur maximale enregistrée.
        #
        # @return int  Maximum en bpm.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        return self._maximum


    def getHeartRate(self):
        ##
        # @brief Alias de getLatest(). Conservé pour compatibilité avec l'existant.
        #
        # @return int  Dernière fréquence cardiaque en bpm.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        return self.getLatest()

# =============================================================================
#  Ajout de données
# =============================================================================

    def addData(self, heartRate):
        ##
        # @brief Enregistre une nouvelle mesure et met à jour les statistiques.
        #
        # @param heartRate Fréquence cardiaque en bpm (entier).
        ##

        for hr in heartRate:
            if hr != 0:
                self._history.append(hr)
                self._total += hr

                if self._minimum is None or hr < self._minimum:
                    self._minimum = hr

                if self._maximum is None or hr > self._maximum:
                    self._maximum = hr
