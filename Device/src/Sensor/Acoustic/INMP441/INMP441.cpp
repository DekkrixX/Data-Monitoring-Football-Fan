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
int32_t INMP441::audioSample[I2S_BUFFER_SIZE];
Logger * INMP441::logger = nullptr;

// ============================================================================
//  Constructeur
// ============================================================================

INMP441::INMP441(int stadiumBleacherId):
Acoustic(INMP441::name),
stadiumBleacherId(stadiumBleacherId)
{
    if (INMP441::logger == nullptr)
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

std::string INMP441::formatData(INMP441Data & data, int stadiumBleacherId)
{
#if DEBUG == 1
    std::string str = "[INMP441] formatData - DB: [ ";
    for (int i=0; i < NB_VALUE; i++)
    {
        char val[32];
        snprintf(val, sizeof(val), "%f ", data.decibel[i]);
        str += val;
    }
    str += "] db\n";
    INMP441::logger->info(str.c_str());
#endif

    std::string jsonString;
    JsonDocument json;

    // Construction de l'objet JSON avec les données du capteur
    json["t"] = getMQTTTopic(SensorType::ACOUSTIC);
    json["n"] = INMP441::name;
    json["id"] = stadiumBleacherId;
    JsonArray array = json["a"].to<JsonArray>();
    for (int i=0; i < NB_VALUE; i++)
        array.add(data.decibel[i]);

    // Sérialisation en chaîne JSON + ajout d'un saut de ligne comme délimiteur de message
    serializeJson(json, jsonString);
    jsonString += '\n';

    return jsonString;
}

// ============================================================================
//  Méthode
// ============================================================================

void INMP441::begin()
{
#if DEBUG == 1
    INMP441::logger->info(Logger::logString("[INMP441] begin - Démarrage du capteur\n"));
#endif

    // Configuration du driver I2S
    i2s_config_t i2s_config = {};
    i2s_config.mode = (i2s_mode_t) (I2S_MODE_MASTER | I2S_MODE_RX);
    i2s_config.sample_rate = I2S_SAMPLE_RATE;
    i2s_config.bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT;
    i2s_config.channel_format = I2S_CHANNEL_FMT_ONLY_LEFT;
    i2s_config.communication_format = I2S_COMM_FORMAT_STAND_I2S,
    i2s_config.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
    i2s_config.dma_buf_count = 4;
    i2s_config.dma_buf_len = I2S_BUFFER_SIZE;
    i2s_config.use_apll = false;

    // Configuration des pins
    i2s_pin_config_t pin_config = {};
    pin_config.bck_io_num = SCK_PIN;
    pin_config.ws_io_num = WS_PIN;
    pin_config.data_out_num = I2S_PIN_NO_CHANGE;
    pin_config.data_in_num = SD_PIN;
    pin_config.mck_io_num = I2S_PIN_NO_CHANGE;

#if DEBUG == 1
    INMP441::logger->info(Logger::logString("[INMP441-9 V6] begin - Configuration du driver et des pins I2S"));
#endif

    // Application des configurations
    if (i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL) != ESP_OK)
    {
        std::string str = Logger::logString("[INMP441] begin - Échec de la configuration du driver I2S\n");
#if DEBUG == 1
        INMP441::logger->error(str);
#endif
        throw std::runtime_error(str);
    }

    if (i2s_set_pin(I2S_PORT, &pin_config) != ESP_OK)
    {
        std::string str = Logger::logString("[INMP441] begin - Échec de la configuration des pins I2S\n");
#if DEBUG == 1
        INMP441::logger->error(str);
#endif
        throw std::runtime_error(str);
    }

    Sensor::state = ConnectionState::CONNECTED;
    
    return ;
}



void INMP441::end()
{
#if DEBUG == 1
    INMP441::logger->info(Logger::logString("[INMP441] end - Arrêt du capteur\n"));
#endif

    Sensor::state = ConnectionState::DISCONNECTED;

#if DEBUG == 1
    INMP441::logger->info(Logger::logString("[INMP441] end - Capteur arrêté\n"));
#endif

    return ;
}



void INMP441::update()
{
#if DEBUG == 1
    INMP441::logger->info(Logger::logString("[INMP441] update - Mise à jour du capteur\n"));
#endif

    size_t bytesRead = 0;

    // Lecture de la trame
    i2s_read(I2S_PORT, INMP441::audioSample, sizeof(INMP441::audioSample), &bytesRead, 100 / portTICK_PERIOD_MS);

    int samples = bytesRead / sizeof(int32_t);
    if (samples > 0)
    {
#if DEBUG == 1
        INMP441::logger->info(Logger::logString("[INMP441] update - Samples reçu: %d\n", samples));
#endif

        // Calcul du RMS
        double sum = 0;
        for (int i=0; i < samples; i++)
        {
            double sample = INMP441::audioSample[i];
            sum += sample * sample;
        }

        double rms = sqrt(sum / samples);

        // Convertion en décibel
        double db = 20.0 * log10((rms + 1) / RMS_REFERENCE);

        this->data.decibel[this->data.decibelIndex] = db;

        // Mise à jour des données
        std::string format = INMP441::formatData(this->data, this->stadiumBleacherId);
        Sensor::data = format;

#if DEBUG == 1
        INMP441::logger->info(Logger::logString("[INMP441] update - Nouvelle mesure sérialisée: %s", format.c_str()));
#else
        INMP441::logger->info(Logger::logString("db: %f\n", this->data.decibel[this->data.decibelIndex]));
#endif

        this->data.decibelIndex++;
        if (this->data.decibelIndex == NB_VALUE)
            this->data.decibelIndex = 0;
    }

    return ;
}



void INMP441::notify(NimBLERemoteCharacteristic *, uint8_t *, size_t)
{
    return ;
}



#endif // _INMP441_CPP_
