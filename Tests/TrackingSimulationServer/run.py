##
# @file run.py
#
# @brief Point d'entrée principal de la simulation des échanges de données pour le tracking avec le serveur.
#
# Initialise le client MQTT. Puis envoi des messages MQTT en temps réel au serveur.
##

# =============================================================================
#  Import
# =============================================================================

import json
import time

from Server.Config.setting import Config
from Server.Core.mqtt import MQTTClientWrapper
from Server.Utils.display import printBanner
from Server.Utils.topic import getMQTTTopic
from Server.Utils.logger import Logger

from Tests.TrackingSimulationServer.Simulation.positionSimulator import PositionSimulator

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Tests/trackingSimulationServer")

# =============================================================================
#  Variable globale
# =============================================================================

## @brief Client MQTT partagé entre main() et les fonctions de messages MQTT.
mqttClient = None

# =============================================================================
#  Création des messages MQTT
# =============================================================================

def positionMessage(positionSimulator, idf):
    position = positionSimulator.getPosition()
    topic    = f"monitoring/tracker/{idf}"
    message  = json.dumps({"n": "Simulator", "p": [position]})
            
    if not mqttClient.publish(topic, message):
        logger.warning(f"[TrackingSimulationServer] Échec de la publication sur le topic '{topic}'")
    else:
        logger.info(f"[TrackingSimulationServer] Publication du message '{message}' sur le topic '{topic}'")

    return

# =============================================================================
#  Programme principal
# =============================================================================

def main():
    global mqttClient

    printBanner("   Simulation d'envoi de données via MQTT au serveur")

    if Config.DEBUG:
        print("\nMQTT:")
        print(f"   Host      : {Config.MQTT_BROKER_HOST}")
        print(f"   Port      : {Config.MQTT_BROKER_PORT}")
        print(f"   KeepAlive : {Config.MQTT_BROKER_KEEPALIVE}")
        print(f"   QoS       : {Config.MQTT_BROKER_QOS}")

    mqttClient = MQTTClientWrapper(
        "MQTT_data_simulation",
        Config.MQTT_BROKER_HOST,
        Config.MQTT_BROKER_PORT,
        Config.MQTT_BROKER_KEEPALIVE,
        qos=Config.MQTT_BROKER_QOS
    )

    try:
        mqttClient.connect()

        # MQTT en mode non bloquant pour que la boucle de simulation puisse tourner ensuite
        mqttClient.start(blocking=False)

        # Création des simulateurs
        positionSimulator1 = PositionSimulator(-250, 250, -250, 250)

        # Boucle de simulation
        while True:
            # Position
            positionMessage(positionSimulator1, 1)

            time.sleep(Config.SENSOR_DELAY)


    except KeyboardInterrupt:
        logger.info("[DataSimulationServer] Arrêt demandé par l'utilisateur (Ctrl+C)")

        mqttClient.stop()

    return

# =============================================================================
#  Point d'entrée
# =============================================================================

if __name__ == "__main__":
    main()
