##
# @file heartRateSimulator.py
#
# @brief Simulation de données de fréquences cardiaques.
#
# Gestion de la simuation de données de fréquences cardiaques.
##

# =============================================================================
#  Import
# =============================================================================

import random
import time
import math

# =============================================================================
#  Simulateur
# =============================================================================

class HeartRateSimulator:

# =============================================================================
#  Constructeur
# =============================================================================

    def __init__(self):
        self._state = "rest"
        self._currentRate = random.uniform(60, 75)
        self._targetRate = self._currentRate
        self._lastUpdate = time.time()
        self._stateDuration = 0

        return

# =============================================================================
#  Changement d'état
# =============================================================================

    def _chooseNewState(self):
        r = random.random()

        if self._state == "rest":
            if r < 0.1:
                self._state = "active"
                self._stateDuration = random.randint(20, 60)
        elif self._state == "active":
            if r < 0.2:
                self._state = "recovery"
                self._stateDuration = random.randint(10, 30)
        elif self._state == "recovery":
            if r < 0.3:
                self._state = "rest"
                self._stateDuration = random.randint(30, 120)

        return

# =============================================================================
#  Mise à jour des données
# =============================================================================

    def _updateTarget(self):
        if self._state == "rest":
            self._targetRate = random.uniform(60, 75)
        elif self._state == "active":
            self._targetRate = random.uniform(90, 140)
        elif self._state == "recovery":
            self._targetRate = random.uniform(65, 85)

        return

# =============================================================================
#  Gestion du bruit sur les données
# =============================================================================

    def _applyNoise(self):
        # HRV (variabilité cardiaque)
        return random.uniform(-1.5, 1.5)

    def _applySpike(self):
        # micro pics (stress, mouvement)
        if random.random() < 0.02:
            return random.uniform(5, 15)
        return 0

# =============================================================================
#  Génération d'une nouvelle donnée
# =============================================================================

    def getHeartRate(self):
        now = time.time()
        dt = now - self._lastUpdate
        self._lastUpdate = now

        # Gestion durée état
        self._stateDuration -= dt
        if self._stateDuration <= 0:
            self._chooseNewState()
            self._updateTarget()

        # Inertie (approche progressive de la cible)
        alpha = 0.05  # vitesse de réaction
        self._currentRate += (self._targetRate - self._currentRate) * alpha

        # Ajout du bruit physiologique
        self._currentRate += self._applyNoise()

        # Ajout de pics occasionnels
        self._currentRate += self._applySpike()

        # Limites réalistes
        self._currentRate = max(50, min(180, self._currentRate))

        return round(self._currentRate, 1)
