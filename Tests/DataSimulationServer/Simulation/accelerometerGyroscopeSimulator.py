##
# @file accelerometerGyroscopeSimulator.py
#
# @brief Simulation de données d'un accéléromètre et gyroscope.
#
# Gestion de la simuation de données d'un accéléromètre et gyroscope.
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

class AccelerometerGyroscopeSimulator:

# =============================================================================
#  Constructeur
# =============================================================================

    def __init__(self):
        self._state = "idle"

        # Accélération (m/s²)
        self._ax = 0.0
        self._ay = 0.0
        self._az = 9.81  # gravité

        # Gyroscope (°/s)
        self._gx = 0.0
        self._gy = 0.0
        self._gz = 0.0

        self._lastUpdate = time.time()
        self._stateDuration = random.randint(30, 120)
        self._t = 0

# =============================================================================
#  Changement d'état
# =============================================================================

    def _chooseNewState(self):
        r = random.random()

        if self._state == "idle":
            self._state = "walking" if r < 0.5 else "active_motion"
        elif self._state == "walking":
            self._state = "idle" if r < 0.3 else "active_motion"
        elif self._state == "active_motion":
            self._state = "walking"

        self._stateDuration = random.randint(20, 100)

# =============================================================================
#  Mise à jour des données
# =============================================================================

    def _updateTarget(self):
        if self._state == "idle":
            self._ax = self._applyNoise(0.05)
            self._ay = self._applyNoise(0.05)
            self._az = 9.81 + self._applyNoise(0.1)

        elif self._state == "walking":
            step = math.sin(self.t * 6)
            self._ax = step * 1.5 + self._applyNoise(0.3)
            self._ay = self._applyNoise(0.5)
            self._az = 9.81 + abs(step) * 2 + self._applyNoise(0.3)

        elif self._state == "active_motion":
            self._ax = random.uniform(-8, 8)
            self._ay = random.uniform(-8, 8)
            self._az = random.uniform(0, 15)

        if self._state == "idle":
            self._gx = self._applyNoise(0.5)
            self._gy = self._applyNoise(0.5)
            self._gz = self._applyNoise(0.5)

        elif self._state == "walking":
            self._gx = math.sin(self.t * 3) * 30 + self._applyNoise(2)
            self._gy = self._applyNoise(5)
            self._gz = math.cos(self.t * 2) * 20 + self._applyNoise(2)

        elif self._state == "active_motion":
            self._gx = random.uniform(-180, 180)
            self._gy = random.uniform(-180, 180)
            self._gz = random.uniform(-250, 250)

# =============================================================================
#  Gestion du bruit sur les données
# =============================================================================

    def _applyNoise(self, scale=0.2):
        return random.uniform(-scale, scale)


# =============================================================================
#  Génération d'une nouvelle données
# =============================================================================

    def getAccelerometerGyroscope(self):
        now = time.time()
        dt = now - self._lastUpdate
        self._lastUpdate = now

        self._t += dt
        self._stateDuration -= dt

        if self._stateDuration <= 0:
            self._chooseNewState()

        self._updateTarget()

        return ([round(self._ax, 3), round(self._ay, 3), round(self._az, 3)], [round(self._gx, 2), round(self._gy, 2), round(self._gz, 2)])
