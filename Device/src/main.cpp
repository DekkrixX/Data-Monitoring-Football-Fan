/**
 * @file main.cpp
 * 
 * @brief Point d'entrée principal du firmware de la carte électronique.
 *
 * Initialise le capteur configuré dans setting.hpp ainsi que l'interface UART externe, puis boucle en envoyant les données du capteur via UART toutes les secondes lorsque celui-ci est connecté.
 */

// ============================================================================
//  Import des headers externes
// ============================================================================

#include <string>
#include <Arduino.h>
#include <LittleFS.h>

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./Sensor/Sensor.hpp"
#include "./Utils/UARTManager/UARTManager.hpp"
#include "./Config/setting.hpp"
#include "./Config/initSensor.hpp"
#include "./Utils/Logger/Logger.hpp"
#include "./Config/Log/Log.hpp"

// ============================================================================
//  Import des capteurs
// ============================================================================

#include "./Sensor/HeartRate/PolarH10/PolarH10.hpp"

// ============================================================================
//  Variable globale
// ============================================================================

Sensor * sensor = nullptr; ///< @brief Pointeur vers le capteur actif. Initialisé dans setup().
UARTManager * uartManager = nullptr; ///< @brief Pointeur vers le gestionnaire UART externe. Initialisé dans setup().
unsigned long lastSendMs = 0; ///< @brief Temps du dernier envoi de données
Logger * logger = nullptr; ///< @brief Logger qui écrit les logs dans un fichier

// ============================================================================
//  Fonction setup
// ============================================================================

/**
 * @brief Initialisation du firmware (appelée une seule fois au démarrage).
 *
 * Initialisation des ports série et le capteur.
 */
void setup()
{
    Serial.begin(BAUDRATE_DEBUG);
    if (not LittleFS.begin(true))
        throw std::runtime_error("Le système de fichier LittleFS n'est pas monté");

    psramInit(); // Initialisation de la PSRAM requis avant toute instanciation de Logger

    logger = new Logger("Main", true);

    // Temps de délais pour script de récupération de log
    delay(5000);
    // Export automatique des logs au boot
    dumpLogsOnBoot();

    logger->info("[SETUP] Démarrage du firmware");

    // Création d'une interface UART
    uartManager = new UARTManager(RX_PIN, TX_PIN, BAUDRATE);

    // Démarrage de l'interface UART
    uartManager->begin();

    // Initialisation du capteur
    sensor = new SENSOR(SUPPORTER_ID);

    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[SETUP] Capteur instancié: %s (supporter id: %d)\n", sensor->getSensorName().c_str(), SUPPORTER_ID); 
    logger->info(str);

    // Démarrage du capteur
    sensor->begin();

    logger->info("[SETUP] Initialisation terminée, entrée dans la boucle principale");

    return ;
}

// ============================================================================
//  Fonction loop
// ============================================================================

/**
 * @brief Boucle principale du firmware (appelée en continu par Arduino).
 *
 * Met à jour l'état interne du capteur, envoie des mesure formatée en JSON via l'UART externe.
 */
void loop()
{
    // Mise à jour du capteur
    sensor->update();

    // Mise à jour du temps
    unsigned long now = millis();

    // Si l’intervalle de temps est écoulé, on prépare et on envoie la trame
    if (now - lastSendMs >= DUTY_CYCLE_TIME)
    {
        lastSendMs = now; 

        // Vérifie la connexion du capteur
        if (sensor->isConnected())
        {
            // Récupération des données
            std::string dataString = sensor->getSensorData();
            size_t size = dataString.length();

            if (size != 0)
            {
                // Formatage des données: conversion std::string -> buffer uint8_t
                uint8_t * data = new uint8_t[size];
                memcpy(data, dataString.c_str(), size);

                // Envoi des données via UART externe
                size_t written = uartManager->writeBuffer(data, size);

                if (written == size)
                {
                    char str[LOGGER_MAX_MESSAGE_SIZE];
                    snprintf(str, sizeof(str), "[LOOP] Trame envoyée via UART (%u octets): %s", size, dataString.c_str());
                    logger->info(str);
                }
                else
                {
                    char str[LOGGER_MAX_MESSAGE_SIZE];
                    snprintf(str, sizeof(str), "[LOOP] AVERTISSEMENT - Envoi UART incomplet: %u/%u octets écrits\n", written, size);
                    logger->info(str);
                }

                delete [] data;
            }
            else
                logger->info("[LOOP] Capteur connecté mais aucune donnée disponible, attente de la prochaine notification");
        }
        else
        {
            char str[LOGGER_MAX_MESSAGE_SIZE];
            snprintf(str, sizeof(str), "[LOOP] Capteur '%s' non connecté, en attente\n", sensor->getSensorName().c_str());
            logger->info(str);
        }
    }

    // Délai entre chaque acquisition
    delay(1000); // 1s

    return ;
}