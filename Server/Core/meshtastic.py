##
# @file meshtastic.py
#
# @brief Déclaration et implémentation de la classe MeshtasticClientWrapper.
#
# Fournit une abstraction haut niveau de l'interface série Meshtastic pour détecter automatiquement le port du nœud, établir la connexion et s'abonner aux paquets reçus via le système pubsub.
##


# =============================================================================
#  Import des bibliothèques
# =============================================================================

import time
import meshtastic
import meshtastic.serial_interface
from pubsub import pub
import serial.tools.list_ports

from Server.Config.setting import Config
from Server.Core.exception import ConnectionFailError, NotConnectionError, PortNotFoundError
from Server.Utils.state import ConnectionState
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/Meshtastic")

# =============================================================================
#  Client Meshtastic
# =============================================================================

class MeshtasticClientWrapper:
    ##
    # @class MeshtasticClientWrapper
    #
    # @brief Gestionnaire de connexion à un nœud Meshtastic via port série.
    ##

# =============================================================================
#  Constructeur
# =============================================================================

    def __init__(self, host, topic, onReceiveCallback=None, autoReconnect=False):
        ##
        # @brief Construit un gestionnaire Meshtastic ciblant un nœud donné.
        #
        # @param host              Adresse du nœud Meshtastic (utilisé pour les messages d'erreur).
        # @param topic             Topic pubsub auquel s'abonner (ex : "meshtastic.receive.text").
        # @param onReceiveCallback Callback utilisateur appelé à chaque paquet reçu (packet, interface).
        # @param autoReconnect     Reconnexion automatique (non implémenté, prévu).
        ##

        self.host          = host          ##< @brief Adresse du nœud Meshtastic.
        self.topic         = topic         ##< @brief Topic pubsub d'abonnement.
        self.userOnReceive = onReceiveCallback ##< @brief Callback utilisateur appelé à la réception d'un paquet.
        self.autoReconnect = autoReconnect ##< @brief Active la reconnexion automatique (non implémenté).

        self.client = None                              ##< @brief Interface série Meshtastic, initialisée dans connect().
        self.port   = None                              ##< @brief Port série détecté, renseigné dans _findPort().
        self.state  = ConnectionState.DISCONNECTED      ##< @brief État courant de la connexion.

# =============================================================================
#  Connexion
# =============================================================================

    def connect(self, timeout=30):
        ##
        # @brief Détecte le port série du nœud, ouvre la connexion et s'abonne au topic pubsub.
        #
        # @param timeout Durée maximale d'attente de connexion en secondes (défaut : 30).
        #
        # @throws ConnectionFailError Si l'une des étapes de connexion échoue.
        ##

        logger.info("[Meshtastic] Connexion au nœud Meshtastic")

        self.state = ConnectionState.CONNECTING

        try:
            self._findPort()

            self.client = meshtastic.serial_interface.SerialInterface(devPath=self.port)

            # Pause nécessaire : le noeud Meshtastic prend ~2s pour s'initialiser
            time.sleep(2)

            self._fetchNodeInfo()

            logger.info(f"[Meshtastic] Abonnement au topic pubsub '{self.topic}'")

            pub.subscribe(self._onReceive, self.topic)

            self.state = ConnectionState.CONNECTED

        except Exception as e:
            self.state = ConnectionState.ERROR
            logger.error(f"Échec de connexion à 'Meshtastic' [{self.host}:{self.port}]")
            raise ConnectionFailError("Meshtastic", self.host, self.port) from e


    def _findPort(self):
        ##
        # @brief Parcourt les ports série disponibles et sélectionne celui dont la description contient un des mots-clés définis dans MESHTASTIC_DESCRIPTION.
        #
        # @throws PortNotFoundError Si aucun port ne correspond aux mots-clés.
        ##

        logger.info("[Meshtastic] Recherche du port série du nœud")

        keywords = Config.MESHTASTIC_DESCRIPTION
        ports    = serial.tools.list_ports.comports()

        for port in ports:
            description = port.description.lower()
            for keyword in keywords:
                if keyword.lower() in description:
                    self.port = port.device
                    logger.info(f"[Meshtastic] Port trouvé : {self.port} ({port.description})")
                    return

        logger.error(f"Aucun port série trouvé pour 'Meshtastic'")
        raise PortNotFoundError("Meshtastic")


    def _fetchNodeInfo(self):
        ##
        # @brief Récupère et affiche les informations du nœud local connecté. Appelé automatiquement après l'ouverture de l'interface série.
        #
        # @throws RuntimeError Si la récupération des informations échoue.
        ##

        logger.info("[Meshtastic] Récupération des informations du noeud local")

        if self.state == ConnectionState.ERROR:
            return

        try:
            node_info = self.client.getMyNodeInfo()

            logger.info(f"[Meshtastic] Noeud local : {node_info}")

        except Exception as e:
            self.state = ConnectionState.ERROR
            message = "[Meshtastic] Échec de la récupération des informations du noeud local"
            logger.error(message)
            raise RuntimeError(message) from e

# =============================================================================
#  Callbacks internes
# =============================================================================

    def _onReceive(self, packet, interface):
        ##
        # @brief Callback interne appelé par pubsub à la réception d'un paquet Meshtastic.
        #
        # @param packet    Paquet Meshtastic reçu (dict).
        # @param interface Interface série source.
        ##

        logger.info(f"[Meshtastic] Paquet reçu depuis le noeud (topic='{self.topic}')")

        if self.userOnReceive:
            try:
                self.userOnReceive(packet, interface)
            except Exception as e:
                logger.warning(f"[Meshtastic] Erreur dans le callback onReceive utilisateur : {e}")

# =============================================================================
#  Boucle de traitement
# =============================================================================

    def waitForever(self):
        ##
        # @brief Maintient le programme actif indéfiniment en attendant les paquets Meshtastic.
        ##

        logger.info("[Meshtastic] En attente de paquets (boucle infinie)")

        while True:
            time.sleep(1)

# =============================================================================
#  Fermeture
# =============================================================================

    def close(self):
        ##
        # @brief Se désabonne du topic pubsub et ferme l'interface série proprement.
        #
        # @throws RuntimeError Si le désabonnement ou la fermeture de l'interface échoue.
        ##

        logger.info("[Meshtastic] Fermeture de la connexion au noeud")

        if self.state != ConnectionState.CONNECTED:
            return

        try:
            logger.info(f"[Meshtastic] Désabonnement du topic pubsub '{self.topic}'")

            pub.unsubscribe(self._onReceive, self.topic)

        except Exception as e:
            self.state = ConnectionState.ERROR
            message = f"[Meshtastic] Échec du désabonnement du topic '{self.topic}'"
            logger.error(message)
            raise RuntimeError(message) from e

        try:
            self.client.close()

        except Exception as e:
            self.state = ConnectionState.ERROR
            message = "[Meshtastic] Échec de la fermeture de l'interface série"
            logger.error(message)
            raise RuntimeError(message) from e

        self.state = ConnectionState.DISCONNECTED

        logger.info("[Meshtastic] Connexion fermée proprement")
