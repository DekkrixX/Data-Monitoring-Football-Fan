##
# @file positionSimulator.py
#
# @brief Simulation de données de position.
#
# Simule le déplacement réaliste d'une personne dans une zone délimitée.
##

# =============================================================================
#  Import
# =============================================================================

import random
import time
import math

# =============================================================================
#  Constantes comportementales
# =============================================================================

# Vitesses en cm/s
_SPEED_STOPPED   = 0.0
_SPEED_WALK_MIN  = 80.0
_SPEED_WALK_MAX  = 160.0
_SPEED_RUN_MIN   = 300.0
_SPEED_RUN_MAX   = 600.0

# Durées des états (secondes)
_STOP_MIN        = 1.0
_STOP_MAX        = 5.0
_WALK_MIN        = 3.0
_WALK_MAX        = 12.0
_RUN_MIN         = 1.0
_RUN_MAX         = 5.0

# Accélération / décélération (cm/s²)
_ACCEL           = 60.0
_TURN_RATE       = 1.2

# Probabilité de transition entre états (par seconde)
_PROB_STOP_TO_WALK  = 0.8
_PROB_WALK_TO_STOP  = 0.05
_PROB_WALK_TO_RUN   = 0.1
_PROB_RUN_TO_WALK   = 0.2
_PROB_RUN_TO_STOP   = 0.05

# Bruit de mesure (cm) — simule imprécision capteur
_NOISE_SIGMA     = 0.5

# Dépassement des bords autorisé, exprimé en fraction de la largeur/hauteur
# de la zone.  Ex : 0.1 = 10 % de débordement possible de chaque côté.
# Mettre à 0.0 pour un rebond strict sur le bord exact.
_OVERSHOOT_RATIO = 0.1

# =============================================================================
#  Simulateur
# =============================================================================

class PositionSimulator:

# =============================================================================
#  Constructeur
# =============================================================================

    def __init__(self, minX, maxX, minY, maxY):
        self._minX = float(minX)
        self._maxX = float(maxX)
        self._minY = float(minY)
        self._maxY = float(maxY)

        # Position initiale aléatoire au centre de la zone (±20%)
        cx = (minX + maxX) / 2.0
        cy = (minY + maxY) / 2.0
        span_x = (maxX - minX) * 0.2
        span_y = (maxY - minY) * 0.2
        self._x = random.uniform(cx - span_x, cx + span_x)
        self._y = random.uniform(cy - span_y, cy + span_y)

        # Cinématique
        self._angle  = random.uniform(0, math.pi * 2)   # Direction courante (rad)
        self._speed  = 0.0                               # Vitesse scalaire courante (cm/s)

        # Machine à états
        # États : "stopped", "walking", "running"
        self._state          = "stopped"
        self._targetSpeed    = 0.0
        self._targetAngle    = self._angle
        self._stateDuration  = random.uniform(_STOP_MIN, _STOP_MAX)
        self._stateElapsed   = 0.0

        self._lastUpdate = time.time()

        return

# =============================================================================
#  Machine à états
# =============================================================================

    def _transitionState(self, dt):
        self._stateElapsed += dt

        # Transition uniquement après la durée minimale de l'état
        if self._stateElapsed < self._stateDuration:
            return

        r = random.random()

        if self._state == "stopped":
            if r < _PROB_STOP_TO_WALK * dt:
                self._enterWalk()

        elif self._state == "walking":
            if r < _PROB_WALK_TO_STOP * dt:
                self._enterStop()
            elif r < (_PROB_WALK_TO_STOP + _PROB_WALK_TO_RUN) * dt:
                self._enterRun()
            else:
                # Changer de direction de temps en temps pendant la marche
                if random.random() < 0.3 * dt:
                    self._pickNewDirection()

        elif self._state == "running":
            if r < _PROB_RUN_TO_STOP * dt:
                self._enterStop()
            elif r < (_PROB_RUN_TO_STOP + _PROB_RUN_TO_WALK) * dt:
                self._enterWalk()

        return

    def _enterStop(self):
        self._state         = "stopped"
        self._targetSpeed   = _SPEED_STOPPED
        self._stateDuration = random.uniform(_STOP_MIN, _STOP_MAX)
        self._stateElapsed  = 0.0

    def _enterWalk(self):
        self._state         = "walking"
        self._targetSpeed   = random.uniform(_SPEED_WALK_MIN, _SPEED_WALK_MAX)
        self._stateDuration = random.uniform(_WALK_MIN, _WALK_MAX)
        self._stateElapsed  = 0.0
        self._pickNewDirection()

    def _enterRun(self):
        self._state         = "running"
        self._targetSpeed   = random.uniform(_SPEED_RUN_MIN, _SPEED_RUN_MAX)
        self._stateDuration = random.uniform(_RUN_MIN, _RUN_MAX)
        self._stateElapsed  = 0.0
        self._pickNewDirection()

