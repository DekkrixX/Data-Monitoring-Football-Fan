#include "UARTManager.h"
#include "Config.h"

UARTManager::UARTManager(int rxPin, int txPin, uint32_t baudRate)
    : rxPin(rxPin),
      txPin(txPin),
      baudRate(baudRate),
      serial(nullptr),
      sentCount(0),
      sendInterval(Config::UART::SEND_INTERVAL),
      lastSendTime(0),
      bufferIndex(0),
      bufferCount(0) {
    // Initialiser le buffer
    clearBuffer();
}

bool UARTManager::begin() {
    serial = &Serial1;
    serial->begin(baudRate, SERIAL_8N1, rxPin, txPin);
    
    delay(100);  // Attendre stabilisation
    
    Serial.print("[UART] Initialise - RX:");
    Serial.print(rxPin);
    Serial.print(" TX:");
    Serial.print(txPin);
    Serial.print(" Baud:");
    Serial.println(baudRate);
    
    return true;
}

void UARTManager::end() {
    if (serial) {
        serial->end();
    }
}

bool UARTManager::send(const String& data) {
    if (!serial) {
        return false;
    }
    
    serial->println(data);
    sentCount++;
    lastSendTime = millis();
    
    return true;
}

bool UARTManager::sendJson(const JsonDocument& doc) {
    String output;
    serializeJson(doc, output);
    
    return send(output);
}

// =====================================================
// ANCIENNE VERSION - Avec moyenne et timestamp
// =====================================================
bool UARTManager::sendHeartRate(const char* supporterId, uint16_t heartRate, 
                                const String& timestamp, uint32_t counter) {
    JsonDocument doc;
    
    doc["id"] = supporterId;
    doc["hr"] = heartRate;
    doc["ts"] = timestamp;
    doc["n"] = counter;
    
    return sendJson(doc);
}

// =====================================================
// Avec buffer complet
// =====================================================
bool UARTManager::sendHeartRateBuffer(const char* supporterId, uint32_t counter) {
    if (bufferCount == 0) {
        Serial.println("  [WARN] Buffer vide, rien à envoyer");
        return false;
    }
    
    JsonDocument doc;
    
    // ID du supporter
    doc["id"] = supporterId;
    
    // ★ NOUVEAU ★ : Tableau de toutes les valeurs
    JsonArray hrArray = doc["hr"].to<JsonArray>();
    for (int i = 0; i < bufferCount; i++) {
        hrArray.add(hrBuffer[i]);
    }
    
    // Compteur de message
    doc["n"] = counter;
    
    
    return sendJson(doc);
}

bool UARTManager::available() {
    return serial && serial->available();
}

String UARTManager::readLine() {
    if (!serial || !serial->available()) {
        return "";
    }
    
    return serial->readStringUntil('\n');
}

bool UARTManager::canSend() {
    return (millis() - lastSendTime) >= sendInterval;
}

// =====================================================
// ============ GESTION DU BUFFER =======================
// =====================================================

void UARTManager::addToBuffer(uint16_t value) {
    // Ajouter la valeur dans le buffer circulaire
    hrBuffer[bufferIndex] = value;
    bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;
    
    // Incrémenter le compte (max BUFFER_SIZE)
    if (bufferCount < BUFFER_SIZE) {
        bufferCount++;
    }
}

uint16_t UARTManager::getAverageFromBuffer() {
    if (bufferCount == 0) {
        return 0;
    }
    
    // Calculer la moyenne (pour affichage uniquement)
    uint32_t sum = 0;
    for (int i = 0; i < bufferCount; i++) {
        sum += hrBuffer[i];
    }
    
    return (uint16_t)(sum / bufferCount);
}

void UARTManager::clearBuffer() {
    bufferIndex = 0;
    bufferCount = 0;
    memset(hrBuffer, 0, sizeof(hrBuffer));
}

int UARTManager::getBufferCopy(uint16_t* outBuffer, int maxSize) {
    int copyCount = (bufferCount < maxSize) ? bufferCount : maxSize;
    
    for (int i = 0; i < copyCount; i++) {
        outBuffer[i] = hrBuffer[i];
    }
    
    return copyCount;
}