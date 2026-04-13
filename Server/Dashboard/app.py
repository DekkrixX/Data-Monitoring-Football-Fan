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
from Server.Core.StadiumBleacher.stadiumBleacher import StadiumBleacher
from Server.Utils.display import printBanner
from Server.Utils.data import createSupporterHeartRateForClient, getNameOfSupporter, getColorOfSupporter, createStadiumBleacherAccelerometerForClient, createStadiumBleacherAcousticForClient, getNameOfStadiumBleacher, getColorOfStadiumBleacher
from Server.Core.mqtt import MQTTClientWrapper
from Server.Dashboard.routes import registerRoutes
from Server.Dashboard.socketioHandlers import registerSocketioHandlers
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/App")

# =============================================================================
#  Variables globales
# =============================================================================

## @brief Liste des supporters actifs, alimentée par les messages MQTT.
supporterList = []
## @brief Liste des tribunes du stade actives, alimentée par les messages MQTT.
stadiumBleacherList = []
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

    registerRoutes(app, supporterList, stadiumBleacherList)
    registerSocketioHandlers(socketio, supporterList, stadiumBleacherList)

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
        socketio.run(app, host=Config.DASHBOARD_HOST, port=Config.DASHBOARD_PORT, use_reloader=False)

    except Exception as e:
        message = "[Dashboard] Erreur lors du démarrage du serveur SocketIO"
        logger.error(message)
        raise RuntimeError(message) from e

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

    logger.info(f"[Dashboard] Message MQTT brut reçu : {message}")

    data = json.loads(message.payload.decode())

    logger.info(f"[Dashboard] Données décodées : {data}")

    # Message de supporter
    if "sid" in data:
        supporterId = data["sid"]

        if not _supporterExists(supporterId):
            _createSupporter(supporterId, data["t"])

        if data["t"] == "heart_rate":
            _addSupporterHeartRate(data)

    # Message de tribune du stade
    if "bid" in data:
        stadiumBleacherId = data["bid"]

        if not _stadiumBleacherExists(stadiumBleacherId):
            _createStadiumBleacher(stadiumBleacherId, data["t"])

        if data["t"] == "accelerometer_gyroscope":
            _addStadiumBleacherAccelerometer(data)
        elif data["t"] == "acoustic":
            _addStadiumBleacherAcoustic(data)


# =============================================================================
#  Initialisation Flask
# =============================================================================

def _createFlaskApp():
    ##
    # @brief Crée et configure l'instance Flask.
    #
    # @return Flask Instance Flask configurée.
    ##

    logger.info("[Dashboard] Création de l'application Flask")

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


def _createSupporter(supporterId, topic):
    ##
    # @brief Crée un nouveau Supporter, l'ajoute à supporterList et notifie les clients web de sa connexion via SocketIO.
    #
    # @param supporterId Identifiant du nouveau supporter.
    # @param topic       Topic MQTT
    ##

    global socketio

    logger.info(f"[Dashboard] Nouveau supporter détecté (id={supporterId})")

    name  = getNameOfSupporter(supporterId)
    color = getColorOfSupporter(supporterId)

    supporterList.append(Supporter(supporterId, name))

    if topic == "heart_rate":
        # heartRate=None: valeur initiale avant la première mesure
        payload = createSupporterHeartRateForClient(supporterId, name, color, None)
    else:
        logger.warning(f"[Dashboard] Topic MQTT inconnu (topic={topic})")
        return
    
    socketio.emit("supporterConnection", payload)


def _addSupporterHeartRate(data):
    ##
    # @brief Enregistre une nouvelle mesure pour le supporter correspondant et pousse la mise à jour aux clients web via SocketIO.
    #
    # @param data Dictionnaire de données reçu depuis le broker MQTT.
    ##

    supporterId = data["sid"]
    name        = getNameOfSupporter(supporterId)
    color       = getColorOfSupporter(supporterId)

    for supporter in supporterList:
        if supporter.getId() == supporterId:
            supporter.addData(data)

            payload = createSupporterHeartRateForClient(supporter.getId(), name, color, data["hr"])
            payload.update({
                "average": supporter.heartRate.getAverage(),
                "minimum": supporter.heartRate.getMinimum(),
                "maximum": supporter.heartRate.getMaximum(),
            })

            socketio.emit("newSupporterHeartRate", payload)
            return

    logger.warning(f"[Dashboard] Données reçues pour un supporter inconnu (id={supporterId}), message ignoré")


