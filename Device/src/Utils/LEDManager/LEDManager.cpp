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

LEDManager::LEDManager(int ledPin, int ledNumber):
ledPin(ledPin),
ledNumber(ledNumber),
led(ledNumber, ledPin, NEO_GRB + NEO_KHZ800)
{
    LEDManager::logger = new Logger("LEDManager", true);
}

// ============================================================================
//  Destructeur
// ============================================================================

LEDManager::~LEDManager()
{
    this->end();
    delete LEDManager::logger;
};

// ============================================================================
//  Méthode
// ============================================================================

void LEDManager::begin()
{
#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] begin - Ouverture du port de la LED (PIN: %d, nombre de LED: %d)\n", this->ledPin, this->ledNumber));
#endif

    // Initialisation de la LED
    this->led.begin();

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
	this->led.clear();
    this->led.show();
    this->isOn = false;

#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] end - LED fermé\n"));
#endif

    return ;
}



void LEDManager::turnOn()
{
	// Allume la LED
	this->led.show();
	this->isOn = true;

#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] turnOn - LED allumé\n"));
#endif

	return ;
}



void LEDManager::turnOff()
{
	// Éteind la LED
	this->led.clear();
	this->led.show();
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


void LEDManager::changeColor(uint8_t red, uint8_t green, uint8_t blue)
{
	// Changement de la couleur de la LED
	this->led.setPixelColor(0, this->led.Color(red, green, blue));

#if DEBUG == 1
    LEDManager::logger->info(Logger::logString("[LED] changeColor - Changement de la couleur de la LED (r:%d, g:%d, b:%d)\n", this->red, this->green, this->blue));
#endif

	return ;
}



#endif // _LEDMANAGER_CPP_
