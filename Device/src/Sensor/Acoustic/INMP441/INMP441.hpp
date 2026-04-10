/**
 * @file INMP441.hpp
 * 
 * @brief Déclaration de la classe INMP441.
 *
 * Implémentation concrète d'un capteur acoustique communiquant via I2S. Hérite de Acoustic.
 *
 * Format JSON produit:
 * @code{.json}
 * {
 *   "t": "acoustic",
 *   "n": "INMP441",
 *   "db": [<int>],
 * }
 * @endcode
 */

#ifndef _INMP441_HPP_
#define _INMP441_HPP_

// ============================================================================
//  Import des headres externes
// ============================================================================

#include <string>
#include <Arduino.h>
#include <ArduinoJson.h>

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "../Acoustic.hpp"
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


/*
 * @}
 */

/**
 * @class INMP441
 * 
 * @brief Capteur acoustique INMP441 via I2S
 */
class INMP441: public Acoustic
{

// ============================================================================
//  Type INMP441Data
// ============================================================================

    private:
        /**
         * @struct INMP411Data
         * 
         * @brief Données brutes collectées auprès du INMP441.
         */
        struct INMP441Data
        {
            int decibelIndex = 0;      ///< @brief Taille courante du buffer de décibel.
            int decibel[NB_VALUE] = 0; ///< @brief Buffer de décibel en db.
        };
        using INMP441Data = struct INMP441Data;

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
        INMP441Data data; ///< @brief Dernières données collectées.
        
        int stadiumBleacherId; ///< @brief Identifiant de la tribune.

// ============================================================================
//  Constructeur
// ============================================================================

    public:
        /**
         * @brief Construit un capteur INMP441.
         */
        INMP441(int stadiumBleacherId);

// ============================================================================
//  Destructeur
// ============================================================================

    public:
        /**
         * @brief Destruction du capteur INMP441.
         */
        virtual ~INMP441();

// ============================================================================
//  Méthode static
// ============================================================================

    public:
        /**
         * @brief Sérialise les données du INMP441 en chaîne JSON.
         * 
         * @param data Référence vers la stucture INMP441Data à sérialiser.
         * 
         * @return std::string Chaîne JSON terminée par un saut de ligne.
         */
        static std::string formatData(INMP441Data & data);

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
         * NOT USE
         */
        void notify(NimBLERemoteCharacteristic *, uint8_t *, size_t);

};



#endif // _INMP441git_HPP_