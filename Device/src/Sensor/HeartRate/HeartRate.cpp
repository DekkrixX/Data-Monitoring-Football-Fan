/**
 * @file HeartRate.cpp
 * 
 * @brief Implémentation de la classe abstraite HeartRate.
 *
 * Classe intermédiaire dans la hiérarchie des capteurs. Spécialise Sensor pour les capteurs de fréquence cardiaque.
 */

#ifndef _HEARTRATE_CPP_
#define _HEARTRATE_CPP_

// ============================================================================
//  Import des headers
// ============================================================================

#include "./HeartRate.hpp"

// ============================================================================
//  Variables static
// ============================================================================

const SensorType HeartRate::type = SensorType::HEART_RATE;

// ============================================================================
//  Constructeur
// ============================================================================

HeartRate::HeartRate(std::string name):
Sensor(name, HeartRate::type)
{}

// ============================================================================
//  Destructeur
// ============================================================================

HeartRate::~HeartRate() = default;



#endif // _HEARTRATE_CPP_
