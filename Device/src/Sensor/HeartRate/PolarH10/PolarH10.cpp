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
    if (DEBUG)
    {
        Serial.printf("[POLARH10] Instanciation pour le supporter. id: %d, adresse MAC cible: %s\n", supporterId, MAC_ADDRESS);
        Serial.flush();
    }

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
}

// ============================================================================
//  Méthode static
// ============================================================================

std::string PolarH10::formatData(PolarH10Data & data, int supporterId)
{
    if (DEBUG)
    {
        Serial.printf("[POLARH10] formatData - HR: ");
        Serial.flush();
        for (int i=0; i < NB_VALUE; i++){
            Serial.printf("%d ", data.heartRate[i]);
            Serial.flush();
        }
        Serial.printf("bpm, localisation: %s, batterie: %u%%\n", data.bodySensorLocation.c_str(), data.batteryLevel);
        Serial.flush();
    }

    std::string jsonString;
    JsonDocument json;

    std::lock_guard<std::mutex> lock(dataMutex);

    // Construction de l'objet JSON avec les données du capteur
    json["t"] = getMQTTTopic(SensorType::HEART_RATE);
    json["n"] = PolarH10::name;
    json["id"] = supporterId;
    JsonArray array = json["hr"].to<JsonArray>();
    for (int i=0; i < NB_VALUE; i++)
        array.add(data.heartRate[i]);
    json["bsl"] = data.bodySensorLocation;
    json["bl"] = data.batteryLevel;

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
    if (DEBUG)
    {
        Serial.println("[POLARH10] begin - Démarrage du capteur");
        Serial.flush();
    }

    // Démarrage de la pile Bluetooth Low Energy et du scan
    this->bleManager->begin();

    // État transitoire: en attente de connexion
    Sensor::state = ConnectionState::CONNECTING;

    if (DEBUG)
    {
        Serial.println("[POLARH10] begin - État: CONNECTING, en attente du périphérique Bluetooth Low Energy");
        Serial.flush();
    }

    return ;
}



void PolarH10::end()
{
    if (DEBUG)
    {
        Serial.println("[POLARH10] end - Arrêt du capteur");
        Serial.flush();
    }

    // Fermeture de l'interface Bluetooth Low Energy
    this->bleManager->end();

    if (DEBUG)
    {
        Serial.println("[POLARH10] end - Capteur arrêté");
        Serial.flush();
    }

    return ;
}



void PolarH10::update()
{
    if (DEBUG)
    {
        Serial.println("[POLARH10] update - Mise à jour du capteur");
        Serial.flush();
    }

    // Délègue la gestion Bluetooth Low Energy au gestionnaire
    this->bleManager->update();

    // Vérifie que le capteur est connecté
    if (this->bleManager->isConnected())
    {
        if (Sensor::state != ConnectionState::CONNECTED)
        {
            Sensor::state = ConnectionState::CONNECTED;

            if (DEBUG)
            {
                Serial.println("[POLARH10] update - État: CONNECTED");
                Serial.flush();
            }
        }

        // Première connexion: lecture des métadonnées et souscription aux notifications
        if (not this->isSubscribed)
        {
            if (DEBUG)
            {
                Serial.println("[POLARH10] update - Première connexion: lecture des métadonnées statiques");
                Serial.flush();
            }

            // Lecture bloquante du niveau de batterie et de la localisation du capteur
            this->getData();

            if (DEBUG)
            {
                Serial.printf("[POLARH10] update - Batterie: %u%%, localisation: %s\n", this->data.batteryLevel, this->data.bodySensorLocation.c_str());
                Serial.flush();
                Serial.println("[POLARH10] update - Souscription aux notifications Heart Rate active");
                Serial.flush();
            }

            // Souscription aux notifications Heart Rate Measurement
            this->bleManager->subscribe(UUID_HEARTRATE_SERVICE, UUID_HEARTRATE_MEASUREMENT_CHARACTERISTIC);
            this->isSubscribed = true;
        }

        // Si une notification a été reçue depuis le dernier update(), sérialise les données
        if (this->isNotify)
        {
            // Formatage des données
            std::string format = PolarH10::formatData(this->data, this->supporterId);
            Sensor::data = format;

            if (DEBUG)
            {
                Serial.printf("[POLARH10] update - Nouvelle mesure sérialisée: %s", format.c_str());
                Serial.flush();
            }

            // Réinitialisation du drapeau pour la prochaine notification
            this->isNotify = false;
        }
        else
        {
            if (DEBUG)
            {
                Serial.println("[POLARH10] update - Aucune nouvelle notification depuis le dernier cycle");
                Serial.flush();
            }
        }
    }
    else
    {
        // Déconnexion: réinitialisation pour forcer une nouvelle souscription à la reconnexion
        Sensor::state = ConnectionState::DISCONNECTED;
        this->isSubscribed = false;

        if (DEBUG)
        {
            Serial.println("[POLARH10] update - État: DISCONNECTED");
            Serial.flush();
        }
    }

    return ;
}



