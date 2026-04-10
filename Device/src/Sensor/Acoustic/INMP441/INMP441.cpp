/**
 * @file INMP441.cpp
 * 
 * @brief Implémentation de la classe INMP441.
 *
 * Implémentation concrète d'un capteur acoustique communiquant via I2S. Hérite de Acoustic.
 */

#ifndef _INMP441_CPP_
#define _INMP441_CPP_

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./INMP441.hpp"

// ============================================================================
//  Variable static
// ============================================================================

const std::string INMP441::name = "INMP441";
Logger * INMP441::logger = nullptr;

// ============================================================================
//  Constructeur
// ============================================================================

INMP441::INMP441(int stadiumBleacherId):
Acoustic(INMP441::name),
stadiumBleacherId(stadiumBleacherId)
{
    INMP441::logger = new Logger("INMP441", true);

    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[INMP441] Instanciation du capteur %s\n", INMP441::name.c_str());
    INMP441::logger->info(str);
}

// ============================================================================
//  Destructeur
// ============================================================================

INMP441::~INMP441()
{
    this->end();
    delete INMP441::logger;
}

// ============================================================================
//  Méthode static
// ============================================================================

std::string INMP441::formatData(INMP441Data & data)
{
    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[INMP441] formatData - DB: [ ");
    for (int i=0; i < NB_VALUE; i++)
    {
        char val[5];
        snprintf(val, sizeof(val), "%d ", data.decibel[i]);
        strcat(str, val);
    }
    strcat(str, "] db\n");
    INMP441::logger->info(str);

    std::string jsonString;
    JsonDocument json;

    // Construction de l'objet JSON avec les données du capteur
    json["t"] = getMQTTTopic(SensorType::ACOUSTIC);
    json["n"] = INMP441::name;
    json["bid"] = stadiumBleacherId;
    JsonArray array = json["db"].to<JsonArray>();
    for (int i=0; i < NB_VALUE; i++)
        array.add(data.decibel[i]);

    // Sérialisation en chaîne JSON + ajout d'un saut de ligne comme délimiteur de message
    serializeJson(json, jsonString);
    jsonString += '\n';

    return jsonString;
}
}

// ============================================================================
//  Méthode
// ============================================================================

void INMP441::begin()
{
    return ;
}



void INMP441::end()
{
    return ;
}



void INMP441::update()
{
    return ;
}



void INMP441::notify(NimBLERemoteCharacteristic *, uint8_t *, size_t)
{
    return ;
}



#endif // _INMP441_CPP_
