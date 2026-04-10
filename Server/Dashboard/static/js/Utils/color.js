/**
 * @file color.js
 *
 * @brief Utilitaires de manipulation des couleurs.
 *
 * Fournit des fonctions de calcul sur les couleurs, utilisées pour la gestion des courbe dans le dashboard.
 */

// ============================================================================
//  Fonctions
// ============================================================================

/**
 * @brief Modifie la couleur original pour donné une autre couleur similaire.
 *
 * @param {string} color  Couleur original en hexadécimal.
 * @param {number} offset Modifcation à appliquer.
 *
 * @returns {string} Code hexadécimal de la nouvelle couleur.
 */
export function adjustColor(color, offset) {
    let colorNumber = parseInt(color.slice(1), 16);

    let red   = (colorNumber >> 16) + offset;
    let green = ((colorNumber >> 8) & 0x00FF) + offset;
    let blue  = (colorNumber & 0x0000FF) + offset;

    red   = Math.max(0, Math.min(255, red));
    green = Math.max(0, Math.min(255, green));
    blue  = Math.max(0, Math.min(255, blue));

    return "#" + (red << 16 | green << 8 | blue).toString(16).padStart(6, "0").toUpperCase();
}
