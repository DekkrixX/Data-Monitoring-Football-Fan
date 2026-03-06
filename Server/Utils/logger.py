##
# @file logger.py
#
# @brief Système de journalisation du serveur.
#
# Fournit la classe Logger permettant d'écrire des messages horodatés dans un fichier de log et de les afficher en console avec coloration ANSI selon le niveau de sévérité. L'écriture fichier est thread-safe grâce à un threading.Lock().
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

import threading
import os
from datetime import datetime

from Server.Config.setting import Config

# =============================================================================
#  Classe
# =============================================================================

class Logger:
    ##
    # @class Logger
    #
    # @brief Journaliseur horodaté avec sortie fichier et console colorée.
    ##

# =============================================================================
#  Constructeur
# =============================================================================

    def __init__(self, name):
        ##
        # @brief Initialise le logger avec son nom et son fichier de sortie.
        #
        # @param name  Nom du logger, utilisé comme nom de fichier de log
        ##

        self._name  = name                                ##< @brief Nom du logger.
        self._file  = Config.PATH["log"] + name + ".log"  ##< @brief Chemin complet du fichier de log.
        self._lock  = threading.Lock()                    ##< @brief Mutex garantissant l'exclusivité des écritures fichier entre threads.

        self._reset  = "\033[0m"                          ##< @brief Code ANSI de réinitialisation de couleur.
        self._white  = "\033[37m"                         ##< @brief Code ANSI couleur blanche (niveau INFO).
        self._yellow = "\033[33m"                         ##< @brief Code ANSI couleur jaune (niveau WARNING).
        self._red    = "\033[31m"                         ##< @brief Code ANSI couleur rouge (niveau ERROR).

        return

# =============================================================================
#  Méthodes privées
# =============================================================================

    def _logIn(self, timestamp, level, message):
        ##
        # @brief Écrit une entrée de log dans le fichier de façon thread-safe.
        #
        # @param timestamp Horodatage formaté de l'entrée.
        # @param level     Niveau de sévérité ("INFO", "WARNING", "ERROR").
        # @param message   Corps du message à journaliser.
        ##

        log = f"[{timestamp}] [{level}] {message}.\n"

        # Création du répertoire de log si inexistant
        os.makedirs(os.path.dirname(self._file), exist_ok=True)

        # Écriture thread-safe avec synchronisation disque forcée
        with self._lock:
            with open(self._file, "a", encoding="utf-8") as f:
                f.write(log)
                f.flush()
                os.fsync(f.fileno())

        return

    def _writeDebug(self, timestamp, level, message):
        ##
        # @brief Affiche un message en console avec coloration ANSI selon le niveau.
        #
        #
        # @param timestamp Horodatage formaté du message.
        # @param level     Niveau de sévérité ("INFO", "WARNING", "ERROR").
        # @param message   Corps du message à afficher.
        ##

        match level:
            case "WARNING":
                color = self._yellow
            case "ERROR":
                color = self._red
            case _:
                color = self._white

        print(f"{color}[{timestamp}] [{level}] {message}.{self._reset}")

        return

# =============================================================================
#  Méthodes publiques
# =============================================================================

    def info(self, message):
        ##
        # @brief Journalise un message de niveau INFO.
        #
        # @param message Message informatif à journaliser.
        ##

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._logIn(timestamp, "INFO", message)

        if Config.DEBUG:
            self._writeDebug(timestamp, "INFO", message)

        return

    def warning(self, message):
        ##
        # @brief Journalise un message de niveau WARNING.
        #
        # @param message Message d'avertissement à journaliser.
        ##

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._logIn(timestamp, "WARNING", message)

        if Config.DEBUG:
            self._writeDebug(timestamp, "WARNING", message)

        return

    def error(self, message):
        ##
        # @brief Journalise un message de niveau ERROR.
        #
        # @param message Message d'erreur à journaliser.
        ##

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._logIn(timestamp, "ERROR", message)

        if Config.DEBUG:
            self._writeDebug(timestamp, "ERROR", message)

        return
