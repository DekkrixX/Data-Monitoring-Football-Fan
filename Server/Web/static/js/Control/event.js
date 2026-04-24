/**
 * @file configuration.js
 * 
 * @brief Logique de la page de configuration du contrôle d'évènement.
 * 
 * Ajoute un écouteur d'évènements sur le bouton de sauvegarde.
 */

// ============================================================================
//  Import des bibliothèques
// ============================================================================

import { createEvent } from "../Utils/element.js";



/**
 * @brief Ajoute un nouvel évènement à la liste des évènements.
 * 
 * @param name Nom de l'évènement.
 * @param code Code de l'évènement.
 */
function newEvent(name, code)
{
	if (window.DEBUG)
		console.log(`[Event] Nouvelle évènement : ${name}`);

	const eventList = document.getElementById("event-list");
	eventList.appendChild(createEvent(name, code));

	return ;
}

window.newEvent = newEvent;
