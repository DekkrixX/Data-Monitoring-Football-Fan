/**
 * @file PolarH10.cpp
 * 
 * @brief Implémentation de la classe PolarH10.
 *
 * Implémentation concrète d'un capteur de fréquence cardiaque Polar H10 communiquant via Bluetooth Low Energy. Hérite de HeartRate et utilise BluetoothLowEnergyManager pour la gestion de la connexion Bluetooth Low Energy.
 */

#ifndef _POLARH10_CPP_
#define _POLARH10_CPP_

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./PolarH10.hpp"

// ============================================================================
//  Variable globale
// ============================================================================

std::mutex dataMutex; ///< @brief Mutex global protégeant les accès concurrents à PolarH10Data.

// ============================================================================
//  Variables static
// ============================================================================

const std::string PolarH10::name = "PolarH10";
Logger * PolarH10::logger = nullptr;

// ============================================================================
//  Constructeur
// ============================================================================

PolarH10::PolarH10(int supporterId):
HeartRate(PolarH10::name),
supporterId(supporterId),
isSubscribed(false),
isNotify(false),
bleManager(nullptr)
{
    PolarH10::logger = new Logger("PolarH10", true);

    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[POLARH10] Instanciation pour le supporter. id: %d, adresse MAC cible: %s\n", supporterId, MAC_ADDRESS);
    PolarH10::logger->info(str);

    // Instanciation du gestionnaire Bluetooth Low Energy avec l'adresse MAC configurée dans setting.hpp
    this->bleManager = new BluetoothLowEnergyManager(MAC_ADDRESS);
}

// ============================================================================
//  Destructeur
// ============================================================================

PolarH10::~PolarH10()
{
    this->end();
    delete this->bleManager;
    delete PolarH10::logger;
}

// ============================================================================
//  Méthode static
// ============================================================================

