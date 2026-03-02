/**
 * @file initSensor.hpp
 * 
 * @brief Initialise le capteur actif à la compilation.
 *
 * En fonction des macros définies dans setting.hpp, ce fichier définit la macro SENSOR avec le nom de la classe concrète correspondante. Si aucune macro de capteur n'est définie ou plusieurs macros de capteur sont définies, la compilation est interrompue avec une erreur explicite.
 *
 * Utilisation dans main.cpp:
 * @code
 * sensor = new SENSOR(SUPPORTER_ID);
 * @endcode
 */

#ifndef _INITSENSOR_HPP_
#define _INITSENSOR_HPP_

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./setting.hpp"

// ============================================================================
//  Initialisation dynamic du capteur
// ============================================================================

#ifdef POLARH10
#define SENSOR PolarH10 ///< @brief Alias vers la classe concrète PolarH10, résolu à la compilation.
#endif // POLARH10

// ============================================================================
//  Vérification de l'initialisation d'un capteur
// ============================================================================

#ifndef SENSOR
#error "Erreur de configuration: Aucun capteur n'est initialisé"
#endif // SENSOR

#if POLARH10 != 1
#error "Erreur de configuration: Plusieurs capteurs sont définis"
#endif

// ============================================================================
//  Vérification de l'initialisation d'un capteur
// ============================================================================

#ifndef SUPPORTER_ID
#error "Erreur de configuration: Aucun identifiant de supporter"
#endif



#endif // _INITSENSOR_HPP_
