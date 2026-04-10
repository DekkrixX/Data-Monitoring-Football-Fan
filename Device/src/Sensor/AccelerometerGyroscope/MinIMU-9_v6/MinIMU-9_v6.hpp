/**
 * @file MinIMU-9_v6.hpp
 * 
 * @brief Déclaration de la classe MinIMU_9_v6.
 *
 * Implémentation concrète d'un capteur accéléromètre et gyroscope communiquant via I2C. Hérite de AccelerometerGyroscope.
 *
 * Format JSON produit:
 * @code{.json}
 * {
 *   "t": "accelerometer_gyroscope",
 *   "n": "MinUMI-9 v6",
 *   "a": [[<int>, <int>, <int>]],
 *   "g": [[<int>, <int>, <int>]],
 *   "m": [[<int>, <int>, <int>]]
 * }
 * @endcode
 */

#ifndef _MINIMU_9_V6_HPP_
#define _MINIMU_9_V6_HPP_

// ============================================================================
//  Import des headres externes
// ============================================================================

#include <string>
#include <Arduino.h>
#include <ArduinoJson.h>
#include <Wire.h>

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "../AccelerometerGyroscope.hpp"
#include "../../../Config/setting.hpp"
#include "../../../Utils/sensorType.hpp"
#include "../../../Utils/state.hpp"
#include "../../../Utils/Logger/Logger.hpp"

// ============================================================================
//  Configuration des registres
// ============================================================================

/**
 * @defgroup CONFIG_MINIMU_9_V6 Configuration des registres du capteur MinIMU-9 v6
 * @{
 */

#define LSM6DS33_ADDRESS 0x6B ///< @brief Adresse de l'accéléromètre et du gyroscope.
#define LIS3MDL_ADDRESS  0x1E ///< @brief Adresse du magnétomètre.

#define REGISTER_ACCELEROMETER_NUMBER 0x10 ///< @brief Numéro du registre de l'accéléromètre.
#define REGISTER_ACCELEROMETER_OUT    0x28 ///< @brief Numéro du registre de sortie de l'accéléromètre.
#define REGISTER_ACCELEROMETER_VALUE  0x80 ///< @brief Valeur du registre de l'accéléromètre.
#define REGISTER_GYROSCOPE_NUMBER     0x11 ///< @brief Numéro du registre du gyroscope.
#define REGISTER_GYROSCOPE_OUT        0x22 ///< @brief Numéro du registre de sortie du gyroscope.
#define REGISTER_GYROSCOPE_VALUE      0x80 ///< @brief Valeur du registre du gyroscope.
#define REGISTER_MAGNETOMETER_NUMBER  0x20 ///< @brief Numéro du registre du magnétomètre.
#define REGISTER_MAGNETOMETER_OUT     0x28 ///< @brief Numéro du registre de sortie du magnétomètre.
#define REGISTER_MAGNETOMETER_VALUE   0x70 ///< @brief Valeur du registre du magnétomètre.

/*
 * @}
 */

/**
 * @class MinIMU_9_v6
 * 
 * @brief Capteur accéléromètre et gyroscope MinIMU-9 v6 via I2C
 */
class MinIMU_9_v6: public AccelerometerGyroscope
{

// ============================================================================
//  Type MinIMU_9_v6Data
// ============================================================================

    private:
        /**
         * @struct MinIMU_9v6Data
         * 
         * @brief Données brutes collectées auprès du MinIMU-9 v6.
         */
        struct MinIMU_9_v6Data
        {
            int accelerometer[3] = {-1, -1, -1}; ///< @brief Données de l'accéléromètre.
            int gyroscope[3]     = {-1, -1, -1}; ///< @brief Données du gyroscope.
            int magnetometer[3]  = {-1, -1, -1}; ///< @brief Données du magnétomètre.

            int verticalAccelerationVector[4] = {-1, -1, -1, -1}; ///< @brief Vecteur accélération vertical.
        };
        using MinIMU_9_v6Data = struct MinIMU_9_v6Data;

// ============================================================================
//  Attribut static
// ============================================================================

    public:
        static const std::string name; ///< @brief Nom du capteur.
    private:
        static Logger * logger; /// <@brief Logger qui écrit les logs dans un fichier.

// ============================================================================
//  Attribut
// ============================================================================

    private:
        MinIMU_9_v6Data data; ///< @brief Dernières données collectées.
        
        int supporterId; ///< @brief Identifiant du supporter.

// ============================================================================
//  Constructeur
// ============================================================================

    public:
        /**
         * @brief Construit un capteur MinIMU-9 v6.
         */
        MinIMU_9_v6(int supporterId);

// ============================================================================
//  Destructeur
// ============================================================================

    public:
        /**
         * @brief Destruction du capteur MinIMU-9 v6.
         */
        virtual ~MinIMU_9_v6();

// ============================================================================
//  Méthode static
// ============================================================================

    public:
        /**
         * @brief Sérialise les données du MinIMU-9 v6 en chaîne JSON.
         * 
         * @param data Référence vers la stucture MinIMU_9_v6Data à sérialiser.
         * 
         * @return std::string Chaîne JSON terminée par un saut de ligne.
         */
        static std::string formatData(MinIMU_9_v6Data & data);

// ============================================================================
//  Méthode
// ============================================================================

    public:
        /**
         */
        void begin();
        
        /**
         */
        void update();
        
        /**
         */
        void end();

        /**
         * @brief Lis le registre de l'addresse donné.
         * 
         * @param address
         * @param registerAddress
         * @param out
         */
        void readRegister(uint8_t address, uint8_t registerAddress, int * out);

        /**
         * @brief Écrit dans le registre de l'addresse donné.
         * 
         * @param address
         * @param registerAddress
         * @param value
         */
        void writeRegister(uint8_t address, uint8_t registerAddress, uint8_t value);

        /**
         * NOT USE
         */
        void notify(NimBLERemoteCharacteristic *, uint8_t *, size_t);

};



#endif // _MINIMU_9_V6_HPP_
