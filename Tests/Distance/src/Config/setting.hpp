/**
 * @file setting.hpp
 * 
 * @brief Configuration globale du firmware.
 *
 * Centralise tous les paramètres modifiables du test de distance.
 */

#ifndef _SETTING_HPP_
#define _SETTING_HPP_

// ============================================================================
//  Paramètre de paquet
// ============================================================================

#define ID         1 ///< @brief Id associé au message.
#define NAME  "test" ///< @brief Nom associé au message.
#define TOPIC_TEST 0 ///< @brief Indice du topic MQTT de test.

#define TIME_INTERVAL 10 * 1000 ///< @brief Temps d'interval entre les envoi de paquets.

// ============================================================================
//  Paramètres de debug
// ============================================================================

#define DEBUG               0 ///< @brief Activation des messages de debug sur le port série (Serial).
#define BAUDRATE_DEBUG 115200 ///< @brief Vitesse de communication UART en bauds.

// ============================================================================
//  Paramètres UART
// ============================================================================

#define RX_PIN       44 ///< @brief Broche RX de l'UART externe (Serial1).
#define TX_PIN       43 ///< @brief Broche TX de l'UART externe (Serial1).
#define BAUDRATE 115200 ///< @brief Vitesse de communication UART en bauds.

// ============================================================================
//  Paramètres LED
// ============================================================================

#define LED_PIN 21 ///< @brief Broche GPIO de la LED de la carte ESP32.

// ============================================================================
//  Paramètres de logs
// ============================================================================

#define NB_LOGGER                 3 ///< @brief Nombre de logger présent sur la carte.
#define LOGGER_MAX_MESSAGE_SIZE 256 ///< @brief Taille maximale d'un message de log en caractères.

#if NB_LOGGER <= 0
#error "Erreur de configuration: Le nombre de logger est invalide"
#else
#define LOGGER_MAX_FILE_SIZE (((1024 * 1024) * 6) / NB_LOGGER) ///< @brief Taille maximale d'un fichier de log en octets.
#endif



#endif // _SETTING_HPP_
