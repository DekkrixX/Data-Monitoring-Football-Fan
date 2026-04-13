##
# @file setting.py
#
# @brief Configuration globale de l'application.
#
# Charge les variables d'environnement depuis le fichier .env situé à la racine du projet et les expose via la classe Config. Appeler Config.validate() au démarrage pour s'assurer que toutes les variables requises sont définies.
##


# =============================================================================
#  Import des bibliothèques
# =============================================================================

import os
from pathlib import Path
from dotenv import load_dotenv

from Server.Core.exception import EnvironmentVariableError

# =============================================================================
#  Chargement du fichier .env
# =============================================================================

## @brief Répertoire contenant ce fichier (Server/Config/).
_current_dir  = Path(__file__).parent
## @brief Racine du projet (deux niveaux au-dessus de ce fichier).
_project_path = _current_dir.parent.parent
## @brief Chemin absolu vers le fichier .env à la racine du projet.
_env_path     = _project_path / ".env"

load_dotenv(dotenv_path=_env_path)


# =============================================================================
#  Fonctions utilitaires internes
# =============================================================================

def _get_bool(key, default="false"):
    ##
    # @brief Lit une variable d'environnement et la convertit en booléen.
    #
    # @param key     Nom de la variable d'environnement.
    # @param default Valeur par défaut si la variable est absente (défaut : "false").
    #
    # @return bool True si la valeur vaut "true" ou "1" (insensible à la casse), False sinon.
    ##
    return os.getenv(key, default).strip().lower() in ("true", "1")


# =============================================================================
#  Configuration
# =============================================================================

class Config:
    ##
    # @class Config
    #
    # @brief Centralise tous les paramètres de l'application chargés depuis
    #        le fichier .env.
    ##

# =============================================================================
#  Général
# =============================================================================

    APP     = os.getenv("APP",     None)  ##< Nom de l'application.
    ENV     = os.getenv("ENV",     None)  ##< Environnement d'exécution ("development", "production"…).
    VERSION = os.getenv("VERSION", None)  ##< Version de l'application.
    DEBUG   = _get_bool("DEBUG")          ##< Activation du mode debug.

# =============================================================================
#  Chemins
# =============================================================================

    ## @brief Chemins absolus vers les répertoires utilisés par l'application.
    PATH = {
        "/":             _project_path,
        "documentation": os.path.join(_project_path, os.getenv("DOCUMENTATION_PATH", "")),
        "data":          os.path.join(_project_path, os.getenv("DATA_PATH",          "")),
        "image":         os.path.join(_project_path, os.getenv("IMAGE_PATH",         "")),
        "log":           os.path.join(_project_path, os.getenv("LOG_PATH",           "")),
    }

# =============================================================================
#  Dashboard
# =============================================================================

    SECRET_KEY      = os.getenv("SECRET_KEY",      None)  ##< Clé secrète Flask.
    DASHBOARD_HOST  = os.getenv("DASHBOARD_HOST",  None)  ##< Hôte d'écoute du dashboard.
    DASHBOARD_PORT  = int(os.getenv("DASHBOARD_PORT", 0)) ##< Port d'écoute du dashboard.
    MAX_DATA_POINTS = 100                                 ##< Nombre maximal de points conservés en mémoire par supporter.

# =============================================================================
#  MQTT
# =============================================================================

    MQTT_BROKER_HOST      = os.getenv("MQTT_BROKER_HOST",      None)        ##< Hôte du broker MQTT.
    MQTT_BROKER_PORT      = int(os.getenv("MQTT_BROKER_PORT",      0))      ##< Port du broker MQTT.
    MQTT_BROKER_TOPICS    = os.getenv("MQTT_BROKER_TOPICS", "").split(",")  ##< Liste des topics MQTT souscrits.
    MQTT_BROKER_KEEPALIVE = int(os.getenv("MQTT_BROKER_KEEPALIVE", 0))      ##< Intervalle de keep-alive MQTT en secondes.
    MQTT_BROKER_QOS       = int(os.getenv("MQTT_BROKER_QOS",       0))      ##< Niveau de qualité de service MQTT (0, 1 ou 2).

# =============================================================================
#  InfluxDB
# =============================================================================

    INFLUXDB_HOST    = os.getenv("INFLUXDB_HOST",    None)   ##< Hôte du serveur InfluxDB (pour les messages d'erreur).
    INFLUXDB_PORT    = int(os.getenv("INFLUXDB_PORT", 0))    ##< Port du serveur InfluxDB (pour les messages d'erreur).
    INFLUXDB_ADRESS  = os.getenv("INFLUXDB_ADRESS",  None)   ##< URL complète du serveur InfluxDB (ex : http://localhost:8086).
    INFLUXDB_TOKEN   = os.getenv("INFLUXDB_TOKEN",   None)   ##< Token d'authentification InfluxDB.
    INFLUXDB_ORG     = os.getenv("INFLUXDB_ORG",     None)   ##< Organisation InfluxDB cible.
    INFLUXDB_BUCKET  = os.getenv("INFLUXDB_BUCKET",  None)   ##< Bucket InfluxDB cible pour l'écriture.

