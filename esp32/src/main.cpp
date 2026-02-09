#include <Arduino.h>
#include <ArduinoJson.h>

#include "Config.h"
#include "UARTManager.h"
#include "PolarH10Sensor.h"

// ═══════════════════════════════════════════════════════
// Architecture Locale - Sans WiFi 
// ═══════════════════════════════════════════════════════

UARTManager* uartManager = nullptr;
PolarH10Sensor* heartRateSensor = nullptr;

unsigned long lastHeartbeatTime = 0;
uint32_t messageCounter = 1;

// ═══════════════════════════════════════════════════════
// FONCTIONS UTILITAIRES
// ═══════════════════════════════════════════════════════

void printBanner() {
    Serial.println("\n");
    Serial.println("╔════════════════════════════════════════════╗");
    Serial.println("║    SYSTÈME MONITORING FOOTBALL - STADE     ║");
    Serial.println("║        Architecture Locale (Sans WiFi)     ║");
    Serial.println("║                                            ║");
    Serial.println("╚════════════════════════════════════════════╝");
    Serial.println();
    Serial.print("Supporter    : ");
    Serial.println(SUPPORTER_NAME);
    Serial.print("ID           : ");
    Serial.println(SUPPORTER_ID);
    Serial.print("Polar H10    : ");
    Serial.println(POLAR_MAC_ADDRESS);
    Serial.println("────────────────────────────────────────────");
    Serial.print("UART TX      : GPIO ");
    Serial.println(Config::UART::TX_PIN);
    Serial.print("UART RX      : GPIO ");
    Serial.println(Config::UART::RX_PIN);
    Serial.print("Baud Rate    : ");
    Serial.println(Config::UART::BAUD_RATE);
    Serial.println();
    Serial.print("★ Noeuds     : ");
    Serial.println(Config::UART::NB_NODES);
    Serial.print("★ Intervalle : ");
    Serial.print(Config::UART::SEND_INTERVAL / 1000);
    Serial.print(" secondes (");
    Serial.print(60000 / Config::UART::SEND_INTERVAL);
    Serial.println(" msg/min)");
    Serial.println("════════════════════════════════════════════\n");
}

void systemHeartbeat() {
    unsigned long now = millis();
    
    if (now - lastHeartbeatTime >= Config::System::HEARTBEAT_INTERVAL) {
        lastHeartbeatTime = now;
        
        Serial.println("\n╔═══════════════════════════════════════════╗");
        Serial.print("║  STATUS - ");
        Serial.print(SUPPORTER_NAME);
        Serial.println("                       ║");
        Serial.println("╠═══════════════════════════════════════════╣");
        
        // Uptime
        Serial.print("║    Uptime        : ");
        Serial.print(now / 1000 / 60);
        Serial.println(" minutes           ║");
        
        // BLE Status
        Serial.print("║  ");
        if (heartRateSensor->isConnected()) {
            Serial.print("✓ BLE Connected  : ");
            Serial.print(heartRateSensor->getRSSI());
            Serial.println(" dBm        ║");
        } else {
            Serial.println("✗ BLE Searching...                    ║");
        }
        
        // UART Stats
        Serial.print("║   UART Messages : ");
        Serial.print(uartManager->getSentCount());
        Serial.println("                    ║");
        
        // Heart Rate Data
        SensorData data = heartRateSensor->getData();
        if (data.valid && data.sampleCount > 0) {
            Serial.println("╠═══════════════════════════════════════════╣");
            Serial.print("║    FC Actuelle   : ");
            Serial.print(data.value);
            Serial.println(" BPM             ║");
            Serial.print("║   FC Moyenne    : ");
            Serial.print(data.average, 1);
            Serial.println(" BPM            ║");
            Serial.print("║   Échantillons  : ");
            Serial.print(data.sampleCount);
            Serial.println("                   ║");
        }
        
        Serial.println("╚═══════════════════════════════════════════╝");
        Serial.println();
    }
}

