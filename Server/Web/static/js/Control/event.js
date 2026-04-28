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



const socket = io();

if (window.DEBUG)
    console.log("[Event] Initialisation - Demande des données des évènements.");

socket.emit("getEventAll");

const team          = document.querySelector("select[name='Équipe']");
const joueur        = document.querySelector("select[name='Joueur']");
const joueurFautif  = document.querySelector("select[name='Joueur fautif']");
const joueurVictime = document.querySelector("select[name='Joueur victime']");
const joueurSortant = document.querySelector("select[name='Joueur sortant']");
const joueurEntrant = document.querySelector("select[name='Joueur entrant']");
team.addEventListener("change", () =>
{
	for (const select of document.querySelectorAll("select[name='Joueur'], select[name='Joueur fautif'], select[name='Joueur victime'], select[name='Joueur sortant'], select[name='Joueur entrant']"))
	{
		for (const option of select.children)
			option.classList.add("hidden");
	}
	for (const option of joueur.children)
	{
		if (option.getAttribute("team") == team.selectedOptions[0].getAttribute("team"))
			option.classList.remove("hidden");
	}
	for (const option of joueurFautif.children)
	{
		if (option.getAttribute("team") == team.selectedOptions[0].getAttribute("team"))
			option.classList.remove("hidden");
	}
	for (const option of joueurSortant.children)
	{
		if (option.getAttribute("team") == team.selectedOptions[0].getAttribute("team"))
			option.classList.remove("hidden");
	}
	for (const option of joueurEntrant.children)
	{
		if (option.getAttribute("team") == team.selectedOptions[0].getAttribute("team"))
			option.classList.remove("hidden");
	}
	for (const option of joueurVictime.children)
	{
		if (option.getAttribute("team") != team.selectedOptions[0].getAttribute("team"))
			option.classList.remove("hidden");
	}
});

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception des données initiales des évènement.
 *
 * @param [{}] data Données des évènements.
 */
socket.on("getEventAllResponse", (data) =>
{
	if (window.DEBUG)
        console.log("[Event] getEventAllResponse - Réception des données initiales.");

	for (const event of data)
	{
		const name = getNameOfEvent(event.code);

		if (window.DEBUG)
			console.log(`[Event] getEventAllResponse - Création de l'évènement '${name}' pour l'identifiant '${event.id}'`);

		const eventElement = createEvent(name, event.code, socket);
		const info = eventElement.querySelector("span");

		info.setAttribute("id", event.id);
		info.setAttribute("team", event.team);
		info.setAttribute("minute", event.minute);

		const eventList = document.getElementById("event-list");
		eventList.appendChild(eventElement);
	}
});



/**
 * @brief Récupère le nom de l'évènement.
 * 
 * @param code Code de l'évènement.
 * 
 * @return string Le nom de l'évènement.
 */
function getNameOfEvent(code)
{
	const config = JSON.parse(window.config)
	for (const category of config.config)
	{
        const event = category.event.find(e => e.code === code);
        if (event)
        	return event.name;
    }

	return "";
}



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
	const newEventElement = createEvent(name, code, socket);
	eventList.appendChild(newEventElement);

	socket.emit("newEvent", code)

	socket.on("newEventResponse", (id) =>
	{
		if (window.DEBUG)
			console.log(`[Event] Récupération de l'identifiant de l'évènement : ${id}`);

		const info = newEventElement.querySelector("span");
		info.setAttribute("id", id);
	});

	return ;
}

window.newEvent = newEvent;
