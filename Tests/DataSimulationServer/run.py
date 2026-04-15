##
# @file run.py
#
# @brief Point d'entrée principal de la simulation des échanges de données avec le serveur.
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

from Tests.DataSimulationServer.Simulation.heartRateSimulator import HeartRateSimulator
from Tests.DataSimulationServer.Simulation.acousticSimulator import AcousticSimulator
from Tests.DataSimulationServer.Simulation.accelerometerGyroscopeSimulator import AccelerometerGyroscopeSimulator

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Tests/dataSimulationServer")

# =============================================================================
#  Variable globale
# =============================================================================

## @brief Client MQTT partagé entre main() et les fonctions de messages MQTT.
mqttClient = None

# =============================================================================
#  Création des messages MQTT
# =============================================================================

def heartRateMessage(heartRateSimulator, idf):
    heartRate = heartRateSimulator.getHeartRate()
    topic     = getMQTTTopic("heart_rate", idf)
    message   = json.dumps({"n": "Simulatior", "hr": [heartRate]})
            
    if not mqttClient.publish(topic, message):
        logger.warning(f"[DataSimulationServer] Échec de la publication sur le topic '{topic}'")
    else:
        logger.info(f"[DataSimulationServer] Publication du message '{message}' sur le topic '{topic}'")

    return


def acousticMessage(acousticSimulator, idf):
    acoustic = acousticSimulator.getAcoustic()
    topic    = getMQTTTopic("acoustic", idf)
    message  = json.dumps({"n": "Simulator", "a": [acoustic]})

    if not mqttClient.publish(topic, message):
        logger.warning(f"[DataSimulationServer] Échec de la publication sur le topic '{topic}'")
    else:
        logger.info(f"[DataSimulationServer] Publication du message '{message}' sur le topic '{topic}'")

    return

def accelerometerGyroscopeMessage(accelerometerGyroscopeSimulator, idf):
    accelerometer, gyroscope = accelerometerGyroscopeSimulator.getAccelerometerGyroscope()
    topic                    = getMQTTTopic("accelerometer_gyroscope", idf)
    message                  = json.dumps({"n": "Simulator", "a": [accelerometer], "g": [gyroscope]})

    if not mqttClient.publish(topic, message):
        logger.warning(f"[DataSimulationServer] Échec de la publication sur le topic '{topic}'")
    else:
        logger.info(f"[DataSimulationServer] Publication du message '{message}' sur le topic '{topic}'")
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
        heartRateSimulator1 = HeartRateSimulator()
        heartRateSimulator2 = HeartRateSimulator()
        heartRateSimulator3 = HeartRateSimulator()
        heartRateSimulator4 = HeartRateSimulator()
        heartRateSimulator5 = HeartRateSimulator()

        acousticSimulator1 = AcousticSimulator()
        acousticSimulator2 = AcousticSimulator()
        acousticSimulator3 = AcousticSimulator()

        accelerometerGyroscopeSimulator1 = AccelerometerGyroscopeSimulator()
        accelerometerGyroscopeSimulator2 = AccelerometerGyroscopeSimulator()
        accelerometerGyroscopeSimulator3 = AccelerometerGyroscopeSimulator()

        # Boucle de simulation
        while True:
            # Fréquence cardiaque
            heartRateMessage(heartRateSimulator1, 1)
            heartRateMessage(heartRateSimulator2, 2)
            heartRateMessage(heartRateSimulator3, 3)
            heartRateMessage(heartRateSimulator4, 4)
            heartRateMessage(heartRateSimulator5, 5)

            # Acoustique
            acousticMessage(acousticSimulator1, 1)
            acousticMessage(acousticSimulator2, 2)
            acousticMessage(acousticSimulator3, 3)

            # Accéléromètre / Gyroscope
            accelerometerGyroscopeMessage(accelerometerGyroscopeSimulator1, 1)
            accelerometerGyroscopeMessage(accelerometerGyroscopeSimulator2, 2)
            accelerometerGyroscopeMessage(accelerometerGyroscopeSimulator3, 3)

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
