/**
 * @file setting.hpp
 * 
 * @brief Configuration globale du firmware.
 *
 * Centralise tous les paramètres modifiables du projet.
 */

#ifndef _SETTING_HPP_
#define _SETTING_HPP_

// ============================================================================
//  ID du supporter
// ============================================================================

#define SUPPORTER_ID 1 ///< @brief Identifiant numérique unique du porteur du capteur.

// ============================================================================
//  Paramètres des capteurs
// ============================================================================

/**
 * @defgroup Capteur Sélection du capteur actif
 * @{
 */

// Définir exactement UNE de ces macros pour activer le capteur correspondant.

#define POLARH10 1 ///< @brief Active le capteur Polar H10.
#define MAC_ADDRESS "c7:6f:37:f6:01:36" ///< @brief Adresse MAC Bluetooth Low Energy du Polar H10 cible (format "xx:xx:xx:xx:xx:xx").

/**
 * @}
 */

// ============================================================================
//  Paramètres de debug
// ============================================================================

#define DEBUG               1 ///< @brief Activation des messages de debug sur le port série (Serial).
#define BAUDRATE_DEBUG 112500 ///< @brief Vitesse de communication UART en bauds.

// ============================================================================
//  Paramètres UART
// ============================================================================

#define RX_PIN       44 ///< @brief Broche RX de l'UART externe (Serial1).
#define TX_PIN       43 ///< @brief Broche TX de l'UART externe (Serial1).
#define BAUDRATE 112500 ///< @brief Vitesse de communication UART en bauds.



#endif // _SETTING_HPP_
