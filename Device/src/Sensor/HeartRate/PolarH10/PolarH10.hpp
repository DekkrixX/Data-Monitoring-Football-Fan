/**
 * @file PolarH10.hpp
 * 
 * @brief Déclaration de la classe PolarH10.
 *
 * Implémentation concrète d'un capteur de fréquence cardiaque Polar H10 communiquant via Bluetooth Low Energy. Hérite de HeartRate et utilise BluetoothLowEnergyManager pour la gestion de la connexion Bluetooth Low Energy.
 *
 * Format JSON produit:
 * @code{.json}
 * {
 *   "type": "heart_rate",
 *   "name": "PolarH10",
 *   "supporter id": <int>,
 *   "heart rate": <int>,
 *   "body sensor location": <string>,
 *   "battery level": <uint8_t>
 * }
 * @endcode
 */

#ifndef _POLARH10_HPP_
#define _POLARH10_HPP_

// ============================================================================
//  Import des headers externes
// ============================================================================

#include <string>
#include <mutex>
#include <atomic>
#include <Arduino.h>
#include <ArduinoJson.h>
#include <NimBLERemoteCharacteristic.h>

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "../HeartRate.hpp"
#include "../../../Utils/sensorType.hpp"
#include "../../../Utils/state.hpp"
#include "../../../Utils/UARTManager/UARTManager.hpp"
#include "../../../Utils/BluetoothLowEnergyManager/BluetoothLowEnergyManager.hpp"

// ============================================================================
//  UUID des services et caractéristiques GATT utilisés
// ============================================================================

/** 
 * @defgroup GATT_UUID UUID GATT du Polar H10
 * @{
 */

#define UUID_BATTERY_SERVICE                            "0000180f-0000-1000-8000-00805f9b34fb" ///< @brief UUID du service Battery.
#define UUID_BATTERY_LEVEL_CHARACTERISTIC               "00002a19-0000-1000-8000-00805f9b34fb" ///< @brief UUID de la caractéristique Battery Level (lecture seule).
#define UUID_HEARTRATE_SERVICE                          "0000180d-0000-1000-8000-00805f9b34fb" ///< @brief UUID du service Heart Rate.
#define UUID_HEARTRATE_MEASUREMENT_CHARACTERISTIC        "00002a37-0000-1000-8000-00805f9b34fb" ///< @brief UUID de la caractéristique Heart Rate Measurement (notification).
#define UUID_HEARTRATE_BODYSENSORLOCATION_CHARACTERISTIC "00002a38-0000-1000-8000-00805f9b34fb" ///< @brief UUID de la caractéristique Body Sensor Location (lecture seule).

/**
 * @}
 */



/**
 * @class PolarH10
 * 
 * @brief Capteur de fréquence cardiaque Polar H10 via Bluetooth Low Energy.
 */
class PolarH10: public HeartRate
{

// ============================================================================
//  Type PolarH10Data
// ============================================================================ 

    private:
        /**
         * @struct PolarH10Data
         * 
         * @brief Données brutes collectées auprès du Polar H10.
         */
        struct PolarH10Data
        {
            int heartRate = -1;                  ///< Fréquence cardiaque en bpm (-1 = non initialisé).
            std::string bodySensorLocation = ""; ///< Localisation du capteur ("" = non initialisé).
            uint8_t batteryLevel = 255;          ///< Niveau de batterie en % (255 = non initialisé).
        };
        using PolarH10Data = struct PolarH10Data;

// ============================================================================
//  Attribut static
// ============================================================================

    public:
        static const std::string name; ///< @brief Nom du capteur.

// ============================================================================
//  Attribut
// ============================================================================

    private:
        const int supporterId;                  ///< Identifiant du porteur du capteur.

        bool isSubscribed;                      ///< Indique si la souscription GATT est active.
        std::atomic<bool> isNotify;             ///< Drapeau indiquant une nouvelle notification reçue.
        PolarH10Data data;                      ///< Dernières données collectées.
        BluetoothLowEnergyManager * bleManager; ///< Gestionnaire Bluetooth Low Energy associé.

// ============================================================================
//  Constructeur
// ============================================================================

    public:
        /**
         * @brief Construit un capteur PolarH10 pour un porteur donné.
         *
         * @param supporterId Identifiant du porteur du capteur.
         */
        PolarH10(int supporterId);

// ============================================================================
//  Destructeur
// ============================================================================

    public:
        /**
         * @brief Arrête le capteur et libère le gestionnaire Bluetooth Low Energy.
         */
        virtual ~PolarH10();

// ============================================================================
//  Méthode static
// ============================================================================

    public:
        /**
         * @brief Sérialise les données du Polar H10 en chaîne JSON.
         *
         * @param data          Référence vers la structure PolarH10Data à sérialiser.
         * @param supporterId   Identifiant du porteur à inclure dans le JSON.
         * 
         * @return std::string Chaîne JSON terminée par un saut de ligne.
         */
        static std::string formatData(PolarH10Data & data, int supporterId);

// ============================================================================
//  Méthode
// ============================================================================

    public:
        /**
         * @brief Initialise le gestionnaire Bluetooth Low Energy.
         */
        void begin() override;
        /**
         * @brief Arrête le gestionnaire Bluetooth Low Energy.
         */
        void end() override;
        /**
         * @brief Met à jour l'état Bluetooth Low Energy, gère la souscription et la sérialisation.
         */
        void update() override;
        /**
         * @brief Traite une notification GATT.
         *
         * @param characteristic Caractéristique ayant émis la notification.
         * @param data           Trame brute de la caractéristique.
         * @param length         Longueur de la trame en octets.
         */
        void notify(NimBLERemoteCharacteristic * characteristic, uint8_t * data, size_t length) override;
    
    private:
        /**
         * @brief Lit les caractéristiques statiques du Polar H10.
         */
        void getData();

};



#endif // _POLARH10_HPP_
