#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// =====================================================
// ============= CONFIGURATION SUPPORTER ================
// =====================================================
// DECOMMENTEZ UNE SEULE LIGNE CI-DESSOUS

// #define SUPPORTER_1
 #define SUPPORTER_2
// #define SUPPORTER_3


// =====================================================

#ifdef SUPPORTER_1
    #define SUPPORTER_ID "supporter1"
    #define SUPPORTER_NAME "Supporter 1"
    #define MQTT_CLIENT_ID "ESP32_Supporter1"
    #define MQTT_TOPIC_HR "polar/supporter1/heartrate"
    #define MQTT_TOPIC_STATUS "polar/supporter1/status"
    #define POLAR_MAC_ADDRESS "c5:58:19:6c:3f:b2"
    #define POLAR_DEVICE_NAME "Polar H10 Supporter1"
#endif

#ifdef SUPPORTER_2
    #define SUPPORTER_ID "supporter2"
    #define SUPPORTER_NAME "Supporter 2"
    #define MQTT_CLIENT_ID "ESP32_Supporter2"
    #define MQTT_TOPIC_HR "polar/supporter2/heartrate"
    #define MQTT_TOPIC_STATUS "polar/supporter2/status"
    #define POLAR_MAC_ADDRESS "fe:02:9d:9f:22:1f"
    #define POLAR_DEVICE_NAME "Polar H10 65AB7621"
#endif

#ifdef SUPPORTER_3
    #define SUPPORTER_ID "supporter3"
    #define SUPPORTER_NAME "Supporter 3"
    #define MQTT_CLIENT_ID "ESP32_Supporter3"
    #define MQTT_TOPIC_HR "polar/supporter3/heartrate"
    #define MQTT_TOPIC_STATUS "polar/supporter3/status"
    #define POLAR_MAC_ADDRESS "5b:4e:8e:88:46:55"
    #define POLAR_DEVICE_NAME "Polar H10 6315682D"
#endif

// Vérification de la configuration
#if !defined(SUPPORTER_1) && !defined(SUPPORTER_2) && !defined(SUPPORTER_3)
    #error "ERREUR: Vous devez decommenter SUPPORTER_1 ou SUPPORTER_2 ou SUPPORTER_3"
#endif

#if defined(SUPPORTER_1) && defined(SUPPORTER_2) && defined(SUPPORTER_3)
    #error "ERREUR: Vous ne pouvez activer qu'UN SEUL supporter a la fois"
#endif

#if (defined(SUPPORTER_1) && defined(SUPPORTER_2)) || \
    (defined(SUPPORTER_1) && defined(SUPPORTER_3)) || \
    (defined(SUPPORTER_2) && defined(SUPPORTER_3))
    #error "ERREUR: Vous ne pouvez activer qu'UN SEUL supporter à la fois"
#endif

// =====================================================
// =============== CONFIGURATION WIFI ===================
// =====================================================
namespace Config {
    namespace WiFi {
        const char* const SSID = "Hillary";
        const char* const PASSWORD = "hillary2003";
        const uint32_t RECONNECT_INTERVAL = 30000;  // 30 secondes
    }

    // =====================================================
    // =============== CONFIGURATION MQTT ===================
    // =====================================================
    namespace MQTT {
        const char* const SERVER = "broker.hivemq.com";
        const int PORT = 1883;
        const uint16_t BUFFER_SIZE = 512;
        const uint16_t KEEP_ALIVE = 60;
        const uint16_t SOCKET_TIMEOUT = 30;
        const uint32_t RECONNECT_INTERVAL = 5000;  // 5 secondes
    }

    // =====================================================
    // =============== CONFIGURATION UART ===================
    // =====================================================
    namespace UART {
        const int RX_PIN = 44;
        const int TX_PIN = 43;
        const uint32_t BAUD_RATE = 115200;
        
        //Nombre de noeuds dans le système 
        const uint8_t NB_NODES = 2;  // Changer selon nombre de capteurs
        
        // Intervalle adaptatif automatique 
        // Formule : 5 secondes × nombre de noeuds
        // 1 noeud  → 5s  → 12 msg/min total
        // 2 noeuds → 10s → 12 msg/min total (6×2)
        // 3 noeuds → 15s → 12 msg/min total (4×3)
        const uint32_t SEND_INTERVAL = 5000 * NB_NODES;  // Auto-calculé
    }

    // =====================================================
    // ============== CONFIGURATION BLE =====================
    // =====================================================
    namespace BLE {
        const char* const HR_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb";
        const char* const HR_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb";
        const int SCAN_TIME = 5;  // secondes
        const uint16_t SCAN_INTERVAL = 100;
        const uint16_t SCAN_WINDOW = 99;
    }

    // =====================================================
    // ============== SYSTÈME ===============================
    // =====================================================
    namespace System {
        const uint32_t HEARTBEAT_INTERVAL = 60000;  // 1 minute
        const uint16_t VALID_HR_MIN = 30;
        const uint16_t VALID_HR_MAX = 220;
    }
}

#endif // CONFIG_H