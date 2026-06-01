/**
 * @file main.cpp
 * 
 * @brief Point d'entrée principal du firmware de la carte électronique.
 *
 * Initialise le firmware de test de distance et envoi des messages à interval régulier.
 */

// ============================================================================
//  Import des headers externes
// ============================================================================

#include <string>
#include <Arduino.h>
#include <ArduinoJson.h>
#include <LittleFS.h>

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./Config/setting.hpp"
#include "./Utils/UARTManager/UARTManager.hpp"
#include "./Utils/LEDManager/LEDManager.hpp"
#include "./Utils/Logger/Logger.hpp"
#include "./Config/Log/Log.hpp"

// ============================================================================
//  Variable globale
// ============================================================================

UARTManager * uartManager = nullptr; ///< @brief Pointeur vers le gestionnaire UART externe. Initialisé dans setup().
LEDManager * ledManager   = nullptr; ///< @brief Pointeur vers le gestionnaire LED.
Logger * logger           = nullptr; ///< @brief Logger qui écrit les logs dans un fichier

uint64_t packageCounter = 0; ///< @brief Compteur de paquet envoyé.

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

    logger = new Logger("Distance", true);

    // Temps de délais pour script de récupération de log
    delay(5000);
    // Export automatique des logs au boot
    dumpLogsOnBoot();

#if DEBUG == 1
    logger->info(Logger::logString("[SETUP] Démarrage du firmware\n"));
#endif

    // Création d'une interface UART
    uartManager = new UARTManager(RX_PIN, TX_PIN, BAUDRATE);

    // Démarrage de l'interface UART
    uartManager->begin();

    // Création d'une interface LED
    ledManager = new LEDManager(LED_PIN);

    // Démarrage de l'interface LED
    ledManager->begin();

#if DEBUG == 1
    logger->info(Logger::logString("[SETUP] Initialisation terminée, entrée dans la boucle principale\n"));
#endif

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
	// Mise à jour de la LED
    ledManager->toggle();

	// Construction du message
	std::string jsonString;
	JsonDocument json;

	json["t"]   = TOPIC_TEST;
	json["n"]   = NAME;
	json["id"]  = ID;
	json["msg"] = packageCounter;

#if DATA_SIMULATION == 1
	const int data[10] = {102, 99, 95, 97, 92, 90, 88, 85, 80, 86};
	JsonArray array = json["d"].to<JsonArray>();
    for (int i=0; i < 10; i++)
        array.add(data[i]);
#endif

	serializeJson(json, jsonString);
	jsonString += '\n';

	// Formatage des données: conversion std::string -> buffer uint8_t
	size_t size = jsonString.length();
	uint8_t * data = new uint8_t[size];
	memcpy(data, jsonString.c_str(), size);

	// Envoi des données via UART externe
	size_t written = uartManager->writeBuffer(data, size);
#if DEBUG == 1
	if (written == size)
		logger->info(Logger::logString("[LOOP] Trame envoyée via UART (%u octets): %s", size, jsonString.c_str()));
	else
		logger->info(Logger::logString("[LOOP] AVERTISSEMENT - Envoi UART incomplet: %u/%u octets écrits\n", written, size));
#endif
	logger->info(Logger::logString("[LOOP] Paquet n°%u envoyé\n", packageCounter));

	delete [] data;

	// Incrémentation du nombre de paquet
	packageCounter++;

	delay(TIME_INTERVAL);

	return ;
}
