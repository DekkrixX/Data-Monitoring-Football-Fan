/**
 * @file Log.hpp
 *
 * @brief Interface d'export automatique des logs LittleFS sur le port série.
 *
 * Déclare la fonction dumpLogsOnBoot() à appeler dans setup() après Serial.begin() et LittleFS.begin(). Tous les fichiers .log présents dans /Logs/ sont envoyés via le port série en utilisant un protocole à marqueurs parsé par le script esp32_log_export.sh.
 *
 * Protocole de sortie :
 * @code{.txt}
 * <<<DUMP_START>>>
 * <<<FILE_START:/Logs/mqtt.log>>>
 * [00:00:01.042] [MQTT] [INFO] Connexion au broker
 * <<<FILE_END>>>
 * <<<DUMP_END>>>
 * @endcode
 */

#ifndef _LOG_HPP_
#define _LOG_HPP_

// ============================================================================
//  Import des bibliothèques
// ============================================================================

#include <Arduino.h>
#include <stdio.h>
#include <dirent.h>
#include <sys/stat.h>
#include <errno.h>

// ============================================================================
//  Déclaration
// ============================================================================

/**
 * @brief Parcourt /Logs/ et envoie tous les fichiers .log via le port série.
 */
void dumpLogsOnBoot();

#endif // _LOG_HPP_
