##
# @file app.py
#
# @brief Point d'entrée principal de l'interface web.
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
from Server.Web.routes import registerRoutes
from Server.Web.socketioHandlers import registerSocketioHandlers
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
    # @brief Initialise et démarre l'interface web.
    #
    # @throws RuntimeError Si le démarrage du serveur SocketIO échoue.
    ##

    global socketio

    printBanner("   Interface Web")

    if Config.DEBUG:
        print("\nInterface Web:")
        print(f"   Host: {Config.WEB_HOST}")
        print(f"   Port: {Config.WEB_PORT}")
        print()

    app      = _createFlaskApp()
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    registerRoutes(app, supporterList, stadiumBleacherList)
    registerSocketioHandlers(socketio, supporterList, stadiumBleacherList)

    # Connexion au broker MQTT pour recevoir les données des supporters en temps réel
    mqttClient = MQTTClientWrapper(
        "interface web",
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
        socketio.run(app, host=Config.WEB_HOST, port=Config.WEB_PORT, use_reloader=False, allow_unsafe_werkzeug=True)

    except Exception as e:
        message = "[APP] Erreur lors du démarrage du serveur SocketIO"
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

    logger.info(f"[APP] Message MQTT brut reçu : {message}")

    data = json.loads(message.payload.decode())

    logger.info(f"[APP] Données décodées : {data}")

    topic = message.topic.split("/")
    dataType = topic[1]
    idf = int(topic[2])

    if dataType == "heart_rate":
        if not _supporterExists(idf):
            _createSupporter(idf, dataType)
        _addSupporterHeartRate(idf, data)
    elif dataType == "accelerometer_gyroscope":
        if not _stadiumBleacherExists(idf):
            _createStadiumBleacher(idf, dataType)
        _addStadiumBleacherAccelerometer(idf, data)
    elif dataType == "acoustic":
        if not _stadiumBleacherExists(idf):
            _createStadiumBleacher(idf, dataType)
        _addStadiumBleacherAcoustic(idf, data)
    else:
        logger.warning(f"[APP] Topic MQTT non reconnu : {message.topic}")


# =============================================================================
#  Initialisation Flask
# =============================================================================

def _createFlaskApp():
    ##
    # @brief Crée et configure l'instance Flask.
    #
    # @return Flask Instance Flask configurée.
    ##

    logger.info("[APP] Création de l'application Flask")

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

    logger.info(f"[APP] Nouveau supporter détecté (id={supporterId})")

    name  = getNameOfSupporter(supporterId)
    color = getColorOfSupporter(supporterId)

    supporterList.append(Supporter(supporterId, name))

    if topic == "heart_rate":
        # heartRate=None: valeur initiale avant la première mesure
        payload = createSupporterHeartRateForClient(supporterId, name, color, None)
    else:
        logger.warning(f"[APP] Topic MQTT inconnu (topic={topic})")
        return
    
    socketio.emit("supporterConnection", payload)


def _addSupporterHeartRate(supporterId, data):
    ##
    # @brief Enregistre une nouvelle mesure pour le supporter correspondant et pousse la mise à jour aux clients web via SocketIO.
    #
    # @param supporterId Identifiant du nouveau supporter.
    # @param data        Dictionnaire de données reçu depuis le broker MQTT.
    ##

    name        = getNameOfSupporter(supporterId)
    color       = getColorOfSupporter(supporterId)

    for supporter in supporterList:
        if supporter.getId() == supporterId:
            supporter.addData(data, "heart_rate")

            payload = createSupporterHeartRateForClient(supporter.getId(), name, color, data["hr"])
            payload.update({
                "average": supporter.heartRate.getAverage(),
                "minimum": supporter.heartRate.getMinimum(),
                "maximum": supporter.heartRate.getMaximum(),
            })

            socketio.emit("newSupporterHeartRate", payload)
            return

    logger.warning(f"[APP] Données reçues pour un supporter inconnu (id={supporterId}), message ignoré")


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

    logger.info(f"[APP] Nouvelle tribune détecté (id={stadiumBleacherId})")

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
        logger.warning(f"[APP] Topic MQTT inconnu (topic={topic})")
        return

    socketio.emit("stadiumBleacherConnection", payload)


def _addStadiumBleacherAccelerometer(stadiumBleacherId, data):
    ##
    # @brief Enregistre une nouvelle mesure pour la tribune correspondant et pousse la mise à jour aux clients web via SocketIO.
    #
    # @param stadiumBleacherId Identifiant de la nouvelle tribune.
    # @param data              Dictionnaire de données reçu depuis le broker MQTT.
    ##

    name              = getNameOfStadiumBleacher(stadiumBleacherId)
    color             = getColorOfStadiumBleacher(stadiumBleacherId)

    for stadiumBleacher in stadiumBleacherList:
        if stadiumBleacher.getId() == stadiumBleacherId:
            stadiumBleacher.addData(data, "accelerometer_gyroscope")

            payload = createStadiumBleacherAccelerometerForClient(stadiumBleacher.getId(), name, color, data["a"])
            payload.update({
                "average": stadiumBleacher.accelerometer.getAverage(),
                "minimum": stadiumBleacher.accelerometer.getMinimum(),
                "maximum": stadiumBleacher.accelerometer.getMaximum(),
            })

            socketio.emit("newStadiumBleacherAccelerometer", payload)
            return

    logger.warning(f"[APP] Données reçues pour une tribune inconnu (id={stadiumBleacherId}), message ignoré")


def _addStadiumBleacherAcoustic(stadiumBleacherId, data):
    ##
    # @brief Enregistre une nouvelle mesure pour la tribune correspondant et pousse la mise à jour aux clients web via SocketIO.
    #
    # @param stadiumBleacherId Identifiant de la nouvelle tribune.
    # @param data Dictionnaire de données reçu depuis le broker MQTT.
    ##

    name              = getNameOfStadiumBleacher(stadiumBleacherId)
    color             = getColorOfStadiumBleacher(stadiumBleacherId)

    for stadiumBleacher in stadiumBleacherList:
        if stadiumBleacher.getId() == stadiumBleacherId:
            stadiumBleacher.addData(data, "acoustic")

            payload = createStadiumBleacherAcousticForClient(stadiumBleacher.getId(), name, color, data["a"])
            payload.update({
                "average": stadiumBleacher.acoustic.getAverage(),
                "minimum": stadiumBleacher.acoustic.getMinimum(),
                "maximum": stadiumBleacher.acoustic.getMaximum(),
            })
            socketio.emit("newStadiumBleacherAcoustic", payload)
            return

    logger.warning(f"[APP] Données reçues pour une tribune inconnu (id={stadiumBleacherId}), message ignoré")


# =============================================================================
#  Point d'entrée
# =============================================================================

if __name__ == "__main__":
    main()
