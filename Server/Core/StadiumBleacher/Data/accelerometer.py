##
# @file accelerometer.py
#
# @brief Déclaration et implémentation de la classe AccelerometerData.
#
# Stocke l'historique de accélération d'une tribune de stade et calcule les statistiques en temps réel (dernière valeur, moyenne, minimum, maximum, vecteur d'accélération).
##


# =============================================================================
#  Données d'accélération
# =============================================================================

class AccelerometerData:
    ##
    # @class AccelerometerData
    #
    # @brief Stocke l'historique d'accélération et calcule les statistiques en temps réel.
    ##

# =============================================================================
#  Constructeur
# =============================================================================

    def __init__(self):
        ##
        # @brief Initialise une instance AccelerometerData sans aucune mesure.
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
        # @return (int, int, int) La dernière mesure de l'accélération sur les trois axes.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        return self._history[-1] if self._history else None


    def getAverage(self):
        ##
        # @brief Retourne la moyenne de toutes les mesures, arrondie à l'entier inférieur.
        #
        # @return (int, int, int) La moyenne de l'accélération sur les trois axes.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        if not self._history:
            return None

        return tuple(self._total[i] // len(self._history) for i in range(3))


    def getMinimum(self):
        ##
        # @brief Retourne la valeur minimale enregistrée.
        #
        # @return (int, int, int) Le minimum de l'accélération sur les trois axes.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        return self._minimum


    def getMaximum(self):        
        ##
        # @brief Retourne la valeur maximale enregistrée.
        #
        # @return (int, int, int) Le maximum de l'accélération sur les trois axes.
        # @return None Si aucune mesure n'a encore été reçue.
        ##
        return self._maximum


    def getAccelerometer(self):
        ##
        # @brief Retourne le dernier envoi de donnée du capteur.
        #
        # @return [(int, int, int)] Dernier envoi de l'accélération.
        ##
        return self._lastData


    def getLastAccelerationVectorX(self):
        ##
        # @brief Retourne le dernier vecteur accélération en x.
        #
        # @return (int, int) Vecteur accélération en x.
        ##
        return (self._history[-2][0], self._history[-1][0])


    def getLastAccelerationVectorY(self):
        ##
        # @brief Retourne le dernier vecteur accélération en y.
        #
        # @return (int, int) Vecteur accélération en y.
        ##
        return (self._history[-2][1], self._history[-1][1])


    def getLastAccelerationVectorZ(self):
        ##
        # @brief Retourne le dernier vecteur accélération en z.
        #
        # @return (int, int) Vecteur accélération en z.
        ##
        return (self._history[-2][2], self._history[-1][2])

# =============================================================================
#  Ajout de données d'accélération
# =============================================================================

    def addData(self, accelerometer):
        ##
        # @brief Enregistre une nouvelle mesure et met à jour les statistiques.
        #
        # @param accelerometer Mesure de l'accéléromètre.
        ##

        for a in accelerometer:
            if a != None:
                self._history.append(a)
                self._total = tuple(self._total[i] + a[i] for i in range(3))

                if self._minimum is None:
                    self._minimum = a
                else:
                    self._minimum = tuple(min(self._minimum[i], a[i]) for i in range(3))

                if self._maximum is None:
                    self._maximum = a
                else:
                    self._maximum = tuple(max(self._maximum[i], a[i]) for i in range(3))

        self._lastData = accelerometer
        