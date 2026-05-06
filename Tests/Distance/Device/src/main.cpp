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

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./Config/Setting.hpp"
#include "./Utils/UARTManager/UARTManager.hpp"

// ============================================================================
//  Fonction setup
// ============================================================================

/**
 * @brief Initialisation du firmware (appelée une seule fois au démarrage).
 *
 * Initialisation des ports série.
 */
void setup()
{
    Serial.begin(BAUDRATE);

    Serial.println("[SETUP] Démarrage du firmware");
    Serial.flush();

    // Création d'une interface UART
    uartManager = new UARTManager(RX_PIN, TX_PIN, BAUDRATE);

    // Démarrage de l'interface UART
    uartManager->begin();

    Serial.println("[SETUP] Initialisation terminée, entrée dans la boucle principale");
    Serial.flush();
    
    return ;
}

// ============================================================================
//  Fonction loop
// ============================================================================

/**
 * @brief Boucle principale du firmware (appelée en continu par Arduino).
 *
 * Envoie d'un message de test formaté en JSON via l'UART externe.
 */
void loop()
{
    std::string jsonString;
    JsonDocument json;

    // Construction de l'objet JSON avec les données du capteur
    json["t"] = TOPIC_MQTT;
    json["m"] = MESSAGE;

    // Sérialisation en chaîne JSON + ajout d'un saut de ligne comme délimiteur de message
    serializeJson(json, jsonString);
    jsonString += '\n';
    size_t size = jsonString.length;

    // Formatage des données: conversion std::string -> buffer uint8_t
    uint8_t * data = new uint8_t[size];
    memcpy(data, jsonString, size);

    // Envoi des données via UART externe
    size_t written = uartManager->writeBuffer(data, size);

    if (written == size)
    {
        Serial.printf("[LOOP] Trame envoyée via UART (%u octets): %s", size, jsonString);
        Serial.flush();
    }
    else
    {
        Serial.printf("[LOOP] AVERTISSEMENT - Envoi UART incomplet: %u/%u octets écrits\n", written, size);
        Serial.flush();
    }

    // Délai entre chaque envoi
    delay(DUTY_CYCLE_TIME);

    return ;
}
