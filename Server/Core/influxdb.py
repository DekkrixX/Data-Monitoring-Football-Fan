##
# @file influxdb.py
#
# @brief Déclaration et implémentation de la classe InfluxDBClientWrapper.
#
# Fournit une abstraction haut niveau du client InfluxDB pour écrire des points de données dans un bucket, avec validation de la connexion via health check.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError

from Server.Utils.state import ConnectionState
from Server.Core.exception import ConnectionFailError, ConnectionRefuseError, NotConnectionError
from Server.Config.setting import Config
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/InfluxDB")

# =============================================================================
#  Client InfluxDB
# =============================================================================

##
# @class InfluxDBClientWrapper
#
# @brief Gestionnaire de connexion et d'écriture vers un serveur InfluxDB.
##
class InfluxDBClientWrapper:

# =============================================================================
#  Constructeur
# =============================================================================

    ##
    # @brief Construit un gestionnaire InfluxDB avec les paramètres de connexion.
    #
    # @param host       Hôte du serveur InfluxDB.
    # @param port       Port du serveur InfluxDB.
    # @param url        URL complète du serveur InfluxDB.
    # @param token      Token d'authentification InfluxDB.
    # @param org        Organisation InfluxDB cible.
    # @param bucket     Bucket InfluxDB cible pour l'écriture.
    # @param timeout    Timeout des requêtes en millisecondes (défaut : 50000).
    # @param enableGzip Active la compression gzip des requêtes (défaut : True).
    ##
    def __init__(self, host, port, url, token, org, bucket, timeout=50000, enableGzip=True):
        self.host       = host       ##< @brief Hôte du serveur InfluxDB (pour les messages d'erreur).
        self.port       = port       ##< @brief Port du serveur InfluxDB (pour les messages d'erreur).
        self.url        = url        ##< @brief URL complète du serveur InfluxDB.
        self.token      = token      ##< @brief Token d'authentification InfluxDB.
        self.org        = org        ##< @brief Organisation InfluxDB cible.
        self.bucket     = bucket     ##< @brief Bucket InfluxDB cible pour l'écriture.
        self.timeout    = timeout    ##< @brief Timeout des requêtes en millisecondes.
        self.enableGzip = enableGzip ##< @brief Active la compression gzip des requêtes.

        self.client   = None ##< @brief Instance InfluxDBClient, initialisée dans connect().
        self.writeApi = None ##< @brief API d'écriture InfluxDB, initialisée dans connect().
        self.queryApi = None ##< @brief API de requête InfluxDB, initialisée dans connect().

        self.state = ConnectionState.DISCONNECTED ##< @brief État courant de la connexion.

        return

# =============================================================================
#  Connexion
# =============================================================================

    ##
    # @brief Ouvre la connexion à InfluxDB et initialise les APIs d'écriture et de requête.
    #
    # @param validate Effectue un health check avant de valider la connexion (défaut : True).
    #
    # @throws ConnectionFailError Si la connexion ou le health check échoue.
    ##
    def connect(self, validate=True):
        logger.info(f"[InfluxDB] Connexion à {self.url}")

        self.state = ConnectionState.CONNECTING

        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org, timeout=self.timeout, enable_gzip=self.enableGzip)

            self.writeApi = self.client.write_api(write_options=SYNCHRONOUS)
            self.queryApi = self.client.query_api()

            if validate:
                self._validateConnection()

            self.state = ConnectionState.CONNECTED

        except (InfluxDBError, Exception) as e:
            self.state = ConnectionState.ERROR
            logger.error(f"Échec de connexion à 'InfluxDB' [{self.host}:{self.port}]");
            raise ConnectionFailError("InfluxDB", self.host, self.port) from e

        return



    ##
    # @brief Vérifie que le serveur InfluxDB est opérationnel via un health check.
    #
    # @throws ConnectionRefuseError Si le statut retourné n'est pas "pass".
    # @throws ConnectionFailError   Si la requête health check échoue.
    ##
    def _validateConnection(self):
        logger.info("[InfluxDB] Vérification de l'état du serveur (health check)")

        try:
            health = self.client.health()

            if health.status != "pass":
                logger.error(f"Connexion refusée par 'InfluxDB' [{self.host}:{self.port}]")
                raise ConnectionRefuseError("InfluxDB", self.host, self.port)

            if Config.DEBUG:
                logger.info(f"[InfluxDB] Health check OK (status='{health.status}')")

        except InfluxDBError as e:
            self.state = ConnectionState.ERROR
            logger.error(f"Échec de connexion à 'InfluxDB' [{self.host}:{self.port}]")
            raise ConnectionFailError("InfluxDB", self.host, self.port) from e

        return

# =============================================================================
#  Écriture
# =============================================================================

    ##
    # @brief Écrit un point de données dans le bucket InfluxDB configuré.
    #
    # @param measurement Nom de la mesure.
    # @param fields      Dictionnaire des valeurs à enregistrer {champ: valeur}.
    # @param tags        Dictionnaire des tags d'indexation {tag: valeur} (default : None).
    # @param timestamp   Timestamp en nanosecondes (default : None).
    #
    # @throws NotConnectionError Si le client n'est pas connecté.
    ##
    def send(self, measurement, fields, tags=None, timestamp=None):
        if not self.isConnected():
            logger.error()
            raise NotConnectionError("InfluxDB")

        point = Point(measurement)

        if tags:
            for key, value in tags.items():
                point.tag(key, value)

        for key, value in fields.items():
            point.field(key, value)

        if timestamp:
            point.time(timestamp, WritePrecision.NS)

        logger.info(f"[InfluxDB] Écriture du point '{measurement}'")
        if tags:
            for key, value in tags.items():
                logger.info(f"   tag   | {key} = {value}")
        for key, value in fields.items():
            logger.info(f"   field | {key} = {value}")

        self.writeApi.write(bucket=self.bucket, org=self.org, record=point)

        return

# =============================================================================
#  Fermeture
# =============================================================================

    ##
    # @brief Ferme l'API d'écriture et la connexion InfluxDB proprement.
    ##
    def close(self):
        logger.info("[InfluxDB] Fermeture de la connexion")

        if not self.isConnected():
            return

        if self.writeApi:
            self.writeApi.close()

        self.client.close()
        self.state = ConnectionState.DISCONNECTED

        logger.info("[InfluxDB] Connexion fermée proprement")

        return

# =============================================================================
#  État
# =============================================================================
    
    ##
    # @brief Indique si le client est actuellement connecté à InfluxDB.
    #
    # @return bool True si l'état est CONNECTED.
    # @return bool False sinon.
    ##
    def isConnected(self):
        return self.state == ConnectionState.CONNECTED