void PolarH10::getData()
{
    if (DEBUG)
    {
        Serial.println("[POLARH10] getData - Lecture des caractéristiques statiques");
        Serial.flush();
    }

    NimBLEAttValue value;

    std::lock_guard<std::mutex> lock(dataMutex);

    if (DEBUG)
    {
        Serial.println("[POLARH10] getData - Lecture du niveau de batterie");
        Serial.flush();
    }

    // Lecture du niveau de batterie: boucle jusqu'à obtenir une valeur valide (!= 255)
    while (this->data.batteryLevel == 255 and this->isConnected())
    {
        // La caractéristique Battery Level est un unique octet (valeur 0–100%)
        value = this->bleManager->getValue(UUID_BATTERY_SERVICE, UUID_BATTERY_LEVEL_CHARACTERISTIC);
        if (value.size() == 1)
        {
            const uint8_t * data = value.data();
            this->data.batteryLevel = data[0];

            if (DEBUG)
            {
                Serial.printf("[POLARH10] getData - Niveau de batterie: %u%%\n", this->data.batteryLevel);
                Serial.flush();
            }
        } 
    }

    if (DEBUG)
    {
        Serial.println("[POLARH10] getData - Lecture de la localisation du capteur");
        Serial.flush();
    }

    // Lecture de la localisation du capteur: boucle jusqu'à obtenir une valeur valide (!= "")
    while (this->data.bodySensorLocation == "" and this->isConnected())
    {
        // La caractéristique Body Sensor Location est un unique octet (enum 0–6)
        value = this->bleManager->getValue(UUID_HEARTRATE_SERVICE, UUID_HEARTRATE_BODYSENSORLOCATION_CHARACTERISTIC);
        if (value.size() == 1)
        {
            const uint8_t * data = value.data();
            switch (data[0])
            {
                case 0:
                    this->data.bodySensorLocation = "Other";
                    break;
                case 1:
                    this->data.bodySensorLocation = "Chest";
                    break;
                case 2:
                    this->data.bodySensorLocation = "Wrist";
                    break;
                case 3:
                    this->data.bodySensorLocation = "Finger";
                    break;
                case 4:
                    this->data.bodySensorLocation = "Hand";
                    break;
                case 5:
                    this->data.bodySensorLocation = "Ear Lobe";
                    break;
                case 6:
                    this->data.bodySensorLocation = "Foot";
                    break;
                default:
                    this->data.bodySensorLocation = "Reserved";
            }

            if (DEBUG)
            {
                Serial.printf("[POLARH10] getData - Localisation: %s (code: %u)\n",
                    this->data.bodySensorLocation.c_str(), data[0]);
                Serial.flush();
            }
        }
    }

    if (DEBUG)
    {
        Serial.println("[POLARH10] getData - Lecture des caractéristiques statiques terminée");
        Serial.flush();
    }

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

                if (DEBUG)
                {
                    Serial.printf("[POLARH10] notify - Fréquence cardiaque (UINT16): %d bpm\n", this->data.heartRate[this->data.heartRateIndex]);
                    Serial.flush();
                }

                this->data.heartRateIndex++;
            }
            else
            {
                // Fréquence cardiaque encodée sur 8 bits
                this->data.heartRate[this->data.heartRateIndex] = static_cast<int>(data[1]);

                if (DEBUG)
                {
                    Serial.printf("[POLARH10] notify - Fréquence cardiaque (UINT8): %d bpm\n", this->data.heartRate[this->data.heartRateIndex]);
                    Serial.flush();
                }

                this->data.heartRateIndex++;
            }
            // Reset du buffer si besoin
            if (this->data.heartRateIndex >= NB_VALUE)
                this->data.heartRateIndex = 0;
        }
        else
        {
            if (DEBUG)
            {
                Serial.printf("[POLARH10] notify - Trame HeartRate trop courte (%u octet), ignorée\n", length);
                Serial.flush();
            }
        }
    }
    else
    {
        if (DEBUG)
        {
            Serial.printf("[POLARH10] notify - Notification ignorée: UUID %s non reconnu\n",
                characteristic->getUUID().toString().c_str());
            Serial.flush();
        }
    }

    // Signale une nouvelle donnée disponible uniquement si la valeur est cohérente
    if (this->data.heartRate != 0)
        this->isNotify = true;

    return ;
}



#endif // _POLARH10_CPP_
