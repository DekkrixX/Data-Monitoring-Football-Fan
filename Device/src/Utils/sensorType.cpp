/**
 * @file sensorType.cpp
 * 
 * @brief Implémentation de getMQTTTopic().
 *
 * Fournit la correspondance entre chaque valeur de l'énumération SensorType et le topic MQTT publié sur le broker.
 */

#ifndef _SENSORTYPE_CPP_
#define _SENSORTYPE_CPP_

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./sensorType.hpp"

// ============================================================================
//  Association du type au topic MQTT
// ============================================================================

std::string getMQTTTopic(SensorType type)
{
    std::string topic;

    switch (type)
    {
        case SensorType::HEART_RATE:
            topic = "heart_rate";
            break;
        case SensorType::ACCELEROMETER_GYROSCOPE:
            topic = "accelerometer_gyroscope";
            break;
        case SensorType::SYSTEM:
            topic = "system";
            break;
        default:
            topic = "default";
    }

    return topic;
}



#endif // _SENSORTYPE_CPP_
