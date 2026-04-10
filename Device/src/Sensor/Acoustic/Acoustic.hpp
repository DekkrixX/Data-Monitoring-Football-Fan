/**
 * @file Acoustic.hpp
 * 
 * @brief Déclaration de la classe abstraite Acoustic.
 *
 * Classe intermédiaire dans la hiérarchie des capteurs. Spécialise Sensor pour les capteurs acoustique.
 */

#ifndef _ACOUSTIC_HPP_
#define _ACOUSTIC_HPP_

// ============================================================================
//  Import des headers externes
// ============================================================================

#include <string>

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "../Sensor.hpp"
#include "../../Utils/sensorType.hpp"



/**
 * @class Acoustic
 * 
 * @brief Classe abstraite intermédiaire pour les capteurs acoustic.
 */
class Acoustic: public Sensor
{

// ============================================================================
//  Attribut static
// ============================================================================

    public:
        static const SensorType type; ///< @brief Type du capteur.

// ============================================================================
//  Constructeur
// ============================================================================

    public:
        /**
         * @brief Construit un capteur Acoustic avec le nom donné.
         *
         * @param name Nom du capteur concret.
         */
        Acoustic(std::string name);

// ============================================================================
//  Destructeur
// ============================================================================

    public:
        /**
         * @brief Destructeur d'un capteur Acoustic.
         */
        virtual ~Acoustic();

// ============================================================================
//  Méthode
// ============================================================================

    public:
        /**
         * @copydoc Sensor::begin()
         */
        virtual void begin() = 0;
        /**
         * @copydoc Sensor::end()
         */
        virtual void end() = 0;
        /**
         * @copydoc Sensor::update()
         */
        virtual void update() = 0;

};



#endif // _ACOUSTIC_HPP_