std::string PolarH10::formatData(PolarH10Data & data, int supporterId)
{
    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[POLARH10] formatData - HR: [ ");
    for (int i=0; i < NB_VALUE; i++)
    {
        char val[5];
        snprintf(val, sizeof(val), "%d ", data.heartRate[i]);
        strcat(str, val);
    }
    strcat(str, "] bpm\n");
    PolarH10::logger->info(str);

    std::string jsonString;
    JsonDocument json;

    // Construction de l'objet JSON avec les données du capteur
    json["t"] = getMQTTTopic(SensorType::HEART_RATE);
    json["n"] = PolarH10::name;
    json["id"] = supporterId;
    JsonArray array = json["hr"].to<JsonArray>();
    for (int i=0; i < NB_VALUE; i++)
        array.add(data.heartRate[i]);

    // Sérialisation en chaîne JSON + ajout d'un saut de ligne comme délimiteur de message
    serializeJson(json, jsonString);
    jsonString += '\n';

    return jsonString;
}

// ============================================================================
//  Méthode
// ============================================================================

void PolarH10::begin()
{
    PolarH10::logger->info("[POLARH10] begin - Démarrage du capteur");

    // Démarrage de la pile Bluetooth Low Energy et du scan
    this->bleManager->begin();

    // État transitoire: en attente de connexion
    Sensor::state = ConnectionState::CONNECTING;

    PolarH10::logger->info("[POLARH10] begin - État: CONNECTING, en attente du périphérique Bluetooth Low Energy");

    return ;
}



void PolarH10::end()
{
    PolarH10::logger->info("[POLARH10] end - Arrêt du capteur");

    // Fermeture de l'interface Bluetooth Low Energy
    this->bleManager->end();

    PolarH10::logger->info("[POLARH10] end - Capteur arrêté");

    return ;
}



void PolarH10::update()
{
    PolarH10::logger->info("[POLARH10] update - Mise à jour du capteur");

    // Délègue la gestion Bluetooth Low Energy au gestionnaire
    this->bleManager->update();

    // Vérifie que le capteur est connecté
    if (this->bleManager->isConnected())
    {
        if (Sensor::state != ConnectionState::CONNECTED)
        {
            Sensor::state = ConnectionState::CONNECTED;

            PolarH10::logger->info("[POLARH10] update - État: CONNECTED");
        }

        // Première connexion: lecture des métadonnées et souscription aux notifications
        if (not this->isSubscribed)
        {
            PolarH10::logger->info("[POLARH10] update - Première connexion: lecture des métadonnées statiques");

            // Lecture bloquante du niveau de batterie et de la localisation du capteur
            this->getData();

            PolarH10::logger->info("[POLARH10] update - Souscription aux notifications Heart Rate active");

            // Souscription aux notifications Heart Rate Measurement
            this->bleManager->subscribe(UUID_HEARTRATE_SERVICE, UUID_HEARTRATE_MEASUREMENT_CHARACTERISTIC);
            this->isSubscribed = true;
        }

        // Si une notification a été reçue depuis le dernier update(), sérialise les données
        if (this->isNotify)
        {
            // Formatage des données
            std::string format;
            
            {
                std::lock_guard<std::mutex> lock(dataMutex);

                format = PolarH10::formatData(this->data, this->supporterId);
                
                // Réinitialisation du drapeau pour la prochaine notification
                this->isNotify = false;
            }

            Sensor::data = format;

            char str[LOGGER_MAX_MESSAGE_SIZE];
            snprintf(str, sizeof(str), "[POLARH10] update - Nouvelle mesure sérialisée: %s", format.c_str()); 
            PolarH10::logger->info(str);
        }
        else
            PolarH10::logger->info("[POLARH10] update - Aucune nouvelle notification depuis le dernier cycle");
    }
    else
    {
        // Déconnexion: réinitialisation pour forcer une nouvelle souscription à la reconnexion
        Sensor::state = ConnectionState::DISCONNECTED;
        this->isSubscribed = false;

        PolarH10::logger->info("[POLARH10] update - État: DISCONNECTED");
    }

    return ;
}



void PolarH10::getData()
{
    PolarH10::logger->info("[POLARH10] getData - Lecture des caractéristiques statiques");

    NimBLEAttValue value;

    std::lock_guard<std::mutex> lock(dataMutex);

    PolarH10::logger->info("[POLARH10] getData - Lecture du niveau de batterie");

    // Lecture du niveau de batterie: boucle jusqu'à obtenir une valeur valide (!= 255)
    uint8_t batteryLevel = 255;
    while (batteryLevel == 255 and this->isConnected())
    {
        // La caractéristique Battery Level est un unique octet (valeur 0–100%)
        value = this->bleManager->getValue(UUID_BATTERY_SERVICE, UUID_BATTERY_LEVEL_CHARACTERISTIC);
        if (value.size() == 1)
        {
            const uint8_t * data = value.data();
            batteryLevel = data[0];

            char str[LOGGER_MAX_MESSAGE_SIZE];
            snprintf(str, sizeof(str), "[POLARH10] getData - Niveau de batterie: %u%%\n", batteryLevel);
            PolarH10::logger->info(str);
        } 
    }

    PolarH10::logger->info("[POLARH10] getData - Lecture de la localisation du capteur");

    // Lecture de la localisation du capteur: boucle jusqu'à obtenir une valeur valide (!= "")
    std::string bodySensorLocation = "";
    while (bodySensorLocation == "" and this->isConnected())
    {
        // La caractéristique Body Sensor Location est un unique octet (enum 0–6)
        value = this->bleManager->getValue(UUID_HEARTRATE_SERVICE, UUID_HEARTRATE_BODYSENSORLOCATION_CHARACTERISTIC);
        if (value.size() == 1)
        {
            const uint8_t * data = value.data();
            switch (data[0])
            {
                case 0:
                    bodySensorLocation = "Other";
                    break;
                case 1:
                    bodySensorLocation = "Chest";
                    break;
                case 2:
                    bodySensorLocation = "Wrist";
                    break;
                case 3:
                    bodySensorLocation = "Finger";
                    break;
                case 4:
                    bodySensorLocation = "Hand";
                    break;
                case 5:
                    bodySensorLocation = "Ear Lobe";
                    break;
                case 6:
                    bodySensorLocation = "Foot";
                    break;
                default:
                    bodySensorLocation = "Reserved";
            }

            char str[LOGGER_MAX_MESSAGE_SIZE];
            snprintf(str, sizeof(str), "[POLARH10] getData - Localisation: %s (code: %u)\n",
                    bodySensorLocation.c_str(), data[0]);
            PolarH10::logger->info(str);
        }
    }

    PolarH10::logger->info("[POLARH10] getData - Lecture des caractéristiques statiques terminée");

    std::string jsonString;
    JsonDocument json;

    json["t"] = getMQTTTopic(SensorType::SYSTEM);
    json["n"] = PolarH10::name;
    json["id"] = this->supporterId;
    json["bsl"] = bodySensorLocation;
    json["bl"] = batteryLevel;

    // Sérialisation en chaîne JSON + ajout d'un saut de ligne comme délimiteur de message
    serializeJson(json, jsonString);
    jsonString += '\n';

    Sensor::data = jsonString;

    return ;
}



void PolarH10::notify(NimBLERemoteCharacteristic * characteristic, uint8_t * data, size_t length)
{
    NimBLEUUID uuid = NimBLEUUID(UUID_HEARTRATE_MEASUREMENT_CHARACTERISTIC);

    std::lock_guard<std::mutex> lock(dataMutex);

    // Vérifie que la notification provient bien de la caractéristique Heart Rate Measurement
    if (characteristic->getUUID() == uuid)
    {
        if (length > 1)
        {
            /* 
            Bit 0 du premier octet indique le format de la valeur de fréquence cardiaque :
                0 = format UINT8  (data[1])
                1 = format UINT16 (data[1] | data[2] << 8)
            */
            if (data[0] & 0x01)
            {
                // Fréquence cardiaque encodée sur 16 bits
                this->data.heartRate[this->data.heartRateIndex] = static_cast<int>( data[1] | (data[2] << 8) );

                char str[LOGGER_MAX_MESSAGE_SIZE];
                snprintf(str, sizeof(str), "[POLARH10] notify - Fréquence cardiaque (UINT16): %d bpm\n", this->data.heartRate[this->data.heartRateIndex]);
                PolarH10::logger->info(str);

                this->data.heartRateIndex++;
            }
            else
            {
                // Fréquence cardiaque encodée sur 8 bits
                this->data.heartRate[this->data.heartRateIndex] = static_cast<int>(data[1]);

                char str[LOGGER_MAX_MESSAGE_SIZE];
                snprintf(str, sizeof(str), "[POLARH10] notify - Fréquence cardiaque (UINT8): %d bpm\n", this->data.heartRate[this->data.heartRateIndex]);
                PolarH10::logger->info(str);

                this->data.heartRateIndex++;
            }
            // Reset du buffer si besoin
            if (this->data.heartRateIndex >= NB_VALUE)
                this->data.heartRateIndex = 0;
        }
        else
        {
            char str[LOGGER_MAX_MESSAGE_SIZE];
            snprintf(str, sizeof(str), "[POLARH10] notify - Trame HeartRate trop courte (%u octet), ignorée\n", length);
            PolarH10::logger->warning(str);
        }
    }
    else
    {
        char str[LOGGER_MAX_MESSAGE_SIZE];
        snprintf(str, sizeof(str), "[POLARH10] notify - Notification ignorée: UUID %s non reconnu\n", characteristic->getUUID().toString().c_str());
        PolarH10::logger->warning(str);
    }

    // Signale une nouvelle donnée disponible uniquement si la valeur est cohérente
    if (this->data.heartRateIndex > 0)
        this->isNotify = true;

    return ;
}



#endif // _POLARH10_CPP_