# =============================================================================
#  Gestion des tribunes du stade
# =============================================================================

def _stadiumBleacherExists(stadiumBleacherId):
    ##
    # @brief Indique si un StadiumBleacher avec cet identifiant est déjà présent
    #        dans stadiumBleacherList.
    #
    # @param stadiumeBleacherId Identifiant de la tribune recherché.
    #
    # @return bool True si la tribune existe, False sinon.
    ##

    for stadiumBleacher in stadiumBleacherList:
        if stadiumBleacher.getId() == stadiumBleacherId:
            return True
    return False


def _createStadiumBleacher(stadiumBleacherId, topic):
    ##
    # @brief Crée un nouveau StadiumBleacher, l'ajoute à stadiumBleacherList et notifie les clients web de sa connexion via SocketIO.
    #
    # @param stadiumBleacher Identifiant de la nouvelle tribune.
    # @param topic           Topic MQTT.
    ##

    global socketio

    logger.info(f"[Dashboard] Nouvelle tribune détecté (id={stadiumBleacherId})")

    name  = getNameOfStadiumBleacher(stadiumBleacherId)
    color = getColorOfStadiumBleacher(stadiumBleacherId)

    stadiumBleacherList.append(StadiumBleacher(stadiumBleacherId, name))

    if topic == "accelerometer_gyroscope":
        # accelerometer=None: valeur initiale avant la première mesure
        payload = createStadiumBleacherAccelerometerForClient(stadiumBleacherId, name, color, None)
    elif topic == "acoustic":
        # acoustic=None: valeur initiale avant la première mesure
        payload = createStadiumBleacherAcousticForClient(stadiumBleacherId, name, color, None)
    else:
        logger.warning(f"[Dashboard] Topic MQTT inconnu (topic={topic})")
        return

    socketio.emit("stadiumBleacherConnection", payload)


def _addStadiumBleacherAccelerometer(data):
    ##
    # @brief Enregistre une nouvelle mesure pour la tribune correspondant et pousse la mise à jour aux clients web via SocketIO.
    #
    # @param data Dictionnaire de données reçu depuis le broker MQTT.
    ##

    stadiumBleacherId = data["bid"]
    name              = getNameOfStadiumBleacher(stadiumBleacherId)
    color             = getColorOfStadiumBleacher(stadiumBleacherId)

    for stadiumBleacher in stadiumBleacherList:
        if stadiumBleacher.getId() == stadiumBleacherId:
            stadiumBleacher.addData(data)

            payload = createStadiumBleacherAccelerometerForClient(stadiumBleacher.getId(), name, color, data["a"])
            payload.update({
                "average": stadiumBleacher.accelerometer.getAverage(),
                "minimum": stadiumBleacher.accelerometer.getMinimum(),
                "maximum": stadiumBleacher.accelerometer.getMaximum(),
            })

            socketio.emit("newStadiumBleacherAccelerometer", payload)
            return

    logger.warning(f"[Dashboard] Données reçues pour une tribune inconnu (id={stadiumBleacherId}), message ignoré")


def _addStadiumBleacherAcoustic(data):
    ##
    # @brief Enregistre une nouvelle mesure pour la tribune correspondant et pousse la mise à jour aux clients web via SocketIO.
    #
    # @param data Dictionnaire de données reçu depuis le broker MQTT.
    ##

    stadiumBleacherId = data["bid"]
    name              = getNameOfStadiumBleacher(stadiumBleacherId)
    color             = getColorOfStadiumBleacher(stadiumBleacherId)

    for stadiumBleacher in stadiumBleacherList:
        if stadiumBleacher.getId() == stadiumBleacherId:
            stadiumBleacher.addData(data)

            payload = createStadiumBleacherAcousticForClient(stadiumBleacher.getId(), name, color, data["a"])
            payload.update({
                "average": stadiumBleacher.acoustic.getAverage(),
                "minimum": stadiumBleacher.acoustic.getMinimum(),
                "maximum": stadiumBleacher.acoustic.getMaximum(),
            })
            socketio.emit("newStadiumBleacherAcoustic", payload)
            return

    logger.warning(f"[Dashboard] Données reçues pour une tribune inconnu (id={stadiumBleacherId}), message ignoré")


# =============================================================================
#  Point d'entrée
# =============================================================================

if __name__ == "__main__":
    main()
