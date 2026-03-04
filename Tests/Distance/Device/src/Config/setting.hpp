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
//  Message de test
// ============================================================================

// À MODIFIER
#define MESSAGE "Message 1" ///< @brief Message de test de la transmission.

// ============================================================================
//  Paramètres MQTT
// ============================================================================

#define TOPIC_MQTT "system" ///< @brief Topic MQTT sur lequel sera publié le message.

// ============================================================================
//  Paramètres UART
// ============================================================================

#define RX_PIN       44 ///< @brief Broche RX de l'UART externe (Serial1).
#define TX_PIN       43 ///< @brief Broche TX de l'UART externe (Serial1).
#define BAUDRATE 112500 ///< @brief Vitesse de communication UART en bauds.



#endif // _SETTING_HPP_
