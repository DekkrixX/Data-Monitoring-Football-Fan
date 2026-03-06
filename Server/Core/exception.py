##
# @file exception.py
#
# @brief Définition des exceptions personnalisées du projet.
#
# Chaque exception correspond à un cas d'erreur précis rencontré lors de la connexion ou de l'utilisation des services externes (MQTT, InfluxDB, Meshtastic) ou lors du chargement de la configuration.
##


# =============================================================================
#  Exception : variable d'environnement manquante
# =============================================================================

class EnvironmentVariableError(Exception):
    ##
    # @class EnvironmentVariableError
    #
    # @brief Levée quand une variable d'environnement requise est absente ou vide dans le fichier .env.
    ##

    def __init__(self, variable):
        ##
        # @brief Construit l'exception avec le nom de la variable manquante.
        #
        # @param variable Nom de la variable d'environnement non définie.
        ##
        super().__init__(f"Variable d'environnement manquante : '{variable}' n'est pas définie dans le fichier .env")


# =============================================================================
#  Exception : échec de connexion
# =============================================================================

class ConnectionFailError(Exception):
    ##
    # @class ConnectionFailError
    #
    # @brief Levée quand la tentative de connexion à un service échoue.
    ##

    def __init__(self, name, host, port):
        ##
        # @brief Construit l'exception avec le nom du service et son adresse.
        #
        # @param name Nom du service (ex : "MQTT", "InfluxDB").
        # @param host Hôte cible.
        # @param port Port cible.
        ##
        super().__init__(f"Échec de connexion à '{name}' [{host}:{port}]")


# =============================================================================
#  Exception : connexion refusée
# =============================================================================

class ConnectionRefuseError(Exception):
    ##
    # @class ConnectionRefuseError
    #
    # @brief Levée quand le service refuse explicitement la connexion.
    ##

    def __init__(self, name, host, port):
        ##
        # @brief Construit l'exception avec le nom du service et son adresse.
        #
        # @param name Nom du service.
        # @param host Hôte cible.
        # @param port Port cible.
        ##
        super().__init__(f"Connexion refusée par '{name}' [{host}:{port}]")


# =============================================================================
#  Exception : opération sans connexion établie
# =============================================================================

class NotConnectionError(Exception):
    ##
    # @class NotConnectionError
    #
    # @brief Levée quand une opération est tentée alors que le client n'est pas connecté au service.
    ##

    def __init__(self, name):
        ##
        # @brief Construit l'exception avec le nom du service non connecté.
        #
        # @param name Nom du service.
        ##
        super().__init__(f"Opération impossible : la connexion à '{name}' n'est pas établie")


# =============================================================================
#  Exception : port série introuvable
# =============================================================================

class PortNotFoundError(Exception):
    ##
    # @class PortNotFoundError
    #
    # @brief Levée quand aucun port série correspondant au périphérique n'est trouvé lors de l'énumération des ports disponibles.
    ##

    def __init__(self, name):
        ##
        # @brief Construit l'exception avec le nom du périphérique recherché.
        #
        # @param name Nom du périphérique (ex : "Meshtastic").
        ##
        super().__init__(f"Aucun port série trouvé pour '{name}'")
