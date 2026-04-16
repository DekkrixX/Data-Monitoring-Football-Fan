##
# @file state.py
#
# @brief Définition des états de connexion utilisés par les clients externes.
#
# Ce fichier déclare l'énumération ConnectionState qui modélise le cycle de vie de la connexion d'un client (MQTT, InfluxDB, Meshtastic).
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

from enum import Enum

# =============================================================================
#  État de connexion
# =============================================================================

##
# @class ConnectionState
#
# @brief États possibles de la connexion d'un client à un service externe.
##
class ConnectionState(Enum):
    DISCONNECTED  = "disconnected" ##< Déconnecté proprement.
    CONNECTING    = "connecting"   ##< Tentative de connexion en cours.
    CONNECTED     = "connected"    ##< Connecté et opérationnel.
    RECONNECTING  = "reconnecting" ##< Reconnexion automatique en cours après une perte de connexion.
    ERROR         = "error"        ##< Erreur de connexion non récupérable.
