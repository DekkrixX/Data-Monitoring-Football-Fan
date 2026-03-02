/**
 * @file AccelerometerGyroscope.cpp
 * 
 * @brief Implémentation de la classe abstraite AccelerometerGyroscope.
 *
 * Classe intermédiaire dans la hiérarchie des capteurs. Spécialise Sensor pour les capteurs combinant accéléromètre et gyroscope.
 */

#ifndef _ACCELEROMETERGYROSCOPE_CPP_
#define _ACCELEROMETERGYROSCOPE_CPP_

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./AccelerometerGyroscope.hpp"

// ============================================================================
//  Variables static
// ============================================================================

const SensorType AccelerometerGyroscope::type = SensorType::ACCELEROMETER_GYROSCOPE;

// ============================================================================
//  Constructeur
// ============================================================================

AccelerometerGyroscope::AccelerometerGyroscope(std::string name):
Sensor(name, AccelerometerGyroscope::type)
{}

// ============================================================================
//  Destructeur
// ============================================================================

AccelerometerGyroscope::~AccelerometerGyroscope() = default;



#endif // _ACCELEROMETERGYROSCOPE_CPP_
