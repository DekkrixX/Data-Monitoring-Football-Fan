/**
 * @file Sensor.cpp
 * 
 * @brief Implémentation des méthodes communes de la classe abstraite Sensor.
 *
 * Définit l'interface commune à tous les capteurs du système. Chaque capteur concret doit hériter de cette classe et implémenter les méthodes virtuelles pures begin(), end(), update() et notify().
 */

#ifndef _SENSOR_CPP_
#define _SENSOR_CPP_

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./Sensor.hpp"

// ============================================================================
//  Constructeur
// ============================================================================

Sensor::Sensor(std::string name, SensorType type):
name(name),
type(type)
{}

// ============================================================================
//  Destructeur
// ============================================================================

Sensor::~Sensor() = default;

// ============================================================================
//  Méthode
// ============================================================================

bool Sensor::isConnected()
{
    return this->state == ConnectionState::CONNECTED;
}



std::string Sensor::getSensorData()
{
    return this->data;
}



SensorType Sensor::getSensorType()
{
    return this->type;
}



std::string Sensor::getSensorName()
{
    return this->name;
}



#endif // _SENSOR_CPP_
