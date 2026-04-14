/**
 * @file time.js
 *
 * @brief Utilitaires de manipulation du temps.
 *
 * Fournit des fonctions de calcul sur les objets Date JavaScript, utilisées pour la gestion des horodatages dans le dashboard.
 */

// ============================================================================
//  Fonctions
// ============================================================================

/**
 * @brief Soustrait un nombre de secondes à un objet Date et retourne le résultat en millisecondes depuis l'epoch Unix.
 *
 * @param {Date}   time    Objet Date de référence.
 * @param {number} seconds Nombre de secondes à soustraire. Doit être positif.
 *
 * @returns {number} Timestamp en millisecondes correspondant à @p time moins @p seconds secondes.
 */
export function subtractSeconds(time, seconds)
{
  // Convertir l’entrée en nombre de millisecondes
  const timeMs = time.getTime();

  // Soustraire le nombre de secondes
  const result = timeMs - seconds * 1000;

  return result;
}