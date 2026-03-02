##
# @file app.py
#
# @brief Point d'entrée principal du dashboard web.
#
# Initialise l'application Flask, la WebSocket SocketIO et le client MQTT, puis démarre le serveur. Les messages MQTT reçus créent ou mettent à jour les supporters et poussent les données aux clients web en temps réel.
##


# =============================================================================
#  Import des bibliothèques
# =============================================================================

import json
from flask import Flask
from flask_socketio import SocketIO

from Server.Config.setting import Config
from Server.Core.Supporter.supporter import Supporter
from Server.Utils.display import printBanner
from Server.Utils.data import createDataForClient, getNameOfSupporter, getColorOfSupporter
from Server.Core.mqtt import MQTTClientWrapper
from Server.Dashboard.routes import registerRoutes
from Server.Dashboard.socketioHandlers import registerSocketioHandlers


# =============================================================================
#  Variables globales
# =============================================================================

## @brief Liste des supporters actifs, alimentée par les messages MQTT.
supporterList = []
## @brief Instance SocketIO partagée entre main() et les callbacks MQTT.
socketio = None


# =============================================================================
#  Programme principal
# =============================================================================

def main():
    ##
    # @brief Initialise et démarre le dashboard web.
    #
    # @throws RuntimeError Si le démarrage du serveur SocketIO échoue.
    ##

    global socketio

    printBanner("   Dashboard Web")

    if Config.DEBUG:
        print("\nDashboard Web:")
        print(f"   Host: {Config.DASHBOARD_HOST}")
        print(f"   Port: {Config.DASHBOARD_PORT}")
        print()

    app      = _createFlaskApp()
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    registerRoutes(app, supporterList)
    registerSocketioHandlers(socketio, supporterList)

    # Connexion au broker MQTT pour recevoir les données des supporters en temps réel
    mqttClient = MQTTClientWrapper(
        "dashboard",
        Config.MQTT_BROKER_HOST,
        Config.MQTT_BROKER_PORT,
        Config.MQTT_BROKER_KEEPALIVE,
        qos=Config.MQTT_BROKER_QOS,
        onMessageCallback=_onMqttMessage
    )

    mqttClient.connect()
    mqttClient.subscribe(Config.MQTT_BROKER_TOPICS)

    # Mode non bloquant: socketio.run() prend ensuite la main
    mqttClient.start(blocking=False)

    try:
        socketio.run(app, use_reloader=False)

    except Exception as e:
        raise RuntimeError("[Dashboard] Erreur lors du démarrage du serveur SocketIO") from e

    finally:
        # Notification de fermeture aux clients web avant l'arrêt
        socketio.emit("serverClose")

        if mqttClient.isConnected():
            mqttClient.stop()


# =============================================================================
#  Callback MQTT
# =============================================================================

def _onMqttMessage(message):
    ##
    # @brief Crée le supporter s'il n'existe pas encore dans supporterList, puis enregistre la nouvelle mesure et notifie les clients web. Appelé à chaque message reçu depuis le broker MQTT.
    #
    # @param message Message paho-mqtt reçu (topic, payload, qos, retain).
    ##

    if Config.DEBUG:
        print(f"[Dashboard] Message MQTT brut reçu : {message}")

    data = json.loads(message.payload.decode())

    if Config.DEBUG:
        print(f"[Dashboard] Données décodées : {data}")

    supporterId = data["supporter id"]

    if not _supporterExists(supporterId):
        _createSupporter(supporterId)

    _addSupporterData(data)


# =============================================================================
#  Initialisation Flask
# =============================================================================

def _createFlaskApp():
    ##
    # @brief Crée et configure l'instance Flask.
    #
    # @return Flask Instance Flask configurée.
    ##

    if Config.DEBUG:
        print("[Dashboard] Création de l'application Flask")

    app = Flask(__name__)
    app.config["SECRET_KEY"]            = Config.SECRET_KEY
    app.config["DEBUG"]                 = Config.DEBUG
    app.config["JSON_SORT_KEYS"]        = False
    app.config["TEMPLATES_AUTO_RELOAD"] = Config.DEBUG

    return app


# =============================================================================
#  Gestion des supporters
# =============================================================================

def _supporterExists(supporterId):
    ##
    # @brief Indique si un Supporter avec cet identifiant est déjà présent
    #        dans supporterList.
    #
    # @param supporterId Identifiant du supporter recherché.
    #
    # @return bool True si le supporter existe, False sinon.
    ##

    for supporter in supporterList:
        if supporter.getId() == supporterId:
            return True
    return False


def _createSupporter(supporterId):
    ##
    # @brief Crée un nouveau Supporter, l'ajoute à supporterList et notifie les clients web de sa connexion via SocketIO.
    #
    # @param supporterId Identifiant du nouveau supporter.
    ##

    global socketio

    if Config.DEBUG:
        print(f"[Dashboard] Nouveau supporter détecté (id={supporterId})")

    name  = getNameOfSupporter(supporterId)
    color = getColorOfSupporter(supporterId)

    supporterList.append(Supporter(supporterId, name))

    # heartRate=0: valeur initiale avant la première mesure
    payload = createDataForClient(supporterId, name, color, 0)
    socketio.emit("supporterConnection", payload)


def _addSupporterData(data):
    ##
    # @brief Enregistre une nouvelle mesure pour le supporter correspondant et pousse la mise à jour aux clients web via SocketIO.
    #
    # @param data Dictionnaire de données reçu depuis le broker MQTT.
    ##

    supporterId = data["supporter id"]
    name        = getNameOfSupporter(supporterId)
    color       = getColorOfSupporter(supporterId)

    for supporter in supporterList:
        if supporter.getId() == supporterId:
            supporter.addData(data)

            payload = createDataForClient(supporter.getId(), name, color, data["heart rate"])
            payload.update({
                "average": supporter.heartRate.getAverage(),
                "minimum": supporter.heartRate.getMinimum(),
                "maximum": supporter.heartRate.getMaximum(),
            })

            socketio.emit("newSupporterData", payload)
            return

    if Config.DEBUG:
        print(f"[Dashboard] Données reçues pour un supporter inconnu (id={supporterId}), message ignoré")


# =============================================================================
#  Point d'entrée
# =============================================================================

if __name__ == "__main__":
    main()
