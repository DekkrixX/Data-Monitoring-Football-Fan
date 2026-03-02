/**
 * @file state.hpp
 * 
 * @brief Définition des états de connexion utilisés par les capteurs.
 *
 * Ce fichier déclare l'énumération ConnectionState qui modélise le cycle de vie de la connexion d'un capteur.
 */

#ifndef _STATE_HPP_
#define _STATE_HPP_

// ============================================================================
//  État de connection
// ============================================================================

/**
 * @enum ConnectionState
 * 
 * @brief États possibles de la connexion d'un capteur.
 */
enum class ConnectionState
{
    DISCONNECTED,   ///< Aucune connexion active.
    CONNECTING,     ///< Tentative de connexion en cours.
    CONNECTED,      ///< Connexion établie et opérationnelle.
    RECONNECTING,   ///< Reconnexion en cours après une perte de liaison.
    ERROR           ///< Erreur irrémédiable sur la connexion.
};

#endif // _STATE_HPP_
