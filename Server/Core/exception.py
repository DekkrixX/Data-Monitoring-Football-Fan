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

##
# @class EnvironmentVariableError
#
# @brief Levée quand une variable d'environnement requise est absente ou vide dans le fichier .env.
##
class EnvironmentVariableError(Exception):
    ##
    # @brief Construit l'exception avec le nom de la variable manquante.
    #
    # @param variable Nom de la variable d'environnement non définie.
    ##
    def __init__(self, variable):
        super().__init__(f"Variable d'environnement manquante : '{variable}' n'est pas définie dans le fichier .env")

        return

# =============================================================================
#  Exception : échec de connexion
# =============================================================================

##
# @class ConnectionFailError
#
# @brief Levée quand la tentative de connexion à un service échoue.
##
class ConnectionFailError(Exception):
    ##
    # @brief Construit l'exception avec le nom du service et son adresse.
    #
    # @param name Nom du service (ex : "MQTT", "InfluxDB").
    # @param host Hôte cible.
    # @param port Port cible.
    ##
    def __init__(self, name, host, port):
        super().__init__(f"Échec de connexion à '{name}' [{host}:{port}]")

        return

# =============================================================================
#  Exception : connexion refusée
# =============================================================================

##
# @class ConnectionRefuseError
#
# @brief Levée quand le service refuse explicitement la connexion.
##
class ConnectionRefuseError(Exception):
    ##
    # @brief Construit l'exception avec le nom du service et son adresse.
    #
    # @param name Nom du service.
    # @param host Hôte cible.
    # @param port Port cible.
    ##
    def __init__(self, name, host, port):
        super().__init__(f"Connexion refusée par '{name}' [{host}:{port}]")

        return

# =============================================================================
#  Exception : opération sans connexion établie
# =============================================================================

##
# @class NotConnectionError
#
# @brief Levée quand une opération est tentée alors que le client n'est pas connecté au service.
##
class NotConnectionError(Exception):
    ##
    # @brief Construit l'exception avec le nom du service non connecté.
    #
    # @param name Nom du service.
    ##
    def __init__(self, name):
        super().__init__(f"Opération impossible : la connexion à '{name}' n'est pas établie")

        return

# =============================================================================
#  Exception : port série introuvable
# =============================================================================

##
# @class PortNotFoundError
#
# @brief Levée quand aucun port série correspondant au périphérique n'est trouvé lors de l'énumération des ports disponibles.
##
class PortNotFoundError(Exception):

    ##
    # @brief Construit l'exception avec le nom du périphérique recherché.
    #
    # @param name Nom du périphérique (ex : "Meshtastic").
    ##
    def __init__(self, name):
        super().__init__(f"Aucun port série trouvé pour '{name}'")

        return
