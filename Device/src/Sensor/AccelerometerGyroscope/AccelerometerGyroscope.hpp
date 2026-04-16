/**
 * @file AccelerometerGyroscope.hpp
 * 
 * @brief Déclaration de la classe abstraite AccelerometerGyroscope.
 *
 * Classe intermédiaire dans la hiérarchie des capteurs. Spécialise Sensor pour les capteurs combinant accéléromètre et gyroscope.
 */

#ifndef _ACCELEROMETERGYROSCOPE_HPP_
#define _ACCELEROMETERGYROSCOPE_HPP_

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
 * @class AccelerometerGyroscope
 * 
 * @brief Classe abstraite intermédiaire pour les capteurs accéléromètre/gyroscope.
 */
class AccelerometerGyroscope: public Sensor
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
         * @brief Construit un capteur AccelerometerGyroscope avec le nom donné.
         *
         * @param name Nom du capteur concret.
         */
        AccelerometerGyroscope(std::string name);

// ============================================================================
//  Destructeur
// ============================================================================

    public:
        /**
         * @brief Destructeur d'un capteur AccelerometerGyroscope.
         */
        virtual ~AccelerometerGyroscope();

// ============================================================================
//  Méthode
// ============================================================================

    public:
        /**
         * @copydoc Sensor::begin()
         */
        virtual void begin() = 0 override;
        /**
         * @copydoc Sensor::end()
         */
        virtual void end() = 0 override;
        /**
         * @copydoc Sensor::update()
         */
        virtual void update() = 0 override;

};



#endif // _ACCELEROMETERGYROSCOPE_HPP_
