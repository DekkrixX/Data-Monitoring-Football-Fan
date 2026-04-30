##
# @file bridge_MQTT_InfluxDB.py
#
# @brief Point d'entrée du bridge MQTT vers InfluxDB.
#
# Souscrit aux topics MQTT configurés, décode les messages JSON reçus et les écrit dans InfluxDB sous forme de points de données.
##


# =============================================================================
#  Import des bibliothèques
# =============================================================================

import json
from datetime import datetime

from Server.Config.setting import Config
from Server.Core.mqtt import MQTTClientWrapper
from Server.Core.influxdb import InfluxDBClientWrapper
from Server.Utils.display import printBanner
from Server.Utils.topic import jsonToFieldsPoints
from Server.Utils.time import subtract_seconds
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/Bridge_MQTT-InfluxDB")

# =============================================================================
#  Variable globale
# =============================================================================

influxdbClient = None ##< @brief Client InfluxDB partagé entre main() et le callback _onMessage().
mqttClient     = None ##< @brief Client MQTT partagé entre main() et le callback _onConnect().

# =============================================================================
#  Programme principal
# =============================================================================

##
# @brief Initialise le bridge MQTT vers InfluxDB et démarre la boucle d'écoute MQTT bloquante.
##
def main():
    global influxdbClient, mqttClient

    printBanner("   Bridge MQTT → InfluxDB")

    if Config.DEBUG:
        print("\nMQTT:")
        print(f"   Host      : {Config.MQTT_BROKER_HOST}")
        print(f"   Port      : {Config.MQTT_BROKER_PORT}")
        print(f"   KeepAlive : {Config.MQTT_BROKER_KEEPALIVE}")
        print(f"   QoS       : {Config.MQTT_BROKER_QOS}")
        print("\nInfluxDB:")
        print(f"   Adresse : {Config.INFLUXDB_ADDRESS}")
        print(f"   Token   : {Config.INFLUXDB_TOKEN}")
        print(f"   Org     : {Config.INFLUXDB_ORG}")
        print(f"   Bucket  : {Config.INFLUXDB_BUCKET}")
        print()

    mqttClient = MQTTClientWrapper("bridge_MQTT_InfluxDB", Config.MQTT_BROKER_HOST, Config.MQTT_BROKER_PORT, Config.MQTT_BROKER_KEEPALIVE, qos=Config.MQTT_BROKER_QOS, onMessageCallback=_onMessage, onConnectCallback=_onConnect)

    influxdbClient = InfluxDBClientWrapper(Config.INFLUXDB_HOST, Config.INFLUXDB_PORT, Config.INFLUXDB_ADDRESS, Config.INFLUXDB_TOKEN, Config.INFLUXDB_ORG, Config.INFLUXDB_BUCKET)

    try:
        mqttClient.connect()
        influxdbClient.connect()

        mqttClient.subscribe(Config.MQTT_BROKER_TOPICS_DATA)

        # Mode bloquant: le thread reste ici jusqu'à déconnexion ou Ctrl+C
        mqttClient.start(blocking=True)

    except KeyboardInterrupt:
        logger.info("[Bridge MQTT-InfluxDB] Arrêt demandé par l'utilisateur (Ctrl+C)")

        mqttClient.stop()
        influxdbClient.close()

    return

# =============================================================================
#  Callbacks MQTT
# =============================================================================

##
# @brief Arrête le client et lève une RuntimeError si la connexion est refusée. Appelé lors de l'établissement de la connexion au broker MQTT.
#
# @param client   Instance paho-mqtt.
# @param userdata Données utilisateur (non utilisé).
# @param flags    Flags de connexion.
# @param rc       Code de retour (0 = succès).
#
# @throws RuntimeError Si rc != 0 (connexion refusée par le broker).
##
def _onConnect(client, userdata, flags, rc):
    global mqttClient

    if rc != 0:
        mqttClient.stop()
        message = f"[Bridge MQTT-InfluxDB] Connexion au broker MQTT refusée (rc={rc})"
        logger.error(message)
        raise RuntimeError(message)

    return



##
# @brief Décode le payload JSON, construit le point InfluxDB (tags et fields) et l'écrit dans la base de données. Le champ "type" est utilisé comme nom de mesure InfluxDB. Appelé à chaque message reçu depuis le broker MQTT.
#
# @param message Message paho-mqtt reçu (topic, payload, qos, retain).
##
def _onMessage(message):
    global influxdbClient

    logger.info(f"[Bridge MQTT-InfluxDB] Message brut reçu : {message}")

    data = json.loads(message.payload.decode())

    logger.info(f"[Bridge MQTT-InfluxDB] Données décodées : {data}")

    # Récupération du timestamp
    timestamp = datetime.now()

    topic = message.topic.split("/")
    measurment = topic[0]
    dataType = topic[1]
    idf = int(topic[2])

    # Ajout de l'identifiant et le type de données aux tags
    tags = {"id": idf, "data": dataType}

    # Construction de la liste des champs
    fieldsList = jsonToFieldsPoints(data)

    for i in range(len(fieldsList)):
        influxdbClient.send(measurment, fieldsList[i], tags, subtract_seconds(timestamp, i))

    return

# =============================================================================
#  Point d'entrée
# =============================================================================

if __name__ == "__main__":
    main()
