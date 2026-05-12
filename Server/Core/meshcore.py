##
# @file meshcore.py
#
# @brief Déclaration et implémentation de la classe MeshcoreClientWrapper.
#
# Fournit une abstraction haut niveau de l'interface client Meshcore pour détecter automatiquement le port du noeud, établir la connexion et lire les messages reçus.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

import subprocess
import time
import re
import serial.tools.list_ports

from Server.Config.setting import Config
from Server.Core.exception import ConnectionFailError, NotConnectionError, PortNotFoundError
from Server.Utils.state import ConnectionState
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/Meshcore")

# =============================================================================
#  Client Meshcore
# =============================================================================

##
# @class MeshcoreClientWrapper
#
# @brief Gestionnaire de connexion à un noeud Meshcore via port série.
##
class MeshcoreClientWrapper:

# =============================================================================
#  Constructeur
# =============================================================================

    ##
    # @brief Construit un gestionnaire Meshcore ciblant un noeud donné.
    ##
    def __init__(self, onReceiveCallback=None):
        self.userOnReceive = onReceiveCallback    ##< @brief Callback utilisateur appelé à la réception d'un paquet.

        self.running = False                        ##< @brief Si le client est en écoute de messages.
        self.port    = None                         ##< @brief Port série détecté, renseigneé dans _findPort().
        self.state   = ConnectionState.DISCONNECTED ##< @brief État courant de la connexion.

        self._ansi_clean = re.compile(r"\x1b\[[0-9;]*m")
        self._pattern    = re.compile(r"ch(\d+)\s*\((\d+)\):\s*([^:]+):\s*(.*)")

# =============================================================================
#  Connexion
# =============================================================================

    ##
    # @brief Détecte le port série du noeud, ouvre la connexion et lis les messages.
    #
    # @throw ConnectionFailError Si l'une des étapes de connexion échoue.
    ##
    def connect(self):
        logger.info("[Meshcore] Connexion au noeud Meshcore")

        self.state = ConnectionState.CONNECTING

        try:
            self._find_port()
            self.state = ConnectionState.CONNECTED

        except Exception as e:
            self.state = ConnectionState.ERROR
            logger.error(f"Échec de connexion à 'Meshcore' [{self.port}]")
            raise ConnectionFailError("Meshcore", self.port) from e

        return



    ##
    # @brief Parcourt les ports série disponibles et sélectionne celui dont la description contient un des mots-clé définis dans MESHCORE_DESCRIPTION.
    #
    # @throw PortNotFoundError Si aucun port ne correspond aux mots-clés.
    ##
    def _find_port(self):
        logger.info("[Meshcore] Recherche du port série du noeud")

        keywords = Config.MESHCORE_DESCRIPTION
        ports = serial.tools.list_ports.comports()

        for port in ports:
            description = port.description.lower()
            for keyword in keywords:
                if keyword.lower() in description:
                    self.port = port.device
                    logger.info(f"[Meshcore] Port trouvé : {self.port} ({port.description})")
                    return

        logger.error("Aucun port série trouvé pour 'Meshcore'")
        raise PortNotFoundError("Meshcore")

        return

# =============================================================================
#  Boucle de traitement
# =============================================================================

    ##
    # @brief Maintient le programme actif indéfiniment en attendant les paquets Meshcore.
    ##
    def waitForever(self):
        logger.info("[Meshcore] En attente de paquets (boucle infinie)")

        CMD = ["meshcli", "-s", self.port, "recv"]

        self.running = True

        while self.running:
            result = subprocess.run(CMD, capture_output=True, text=True)

            lines = result.stdout.splitlines()

            for line in lines:
                clean_line = self._ansi_clean.sub("", line).strip()

                match = re.search(self._pattern, clean_line)

                if not match:
                    continue

                packet = {}
                packet["channel"] = int(match.group(1))
                packet["hop"] = int(match.group(2))
                packet["sender"] = match.group(3).strip()
                packet["payload"] = match.group(4).strip()

                logger.info(f"[Meshcore] Paquet reçu depuis le noeud (sender='{packet['sender']}')")

                if self.userOnReceive:
                    try:
                        self.userOnReceive(packet)
                    except Exception as e:
                        logger.warning(f"[Meshcore] Erreur dans le callback onReceive utilisateur : {e}")

        return

# =============================================================================
#  Fermeture
# =============================================================================

    ##
    # @brief Ferme la connexion au noeud Meshcore.
    ##
    def close(self):
        logger.info("[Meshcore] Fermeture de la connexion au noeud")
        self.running = False
        self.state = ConnectionState.DISCONNECTED
        logger.info("[Meshcore] Connexion fermée proprement")

        return
