/**
 * @file stringConversion.js
 *
 * @brief Utilitaires des conversions de clé en chaîne de caractère lisible.
 *
 * Fournit des fonctions de conversion de chaîne de caractère, utilisé pour l'affichage à l'utilisateur.
 */

// ============================================================================
//  Fonctions
// ============================================================================

/**
 * @brief Transforme le type de données en chaîne lisible.
 *
 * @param {string} data Type de données.
 *
 * @returns {string} La chaîne lisible correspondant au type de données.
 */
export function dataToString(data)
{
    let string = "";

    switch (data)
    {
    case "heart_rate":
        string = "de la fréquence cardiaque";
        break;
    case "accelerometer":
        string = "de l'accélération";
        break;
    case "acoustic":
        string = "du niveau sonore";
        break;
    default:
        if (window.DEBUG)
            console.log(`[StringConvertion] dataToString - Type de données inconnu: ${data}`);
    }

    return string;
}

/**
 * @brief Transforme le type de support en chaîne lisible.
 *
 * @param {string} type Type de support.
 *
 * @returns {string} La chaîne lisible correspondant au type de support.
 */
export function typeToString(type)
{
    let string = "";

    switch (type)
    {
    case "Supporter":
        string = "supporters";
        break;
    case "StadiumBleacher":
        string = "tribunes";
        break;
    default:
        if (window.DEBUG)
            console.log(`[StringConvertion] typeToString - Type de support inconnu: ${data}`);
    }

    return string;
}