# =============================================================================
#  Meshtastic
# =============================================================================

    MESHTASTIC_PORT        = os.getenv("MESHTASTIC_PORT",        None)          ##< Port série du nœud Meshtastic (inutilisé si détection automatique).
    MESHTASTIC_HOST        = os.getenv("MESHTASTIC_HOST",        None)          ##< Hôte du nœud Meshtastic (pour les messages d'erreur).
    MESHTASTIC_TOPIC       = os.getenv("MESHTASTIC_TOPIC",       None)          ##< Topic pubsub Meshtastic (ex : "meshtastic.receive.text").
    MESHTASTIC_DESCRIPTION = os.getenv("MESHTASTIC_DESCRIPTION", "").split(",") ##< Mots-clés de description de port série pour la détection automatique du noeud.

# =============================================================================
#  Grafana
# =============================================================================

    GRAFANA_HOST = os.getenv("GRAFANA_HOST", None)         ##< Hôte du serveur Grafana.
    GRAFANA_PORT = int(os.getenv("GRAFANA_PORT", 0))       ##< Port du serveur Grafana.

# =============================================================================
#  Délais d'échantillonage des capteurs
# =============================================================================

    SENSOR_DELAY = float(os.getenv("SENSOR_DELAY", 0)) ##< Délais d'échantillonage des capteurs.


    @classmethod
    def validate(cls):
        ##
        # @brief Vérifie que toutes les variables d'environnement requises sont définies et non vides.
        #
        # @throws EnvironmentVariableError À la première variable manquante ou vide détectée.
        ##

        required = {
            # Général
            "APP":     cls.APP,
            "ENV":     cls.ENV,
            "VERSION": cls.VERSION,

            # Chemins
            "DOCUMENTATION_PATH": cls.PATH["documentation"],
            "DATA_PATH":          cls.PATH["data"],
            "IMAGE_PATH":         cls.PATH["image"],
            "LOG_PATH":           cls.PATH["log"],

            # Dashboard
            "SECRET_KEY":     cls.SECRET_KEY,
            "DASHBOARD_HOST": cls.DASHBOARD_HOST,
            "DASHBOARD_PORT": cls.DASHBOARD_PORT,

            # MQTT
            "MQTT_BROKER_HOST":      cls.MQTT_BROKER_HOST,
            "MQTT_BROKER_PORT":      cls.MQTT_BROKER_PORT,
            "MQTT_BROKER_TOPICS":    cls.MQTT_BROKER_TOPICS,
            "MQTT_BROKER_KEEPALIVE": cls.MQTT_BROKER_KEEPALIVE,
            "MQTT_BROKER_QOS":       cls.MQTT_BROKER_QOS,

            # InfluxDB
            "INFLUXDB_HOST":   cls.INFLUXDB_HOST,
            "INFLUXDB_PORT":   cls.INFLUXDB_PORT,
            "INFLUXDB_ADRESS": cls.INFLUXDB_ADRESS,
            "INFLUXDB_TOKEN":  cls.INFLUXDB_TOKEN,
            "INFLUXDB_ORG":    cls.INFLUXDB_ORG,
            "INFLUXDB_BUCKET": cls.INFLUXDB_BUCKET,

            # Meshtastic
            "MESHTASTIC_PORT":        cls.MESHTASTIC_PORT,
            "MESHTASTIC_HOST":        cls.MESHTASTIC_HOST,
            "MESHTASTIC_TOPIC":       cls.MESHTASTIC_TOPIC,
            "MESHTASTIC_DESCRIPTION": cls.MESHTASTIC_DESCRIPTION,

            # Grafana
            "GRAFANA_HOST": cls.GRAFANA_HOST,
            "GRAFANA_PORT": cls.GRAFANA_PORT,

            # Délais d'échantillonage des capteurs
            "SENSOR_DELAY": cls.SENSOR_DELAY
        }

        if cls.DEBUG:
            print("[Config] Validation des variables d'environnement")

        for key, value in required.items():
            if value is None or value == "" or value == [""]:
                raise EnvironmentVariableError(key)

        if cls.DEBUG:
            print("[Config] Toutes les variables d'environnement sont définies")
