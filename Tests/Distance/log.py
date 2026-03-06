##
# @file log.py
##


# =============================================================================
#  Import des bibliothèques
# =============================================================================

import json
from datetime import datetime

from Server.Config.setting import Config
from Server.Utils.display import printBanner
from Server.Core.mqtt import MQTTClientWrapper

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
    # @brief Initialise et démarre le client MQTT.
    ##

    printBanner("   Log des tests")

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

    mqttClient.start()

# =============================================================================
#  Callback MQTT
# =============================================================================

def _onMqttMessage(message):
    ##
    # @brief Affiche le message reçu depuis MQTT.
    #
    # @param message Message paho-mqtt reçu (topic, payload, qos, retain).
    ##

    data = json.loads(message.payload.decode())

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Message reçu: {data['m']}")

# =============================================================================
#  Point d'entrée
# =============================================================================

if __name__ == "__main__":
    main()
