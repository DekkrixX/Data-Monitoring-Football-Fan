##
# @file acoustic.py
#
# @brief Déclaration et implémentation de la classe AcousticData.
#
# Stocke l'historique acoustique d'une tribune de stade et calcule les statistiques en temps réel (dernière valeur, moyenne, minimum, maximum).
##


# =============================================================================
#  Données acoustiques
# =============================================================================

class AcousticData:
    ##
    # @class AcousticData
    #
    # @brief Stocke l'historique acoustique et calcule les statistiques en temps réel.
    ##

# =============================================================================
#  Constructeur
# =============================================================================

    def __init__(self):
        ##
        # @brief Initialise une instance AcousticData sans aucune mesure.
        ##

        self._history  = []        ##< @brief Historique complet des mesures.
        self._lastData = []        ##< @brief Dernier envoi de données par le capteur.
        self._total    = (0, 0, 0) ##< @brief Somme cumulée des mesures pour le calcul de la moyenne.
        self._minimum  = None      ##< @brief Valeur minimale enregistrée (None si aucune mesure).
        self._maximum  = None      ##< @brief Valeur maximale enregistrée (None si aucune mesure).

# =============================================================================
#  Accesseurs
# =============================================================================

    def getLasted(self):
        ##
        # @brief Retourne la dernière mesure reçue.
        #
        # @return float La dernière mesure acoustique.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        return self._history[-1] if self._history else None


    def getAverage(self):
        ##
        # @brief Retourne la moyenne de toutes les mesures.
        #
        # @return float La moyenne des données acoustiques.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        if not self._history:
            return None

        return tuple(self._total[i] / len(self._history) for i in range(3))


    def getMinimum(self):
        ##
        # @brief Retourne la valeur minimale enregistrée.
        #
        # @return float Le minimum des données acoustiques.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        return self._minimum


    def getMaximum(self):        
        ##
        # @brief Retourne la valeur maximale enregistrée.
        #
        # @return float Le maximum des données acoutiques.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        return self._maximum


    def getAccelerometer(self):
        ##
        # @brief Retourne le dernier envoi de donnée du capteur.
        #
        # @return [float] Dernier envoi de données acoustiques.
        ##
        return self._lastData

# =============================================================================
#  Ajout de données d'accélération
# =============================================================================

    def addData(self, acoustic):
        ##
        # @brief Enregistre une nouvelle mesure et met à jour les statistiques.
        #
        # @param acoustic Mesure acoustique.
        ##

        for a in acoustic:
            if a != (-1, -1, -1):
                self._history.append(a)
                self._total += a

                if self._minimum is None or hr < self._minimum:
                    self._minimum = a

                if self._maximum is None or hr > self._maximum:
                    self._maximum = a

        self._lastData = acoustic
        