# =============================================================================
#  Direction
# =============================================================================

    def _pickNewDirection(self):
        # Choisit une direction qui évite les bords (répulsion douce)
        cx = (self._minX + self._maxX) / 2.0
        cy = (self._minY + self._maxY) / 2.0

        # Vecteur vers le centre avec bruit
        to_center = math.atan2(cy - self._y, cx - self._x)
        noise     = random.gauss(0, math.pi / 3)

        # Plus on est loin du centre, plus on est attiré vers lui
        dx = self._x - cx
        dy = self._y - cy
        dist_ratio = math.sqrt(dx*dx + dy*dy) / (max(self._maxX - self._minX, self._maxY - self._minY) / 2.0)
        center_weight = min(dist_ratio * 1.5, 1.0)

        free_angle = self._angle + random.uniform(-math.pi / 2, math.pi / 2)
        self._targetAngle = to_center * center_weight + free_angle * (1.0 - center_weight) + noise * (1.0 - center_weight)

        return

# =============================================================================
#  Génération d'une nouvelle position
# =============================================================================

    def getPosition(self):
        now = time.time()
        dt  = min(now - self._lastUpdate, 0.1)
        self._lastUpdate = now

        # Mise à jour de la machine à états
        self._transitionState(dt)

        # Rotation progressive vers l'angle cible
        delta_angle = self._targetAngle - self._angle
        # Normalisation de l'écart entre -π et +π
        delta_angle = (delta_angle + math.pi) % (2 * math.pi) - math.pi
        max_turn    = _TURN_RATE * dt
        self._angle += max(-max_turn, min(max_turn, delta_angle))

        # Accélération / décélération progressive vers la vitesse cible
        delta_speed = self._targetSpeed - self._speed
        max_accel   = _ACCEL * dt
        self._speed += max(-max_accel, min(max_accel, delta_speed))
        self._speed  = max(0.0, self._speed)

        # Déplacement
        vx = math.cos(self._angle) * self._speed
        vy = math.sin(self._angle) * self._speed

        new_x = self._x + vx * dt
        new_y = self._y + vy * dt

        # Dépassement possible des bords (simule une imprécision de zone ou un
        # débordement momentané).  Au-delà de la marge, rebond strict.
        overshoot_x = (self._maxX - self._minX) * _OVERSHOOT_RATIO
        overshoot_y = (self._maxY - self._minY) * _OVERSHOOT_RATIO

        bounced = False
        if new_x < self._minX - overshoot_x:
            new_x = self._minX - overshoot_x
            self._angle = math.pi - self._angle
            bounced = True
        elif new_x > self._maxX + overshoot_x:
            new_x = self._maxX + overshoot_x
            self._angle = math.pi - self._angle
            bounced = True

        if new_y < self._minY - overshoot_y:
            new_y = self._minY - overshoot_y
            self._angle = -self._angle
            bounced = True
        elif new_y > self._maxY + overshoot_y:
            new_y = self._maxY + overshoot_y
            self._angle = -self._angle
            bounced = True

        if bounced:
            # Légère variation pour éviter les rebonds parfaitement symétriques
            self._angle += random.uniform(-0.2, 0.2)
            self._targetAngle = self._angle

        self._x = new_x
        self._y = new_y

        # Bruit de mesure gaussien (imprécision capteur)
        noise_x = random.gauss(0, _NOISE_SIGMA)
        noise_y = random.gauss(0, _NOISE_SIGMA)

        return {
            "x": int(round(self._x + noise_x)),
            "y": int(round(self._y + noise_y))
        }
