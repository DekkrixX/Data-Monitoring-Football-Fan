/**
 * @file Acoustic.cpp
 * 
 * @brief Implémentation de la classe abstraite Acoustic.
 *
 * Classe intermédiaire dans la hiérarchie des capteurs. Spécialise Sensor pour les capteurs acoustic.
 */

#ifndef _ACOUSTIC_CPP_
#define _ACOUSTIC_CPP_

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./Acoustic.hpp"

// ============================================================================
//  Variables static
// ============================================================================

const SensorType Acoustic::type = SensorType::ACOUSTIC;

// ============================================================================
//  Constructeur
// ============================================================================

Acoustic::Acoustic(std::string name):
Sensor(name, Acoustic::type)
{}

// ============================================================================
//  Destructeur
// ============================================================================

Acoustic::~Acoustic() = default;



#endif // _ACOUSTIC_CPP_
