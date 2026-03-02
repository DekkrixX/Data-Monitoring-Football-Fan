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


# =============================================================================
#  Client InfluxDB
# =============================================================================

class InfluxDBClientWrapper:
    ##
    # @class InfluxDBClientWrapper
    #
    # @brief Gestionnaire de connexion et d'écriture vers un serveur InfluxDB.
    ##

# =============================================================================
#  Constructeur
# =============================================================================

    def __init__(self, host, port, url, token, org, bucket, timeout=50000, enableGzip=True):
        ##
        # @brief Construit un gestionnaire InfluxDB avec les paramètres de connexion.
        #
        # @param host       Hôte du serveur InfluxDB (utilisé pour les messages d'erreur).
        # @param port       Port du serveur InfluxDB (utilisé pour les messages d'erreur).
        # @param url        URL complète du serveur InfluxDB (ex : http://localhost:8086).
        # @param token      Token d'authentification InfluxDB.
        # @param org        Organisation InfluxDB cible.
        # @param bucket     Bucket InfluxDB cible pour l'écriture.
        # @param timeout    Timeout des requêtes en millisecondes (défaut : 50000).
        # @param enableGzip Active la compression gzip des requêtes (défaut : True).
        ##

        self.host        = host        ##< @brief Hôte du serveur InfluxDB (pour les messages d'erreur).
        self.port        = port        ##< @brief Port du serveur InfluxDB (pour les messages d'erreur).
        self.url         = url         ##< @brief URL complète du serveur InfluxDB.
        self.token       = token       ##< @brief Token d'authentification InfluxDB.
        self.org         = org         ##< @brief Organisation InfluxDB cible.
        self.bucket      = bucket      ##< @brief Bucket InfluxDB cible pour l'écriture.
        self.timeout     = timeout     ##< @brief Timeout des requêtes en millisecondes.
        self.enableGzip  = enableGzip  ##< @brief Active la compression gzip des requêtes.

        self.client   = None  ##< @brief Instance InfluxDBClient, initialisée dans connect().
        self.writeApi = None  ##< @brief API d'écriture InfluxDB, initialisée dans connect().
        self.queryApi = None  ##< @brief API de requête InfluxDB, initialisée dans connect().
        self.state    = ConnectionState.DISCONNECTED ##< @brief État courant de la connexion.

# =============================================================================
#  Connexion
# =============================================================================

    def connect(self, validate=True):
        ##
        # @brief Ouvre la connexion à InfluxDB et initialise les APIs d'écriture et de requête.
        #
        # @param validate True : effectue un health check avant de valider la connexion (défaut : True).
        #
        # @throws ConnectionFailError Si la connexion ou le health check échoue.
        ##

        if Config.DEBUG:
            print(f"[InfluxDB] Connexion à {self.url}")

        self.state = ConnectionState.CONNECTING

        try:
            self.client = InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org,
                timeout=self.timeout,
                enable_gzip=self.enableGzip
            )

            self.writeApi = self.client.write_api(write_options=SYNCHRONOUS)
            self.queryApi = self.client.query_api()

            if validate:
                self._validateConnection()

            self.state = ConnectionState.CONNECTED

        except (InfluxDBError, Exception) as e:
            self.state = ConnectionState.ERROR
            raise ConnectionFailError("InfluxDB", self.host, self.port) from e


    def _validateConnection(self):
        ##
        # @brief Vérifie que le serveur InfluxDB est opérationnel via un health check.
        #
        # @throws ConnectionRefuseError Si le statut retourné n'est pas "pass".
        # @throws ConnectionFailError   Si la requête health check échoue.
        ##

        if Config.DEBUG:
            print("[InfluxDB] Vérification de l'état du serveur (health check)")

        try:
            health = self.client.health()

            if health.status != "pass":
                raise ConnectionRefuseError("InfluxDB", self.host, self.port)

            if Config.DEBUG:
                print(f"[InfluxDB] Health check OK (status='{health.status}')")

        except InfluxDBError as e:
            self.state = ConnectionState.ERROR
            raise ConnectionFailError("InfluxDB", self.host, self.port) from e

# =============================================================================
#  Écriture
# =============================================================================

    def send(self, measurement, fields, tags=None, timestamp=None):
        ##
        # @brief Écrit un point de données dans le bucket InfluxDB configuré.
        #
        # @param measurement Nom de la mesure (table InfluxDB).
        # @param fields      Dictionnaire des valeurs à enregistrer {champ: valeur}.
        # @param tags        Dictionnaire des tags d'indexation {tag: valeur} (optionnel).
        # @param timestamp   Timestamp en nanosecondes (optionnel, InfluxDB utilise
        #                    l'heure courante si absent).
        #
        # @throws NotConnectionError Si le client n'est pas connecté.
        ##

        if not self.isConnected():
            raise NotConnectionError("InfluxDB")

        point = Point(measurement)

        if tags:
            for key, value in tags.items():
                point.tag(key, value)

        for key, value in fields.items():
            point.field(key, value)

        if timestamp:
            point.time(timestamp, WritePrecision.NS)

        if Config.DEBUG:
            print(f"[InfluxDB] Écriture du point '{measurement}'")
            if tags:
                for key, value in tags.items():
                    print(f"   tag   | {key} = {value}")
            for key, value in fields.items():
                print(f"   field | {key} = {value}")

        self.writeApi.write(bucket=self.bucket, record=point)

# =============================================================================
#  Fermeture
# =============================================================================

    def close(self):
        ##
        # @brief Ferme l'API d'écriture et la connexion InfluxDB proprement.
        ##

        if Config.DEBUG:
            print("[InfluxDB] Fermeture de la connexion")

        if not self.isConnected():
            return

        if self.writeApi:
            self.writeApi.close()

        self.client.close()
        self.state = ConnectionState.DISCONNECTED

        if Config.DEBUG:
            print("[InfluxDB] Connexion fermée proprement")

# =============================================================================
#  État
# =============================================================================

    def isConnected(self):
        ##
        # @brief Indique si le client est actuellement connecté à InfluxDB.
        #
        # @return bool True si l'état est CONNECTED, False sinon.
        ##
        return self.state == ConnectionState.CONNECTED
