/**
 * @file LEDManager.hpp
 * 
 * @brief Déclaration de la classe LEDManager.
 *
 * Fournit une abstraction haut niveau de la led de la carte ESP32.
 */

#ifndef _LEDMANAGER_HPP_
#define _LEDMANAGER_HPP_

// ============================================================================
//  Import des headers externes
// ============================================================================

#include <Arduino.h>

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "../../Config/setting.hpp"
#include "../Logger/Logger.hpp"



/**
 * @class LEDManager
 * 
 * @brief Gestionnaire de la LED de la carte ESP32.
 */
class LEDManager
{

// ============================================================================
//  Attribut static
// ============================================================================

    private:
        static Logger * logger; ///< @brief Logger qui écrit les logs dans un fichier

// ============================================================================
//  Attribut
// ============================================================================

    private:
        const int ledPin;        ///< @brief Numéro de broche de la LED.

        bool isOn = false;       ///< @brief État courant de la LED.

// ============================================================================
//  Constructeur
// ============================================================================

    public:
        /**
         * @brief Construit un LEDManager avec les paramètres matériels donnés.
         *
         * @param ledPin    Broche de la LED.
         */
        LEDManager(int ledPin);

// ============================================================================
//  Destructeur
// ============================================================================

    public:
        /**
         * @brief Destruction de l'objet.
         */
        virtual ~LEDManager();

// ============================================================================
//  Méthode
// ============================================================================

    public:
    	/**
    	 * @brief Initialisation de la LED.
    	 */
    	void begin();
    	/**
    	 * @brief Extinction de la LED.
    	 */
    	void end();
    	/**
    	 * @brief Allume la LED.
    	 */
    	void turnOn();
    	/**
    	 * @brief Éteind la LED.
    	 */
    	void turnOff();
    	/**
    	 * @brief Change l'état de la LED.
    	 */
    	void toggle();

};



#endif // _LEDMANAGER_HPP_
