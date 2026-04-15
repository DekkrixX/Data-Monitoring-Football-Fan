##
# @file acousticSimulator.py
#
# @brief Simulation de données acoustiques.
#
# Gestion de la simuation de données acoustiques.
##

# =============================================================================
#  Import
# =============================================================================

import random
import time

# =============================================================================
#  Simulateur
# =============================================================================

class AcousticSimulator:

# =============================================================================
#  Constructeur
# =============================================================================

    def __init__(self):
        self._state = "quiet"
        self._currentAcoustic = random.uniform(30, 40)
        self._targetAcoustic = self._currentAcoustic
        self._stateDuration = random.randint(30, 120)
        self._lastUpdate = time.time()

# =============================================================================
#  Changement d'état
# =============================================================================

    def _chooseNewState(self):
        r = random.random()

        if self._state == "quiet":
            self._state = "indoor"
        elif self._state == "indoor":
            self._state = "street" if r < 0.4 else "quiet"
        elif self._state == "street":
            self._state = "indoor" if r < 0.5 else "loud"
        elif self._state == "loud":
            self._state = "street"

        self.stateDuration = random.randint(20, 90)

# =============================================================================
#  Mise à jour des données
# =============================================================================

    def _updateTarget(self):
        if self._state == "quiet":
            self._targetAcoustic = random.uniform(30, 40)
        elif self._state == "indoor":
            self._targetAcoustic = random.uniform(40, 55)
        elif self._state == "street":
            self._targetAcoustic = random.uniform(55, 75)
        elif self._state == "loud":
            self._targetAcoustic = random.uniform(75, 100)

# =============================================================================
#  Gestion du bruit sur les données
# =============================================================================

    def _applyNoise(self):
        # bruit environnemental naturel
        return random.uniform(-1.5, 1.5)

    def _applySpike(self):
        # pics (porte qui claque, voix, etc.)
        if random.random() < 0.03:
            return random.uniform(5, 20)
        return 0

# =============================================================================
#  Génération d'une nouvelle données
# =============================================================================

    def getAcoustic(self):
        now = time.time()
        dt = now - self._lastUpdate
        self._lastUpdate = now

        self._stateDuration -= dt
        if self._stateDuration <= 0:
            self._chooseNewState()
            self._updateTarget()

        # inertie (transition progressive)
        alpha = 0.08
        self._currentAcoustic += (self._targetAcoustic - self._currentAcoustic) * alpha

        # bruit naturel
        self._currentAcoustic += self._applyNoise()

        # événements soudains
        self._currentAcoustic += self._applySpike()

        # limites réalistes
        self._currentAcoustic = max(20, min(120, self._currentAcoustic))

        return round(self._currentAcoustic, 1)
