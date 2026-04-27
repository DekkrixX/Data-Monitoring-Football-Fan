##
# @file postgresql.py
#
# @brief Wrapper de gestion d'un client PostgreSQL.
#
# Fournit une abstraction haut niveau pour se connecter à PostgreSQL,
# exécuter des requêtes SQL et gérer proprement le cycle de vie de la connexion.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

import psycopg
from psycopg.rows import dict_row

from Server.Utils.state import ConnectionState
from Server.Core.exception import ConnectionFailError, NotConnectionError
from Server.Utils.logger import Logger

# =============================================================================
#  Logger
# =============================================================================

logger = Logger("Serveur/PostgreSQL")

# =============================================================================
#  Client PostgreSQL
# =============================================================================

##
# @class PostgreSQLClientWrapper
#
# @brief Gestionnaire de connexion PostgreSQL basé sur psycopg.
##
class PostgreSQLClientWrapper:

# =============================================================================
#  Constructeur
# =============================================================================

    ##
    # @brief Construit un gestionnaire PostgreSQL avec les paramètres de connexion
    #
    # @param host         Hôte de la base de données.
    # @param port         Port de la base de données.
    # @param databasename Nom de la base de données.
    # @param user         Nom d'utilisateur de la base de données.
    # @param password     Mot de passe de la basse de données.
    ##
    def __init__(self, host, port, databasename, user, password):
        self.host         = host         ##< @brief Hôte de la base de données.
        self.port         = port         ##< @brief Port de la base de données.
        self.databasename = databasename ##< @brief Nom de la base de données.
        self.user         = user         ##< @brief Nom d'utilisateur de la base de données.
        self.password     = password ##< @brief Mot de passe de la base de données.

        self.conn = None   ##< @brief Connexion de la base de données.
        self.cursor = None ##< @brief Pointeur de données de la base de données.

        self.state = ConnectionState.DISCONNECTED ##< @brief État courant de la connexion.

        return

# =============================================================================
#  Connexion
# =============================================================================

    ##
    # @brief Ouvre une connexion PostgreSQL.
    #
    # @throws ConnectionFailError si la connexion échoue.
    ##
    def connect(self):
        logger.info(f"[PostgreSQL] Connexion à {self.host}:{self.port}/{self.databasename}")

        self.state = ConnectionState.CONNECTING

        try:
            self.conn = psycopg.connect(
                host=self.host,
                port=self.port,
                dbname=self.databasename,
                user=self.user,
                password=self.password,
                row_factory=dict_row
            )

            self.cursor = self.conn.cursor()
            self.state = ConnectionState.CONNECTED

            logger.info("[PostgreSQL] Connexion établie avec succès")

        except Exception as e:
            self.state = ConnectionState.ERROR
            logger.error(f"Échec de connexion PostgreSQL [{self.host}:{self.port}]")
            raise ConnectionFailError("PostgreSQL", self.host, self.port)

        return

# =============================================================================
#  Initialisation de la base de données
# =============================================================================

    ##
    # @brief Exécute un fichier SQL pour initialiser la base de données.
    #
    # @param filePath Chemin vers le fichier SQL.
    #
    # @throw NotConnectionError si la conexion PostgreSQL n'est pas active.
    # @throw FileNotFoundError si le fichier n'existe pas.
    ##
    def initDatabaseFromFile(self, filePath):
        if not self.isConnected():
            raise NotConnectionError("PostgreSQL")

        logger.info(f"[PostgreSQL] Initialisation depuis le fichier : {filePath}")

        try:
            with open(filePath, "r", encoding="utf-8") as file:
                sqlScript = file.read()

            # Découpe simple des requêtes (séparées par ;)
            queries = [q.strip() for q in sqlScript.split(";") if q.strip()]

            logger.info("[PostgreSQL] Exécution des requètes d'initialisation de la base de données")
            for query in queries:
                self.cursor.execute(query)

            self.conn.commit()

            logger.info("[PostgreSQL] Base de données initialisée avec succès")

        except FileNotFoundError:
            logger.error(f"[PostgreSQL] Fichier introuvable : {filePath}")
            raise

        except Exception as e:
            self.conn.rollback()
            logger.error("[PostgreSQL] Erreur lors de l'initialisation de la base")
            raise e

        return

# =============================================================================
#  Requêtes
# =============================================================================

    ##
    # @brief Exécute une requête SQL SELECT.
    #
    # @param query  Requête SQL.
    # @param params Paramètres optionnels.
    #
    # @return list résultats sous forme de dictionnaires.
    ##
    def fetch(self, query, params=None):
        if not self.isConnected():
            raise NotConnectionError("PostgreSQL")

        logger.info(f"[PostgreSQL] SELECT exécuté : {query}")

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    ##
    # @brief Exécute une requête SQL (INSERT / UPDATE / DELETE).
    #
    # @param query  Requête SQL.
    # @param params Paramètres optionnels.
    #
    # @return Une donnée si la requête demande de retourne une données.
    ##
    def execute(self, query, params=None, returning=False):
        response = None
        
        if not self.isConnected():
            raise NotConnectionError("PostgreSQL")

        logger.info(f"[PostgreSQL] EXECUTE : {query}")

        self.cursor.execute(query, params)
        if returning:
            response = self.cursor.fetchone()
        self.conn.commit()

        return response

# =============================================================================
#  Transactions
# =============================================================================

    ##
    # @brief Annule la transaction en cours.
    ##
    def rollback(self):
        if self.conn:
            logger.info("[PostgreSQL] Rollback transaction")
            self.conn.rollback()

        return

# =============================================================================
#  Fermeture
# =============================================================================

    ##
    # @brief Ferme proprement la connexion PostgreSQL.
    ##
    def close(self):
        logger.info("[PostgreSQL] Fermeture de la connexion")

        if not self.isConnected():
            return

        if self.cursor:
            self.cursor.close()

        if self.conn:
            self.conn.close()

        self.state = ConnectionState.DISCONNECTED

        return

# =============================================================================
#  État
# =============================================================================

    ##
    # @brief Vérifie si le client est connecté.
    #
    # @return bool
    ##
    def isConnected(self):
        return self.state == ConnectionState.CONNECTED
