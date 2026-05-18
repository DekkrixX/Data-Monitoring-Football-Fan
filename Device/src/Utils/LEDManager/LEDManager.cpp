/**
 * @file LEDManager.cpp
 * 
 * @brief Implémentation de la classe LEDManager.
 *
 * Fournit une abstraction haut niveau de la led de la carte ESP32.
 */

#ifndef _LEDMANAGER_CPP_
#define _LEDMANAGER_CPP_

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./LEDManager.hpp"

// ============================================================================
//  Variable static
// ============================================================================

Logger * LEDManager::logger = nullptr;

// ============================================================================
//  Constructeur
// ============================================================================

LEDManager::LEDManager(int ledPin):
ledPin(ledPin)
{
	if (LEDManager::logger == nullptr)
    	LEDManager::logger = new Logger("LEDManager", true);
}

// ============================================================================
//  Destructeur
// ============================================================================

LEDManager::~LEDManager()
{
    this->end();
};

// ============================================================================
//  Méthode
// ============================================================================

void LEDManager::begin()
{
#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] begin - Ouverture du port de la LED (PIN: %d)\n", this->ledPin));
#endif

    // Initialisation de la LED
    pinMode(this->ledPin, OUTPUT);

#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] begin - LED prête\n"));
#endif

	return ;
}



void LEDManager::end()
{
#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] end - Fermeture de la LED\n"));
#endif

    // Extinction de la LED
	if (this->isOn)
		this->turnOff();

#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] end - LED fermé\n"));
#endif

    return ;
}



void LEDManager::turnOn()
{
	// Allume la LED
	digitalWrite(this->ledPin, LOW);
	this->isOn = true;

#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] turnOn - LED allumé\n"));
#endif

	return ;
}



void LEDManager::turnOff()
{
	// Éteind la LED
	digitalWrite(this->ledPin, HIGH);
	this->isOn = false;

#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] turnOff - LED éteinte\n"));
#endif

    return ;
}


void LEDManager::toggle()
{
	// Changement d'état de la LED
	if (this->isOn)
		this->turnOff();
	else
		this->turnOn();

#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] toggle - Changement d'état de la LED\n"));
#endif

    return ;
}



#endif // _LEDMANAGER_CPP_