void onSensorDataReceived(const SensorData& data) {
    // Extraire la fréquence cardiaque
    uint16_t heartRate = data.value;
    
    // Valider la fréquence cardiaque
    if (heartRate < Config::System::VALID_HR_MIN || 
        heartRate > Config::System::VALID_HR_MAX) {
        Serial.print("  FC invalide (");
        Serial.print(heartRate);
        Serial.println(" BPM) - ignorée");
        return;
    }
    
    // Affichage temps réel compact
    Serial.print(" FC : ");
    Serial.print(heartRate);
    Serial.print(" BPM");
    Serial.print(" | Buffer : ");
    Serial.print(uartManager->getBufferCount());
    Serial.println(" valeurs");
    
    // Ajout au buffer 
    uartManager->addToBuffer(heartRate);
    
    // Envoi via UART/Meshtastic si intervalle respecté
    if (uartManager->canSend()) {
        int bufferCount = uartManager->getBufferCount();
        
        if (bufferCount > 0) {
        
            uint16_t averageHR = uartManager->getAverageFromBuffer();
            
    
            bool success = uartManager->sendHeartRateBuffer(
                SUPPORTER_ID, 
                messageCounter
            );
            
            if (success) {
                messageCounter++;
                
                // Affichage de confirmation
                Serial.println();
                Serial.println("┌──────────────────────────────────────┐");
                Serial.print("│  ENVOI MESHTASTIC #");
                Serial.print(messageCounter - 1);
                Serial.println();
                Serial.println("├──────────────────────────────────────┤");
                Serial.print("│ Moyenne    : ");
                Serial.print(averageHR);
                Serial.print(" BPM");
                Serial.println();
                Serial.print("│ Valeurs    : ");
                Serial.print(bufferCount);
                Serial.print(" échantillons");
                Serial.println();
                Serial.print("│ Format     : Buffer complet (JSON array)");
                Serial.println();
                Serial.print("│ Timestamp  : Reconstruit serveur");
                Serial.println();
                Serial.println("└──────────────────────────────────────┘");
                Serial.println();
            } else {
                Serial.println("  Erreur envoi UART");
            }
            
            // Vider le buffer
            uartManager->clearBuffer();
        }
    }
}

void onSensorStatusChanged(bool connected) {
    Serial.println();
    if (connected) {
        Serial.println(" Polar H10 CONNECTÉ");
    } else {
        Serial.println(" Polar H10 DÉCONNECTÉ - Recherche...");
    }
    Serial.println();
}

// ═══════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    printBanner();
    
    Serial.println("[1/2]  Initialisation UART/Meshtastic...");
    uartManager = new UARTManager(
        Config::UART::RX_PIN, 
        Config::UART::TX_PIN, 
        Config::UART::BAUD_RATE
    );
    
    if (uartManager->begin()) {
        Serial.println("       UART OK");
    } else {
        Serial.println("       ERREUR UART");
    }
    
    Serial.println();
    Serial.println("[2/2]  Initialisation Polar H10...");
    heartRateSensor = new PolarH10Sensor(POLAR_MAC_ADDRESS, POLAR_DEVICE_NAME);
    heartRateSensor->onDataReceived(onSensorDataReceived);
    heartRateSensor->onStatusChanged(onSensorStatusChanged);
    
    if (heartRateSensor->begin()) {
        Serial.println("       BLE OK");
    } else {
        Serial.println("       ERREUR BLE");
    }
    
    Serial.println();
    Serial.println("════════════════════════════════════════════");
    Serial.println(" ✓ INITIALISATION TERMINÉE (BUFFER V2)");
    Serial.println(" Recherche du Polar H10...");
    Serial.println("════════════════════════════════════════════");
    Serial.println();
}

// ═══════════════════════════════════════════════════════
// LOOP
// ═══════════════════════════════════════════════════════

void loop() {
    // Mise à jour capteur
    heartRateSensor->update();
    
    // Heartbeat système
    systemHeartbeat();
    
    // Délai adaptatif
    if (heartRateSensor->isConnected()) {
        delay(1000);  // 1 seconde si connecté
    } else {
        delay(100);   // 100ms si recherche
    }
}