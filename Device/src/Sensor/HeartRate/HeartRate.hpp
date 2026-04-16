/**
 * @file HeartRate.hpp
 * 
 * @brief Déclaration de la classe abstraite HeartRate.
 *
 * Classe intermédiaire dans la hiérarchie des capteurs. Spécialise Sensor pour les capteurs de fréquence cardiaque.
 */

#ifndef _HEARTRATE_HPP_
#define _HEARTRATE_HPP_

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
 * @class HeartRate
 * 
 * @brief Classe abstraite intermédiaire pour les capteurs de fréquence cardiaque.
 */
class HeartRate: public Sensor
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
         * @brief Construit un capteur HeartRate avec le nom donné.
         *
         * @param name Nom du capteur concret.
         */
        HeartRate(std::string name);

// ============================================================================
//  Destructeur
// ============================================================================

    public:
        /**
         * @brief Destructeur d'un capteur HeartRate.
         */
        virtual ~HeartRate();

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



#endif // _HEARTRATE_HPP_
