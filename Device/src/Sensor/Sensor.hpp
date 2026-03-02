/**
 * @file Sensor.hpp
 * 
 * @brief Déclaration de la classe abstraite Sensor.
 *
 * Définit l'interface commune à tous les capteurs du système. Chaque capteur concret doit hériter de cette classe et implémenter les méthodes virtuelles pures begin(), end(), update() et notify().
 */

#ifndef _SENSOR_HPP_
#define _SENSOR_HPP_

// ============================================================================
//  Import des headers externes
// ============================================================================

#include <string>
#include <NimBLERemoteCharacteristic.h>

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "../Utils/state.hpp"
#include "../Utils/sensorType.hpp"



/**
 * @class Sensor
 * 
 * @brief Interface abstraite pour tous les capteurs du système.
 */
class Sensor
{

// ============================================================================
//  Attribut
// ============================================================================

    protected:
        const std::string name;                                ///< Nom identifiant le capteur.
        const SensorType type;                                 ///< Type fonctionnel du capteur.
        
        ConnectionState state = ConnectionState::DISCONNECTED; ///< État courant de la connexion.
        std::string data;                                      ///< Dernière mesure sérialisée (JSON).

// ============================================================================
//  Constructeur
// ============================================================================

    public:
        /**
         * @brief Construit un capteur avec un nom et un type donnés.
         *
         * @param name Nom du capteur.
         * @param type Type fonctionnel.
         */
        Sensor(std::string name, SensorType type);

// ============================================================================
//  Destructeur
// ============================================================================

    public:
        /**
         * @brief Destructeur d'un capteur.
         */
        virtual ~Sensor();

// ============================================================================
//  Méthode
// ============================================================================

    public:
        /**
         * @brief Initialise et démarre le capteur.
         */
        virtual void begin() = 0;
        /**
         * @brief Arrête le capteur et libère ses ressources.
         */
        virtual void end() = 0;
        /**
         * @brief Met à jour l'état et les données du capteur.
         */
        virtual void update() = 0;
        /**
         * @brief Traite une notification Bluetooth Low Energy reçue par le gestionnaire Bluetooth Low Energy, appelé depuis le callback statique de BluetoothLowEnergyManager lorsqu'une notification GATT est reçue.
         *
         * @param characteristic Caractéristique Bluetooth Low Energy ayant émis la notification.
         * @param data           Pointeur vers les données brutes reçues.
         * @param length         Taille des données en octets.
         */
        virtual void notify(NimBLERemoteCharacteristic * characteristic, uint8_t * data, size_t length) = 0;
        /**
         * @brief Indique si le capteur est actuellement connecté.
         *
         * @return true  Connecté.
         * @return false Déconnecté.
         */
        bool isConnected();
        /**
         * @brief Retourne la dernière mesure sérialisée du capteur.
         *
         * @return std::string Données au format JSON (chaîne vide si aucune mesure).
         */
        std::string getSensorData();
        /**
         * @brief Retourne le type fonctionnel du capteur.
         *
         * @return SensorType Type du capteur.
         */
        SensorType getSensorType();
        /**
         * @brief Retourne le nom du capteur.
         *
         * @return std::string Nom du capteur.
         */
        std::string getSensorName();

};



#endif // _SENSOR_HPP_
