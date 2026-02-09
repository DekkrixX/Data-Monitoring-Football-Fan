#ifndef UART_MANAGER_H
#define UART_MANAGER_H

#include <Arduino.h>
#include <HardwareSerial.h>
#include <ArduinoJson.h>

/**
 * @brief Gestionnaire de communication UART
 * 
 * Cette classe gère la communication série avec le module Meshtastic
 * pour la transmission des données via le réseau mesh.
 */
class UARTManager {
public:
    /**
     * @brief Constructeur
     * @param rxPin Pin RX
     * @param txPin Pin TX
     * @param baudRate Vitesse de communication
     */
    UARTManager(int rxPin, int txPin, uint32_t baudRate);
    
    /**
     * @brief Initialise la communication UART
     * @return true si initialisation réussie, false sinon
     */
    bool begin();
    
    /**
     * @brief Arrête la communication UART
     */
    void end();
    
    /**
     * @brief Envoie des données via UART
     * @param data Données à envoyer (string)
     * @return true si envoi réussi, false sinon
     */
    bool send(const String& data);
    
    /**
     * @brief Envoie un document JSON via UART
     * @param doc Document JSON
     * @return true si envoi réussi, false sinon
     */
    bool sendJson(const JsonDocument& doc);
    
    /**
     * @brief Envoie des données de capteur formatées (ANCIENNE VERSION)
     * @param supporterId ID du supporter
     * @param heartRate Fréquence cardiaque
     * @param timestamp Timestamp
     * @param counter Compteur de messages
     * @return true si envoi réussi, false sinon
     * @deprecated Utilisez sendHeartRateBuffer() à la place
     */
    bool sendHeartRate(const char* supporterId, uint16_t heartRate, 
                       const String& timestamp, uint32_t counter);
    
    /**
     * @brief ★ NOUVEAU ★ Envoie toutes les valeurs du buffer (pas de moyenne)
     * @param supporterId ID du supporter
     * @param counter Compteur de messages
     * @return true si envoi réussi, false sinon
     * 
     * Format JSON envoyé :
     * {
     *   "id": "supporter1",
     *   "hr": [60, 65, 70, 68, 72],  // Toutes les valeurs
     *   "n": 42
     * }
     * 
     * Le timestamp sera reconstruit côté serveur
     */
    bool sendHeartRateBuffer(const char* supporterId, uint32_t counter);
    
    /**
     * @brief Vérifie si des données sont disponibles
     * @return true si données disponibles, false sinon
     */
    bool available();
    
    /**
     * @brief Lit une ligne depuis UART
     * @return String contenant la ligne lue
     */
    String readLine();
    
    /**
     * @brief Obtient le nombre de messages envoyés
     * @return Nombre de messages envoyés
     */
    uint32_t getSentCount() const { return sentCount; }
    
    /**
     * @brief Configure l'intervalle d'envoi
     * @param interval Intervalle en millisecondes
     */
    void setSendInterval(uint32_t interval) { sendInterval = interval; }
    
    /**
     * @brief Vérifie si on peut envoyer (respect de l'intervalle)
     * @return true si on peut envoyer, false sinon
     */
    bool canSend();
    
    /**
     * @brief Ajoute une valeur au buffer
     * @param value Valeur de fréquence cardiaque
     */
    void addToBuffer(uint16_t value);
    
    /**
     * @brief Obtient la moyenne des valeurs dans le buffer
     * @return Moyenne des valeurs
     * @deprecated Utilisé uniquement pour affichage, pas pour envoi
     */
    uint16_t getAverageFromBuffer();
    
    /**
     * @brief Vide le buffer
     */
    void clearBuffer();
    
    /**
     * @brief Obtient le nombre de valeurs dans le buffer
     * @return Nombre de valeurs
     */
    int getBufferCount() const { return bufferCount; }
    
    /**
     * @brief ★ NOUVEAU ★ Obtient une copie du buffer pour envoi
     * @param outBuffer Pointeur vers tableau de destination
     * @param maxSize Taille maximale du tableau
     * @return Nombre de valeurs copiées
     */
    int getBufferCopy(uint16_t* outBuffer, int maxSize);
    
private:
    int rxPin;
    int txPin;
    uint32_t baudRate;
    HardwareSerial* serial;
    
    uint32_t sentCount;
    uint32_t sendInterval;
    unsigned long lastSendTime;
    
    // Buffer pour stocker toutes les valeurs
    static const int BUFFER_SIZE = 50;  // Max 50 valeurs stockées
    uint16_t hrBuffer[BUFFER_SIZE];
    int bufferIndex;
    int bufferCount;
};

#endif // UART_MANAGER_H