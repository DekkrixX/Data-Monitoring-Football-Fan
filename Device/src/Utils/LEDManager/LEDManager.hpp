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

#include <Adafruit_NeoPixel.h>

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
        const int ledNumber;     ///< @brief Nombre de LED associé à la broche.

        bool isOn = false;       ///< @brief État courant de la LED.
        uint8_t red = 0;         ///< @brief Niveau courant de rouge de la LED.
        uint8_t green = 255;     ///< @brief Niveau courant de vert de la LED.
        uint8_t blue = 0;        ///< @brief Niveau courant de bleu de la LED.

        Adafruit_NeoPixel led; ///< @brief Référence vers le port de la LED.

// ============================================================================
//  Constructeur
// ============================================================================

    public:
        /**
         * @brief Construit un LEDManager avec les paramètres matériels donnés.
         *
         * @param ledPin    Broche de la LED.
         * @param ledNumber Nombre de LED associé à la broche.
         */
        LEDManager(int ledPin, int ledNumber);

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
    	/**
    	 * @brief Change la couleur de la LED.
    	 * 
    	 * @param red   Niveau de rouge.
    	 * @param green Niveau de vert.
    	 * @param blue  Niveau de bleu.
    	 */
    	void changeColor(uint8_t red, uint8_t green, uint8_t blue);

};



#endif // _LEDMANAGER_HPP_
