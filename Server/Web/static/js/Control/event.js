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



let timeout;
const socket = io();

if (window.DEBUG)
    console.log("[Event] Initialisation - Demande des données des évènements.");

socket.emit("getEventAll", window.matchId);

const team          = document.querySelector("select[name='Équipe']");
const joueur        = document.querySelector("select[name='Joueur']");
const joueurFautif  = document.querySelector("select[name='Joueur fautif']");
const joueurVictime = document.querySelector("select[name='Joueur victime']");
const joueurSortant = document.querySelector("select[name='Joueur sortant']");
const joueurEntrant = document.querySelector("select[name='Joueur entrant']");
function selectValidOptions()
{
	for (const select of document.querySelectorAll("select[name='Joueur'], select[name='Joueur fautif'], select[name='Joueur victime'], select[name='Joueur sortant'], select[name='Joueur entrant']"))
	{
		for (const option of select.children)
			option.classList.add("hidden");
	}
	for (const option of joueur.children)
	{
		if (option.getAttribute("team") == team.selectedOptions[0].getAttribute("team") && option.getAttribute("name") != "" && option.getAttribute("name") != "None" && option.getAttribute("number") != "0" && option.getAttribute("number") != "None")
			option.classList.remove("hidden");
	}
	for (const option of joueurFautif.children)
	{
		if (option.getAttribute("team") == team.selectedOptions[0].getAttribute("team") && option.getAttribute("name") != "" && option.getAttribute("name") != "None" && option.getAttribute("number") != "0" && option.getAttribute("number") != "None")
			option.classList.remove("hidden");
	}
	for (const option of joueurSortant.children)
	{
		if (option.getAttribute("team") == team.selectedOptions[0].getAttribute("team") && option.getAttribute("name") != "" && option.getAttribute("name") != "None" && option.getAttribute("number") != "0" && option.getAttribute("number") != "None")
			option.classList.remove("hidden");
	}
	for (const option of joueurEntrant.children)
	{
		if (option.getAttribute("team") == team.selectedOptions[0].getAttribute("team") && option.getAttribute("name") != "" && option.getAttribute("name") != "None" && option.getAttribute("number") != "0" && option.getAttribute("number") != "None")
			option.classList.remove("hidden");
	}
	for (const option of joueurVictime.children)
	{
		if (option.getAttribute("team") != team.selectedOptions[0].getAttribute("team") && option.getAttribute("name") != "" && option.getAttribute("name") != "None" && option.getAttribute("number") != "0" && option.getAttribute("number") != "None")
			option.classList.remove("hidden");
	}

	return ;
}
team.addEventListener("change", () => selectValidOptions());
selectValidOptions();

// Envoi des données d'évènement
document.addEventListener("DOMContentLoaded", () =>
{
    const inputs = document.querySelectorAll("#event-selected input, #even-selected select");

    inputs.forEach(input =>
    {
        input.addEventListener("input", autoSend);
        input.addEventListener("change", autoSend);
    });
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
		info.setAttribute("ts", event.ts);
		info.setAttribute("minute_number", event.minute_number);
		info.setAttribute("match_minute", event.match_minute);
		info.setAttribute("team", event.team);
		info.setAttribute("player", event.player);
		info.setAttribute("offending_player", event.offending_player);
		info.setAttribute("victim_player", event.victim_player);
		info.setAttribute("out_player", event.out_player);
		info.setAttribute("in_player", event.in_player);
		info.setAttribute("detail", event.detail);
		info.setAttribute("match", event.match);

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

	socket.on("newEventResponse", (data) =>
	{
		if (window.DEBUG)
			console.log(`[Event] Récupération de l'identifiant de l'évènement : ${data.id}`);

		const info = newEventElement.querySelector("span");
		info.setAttribute("id", data.id);
		info.setAttribute("ts", data.ts);
	});

	socket.emit("newEvent", code, window.matchId)

	return ;
}

window.newEvent = newEvent;



/**
 * @brief Récupération des informations d'évènement.
 */
function getEventInformation()
{
    const idEvent = document.querySelector("#event-selected p")?.textContent;

    if (!idEvent)
    {
        console.log("Aucun événement sélectionné");
        return null;
    }

    const span = document.querySelector(`#event-list span[id='${idEvent}']`);

    if (!span)
    {
        console.log(`Événement introuvable dans #event-list pour id=${idEvent}`);
        return null;
    }

    return {
    	id: idEvent,
        ts: span.getAttribute("ts"),
        minute_number: span.getAttribute("minute_number"),
        match_minute: span.getAttribute("match_minute"),
        team: span.getAttribute("team"),
        player: span.getAttribute("player"),
        offending_player: span.getAttribute("offending_player"),
        victim_player: span.getAttribute("victim_player"),
        out_player: span.getAttribute("out_player"),
        in_player: span.getAttribute("in_player"),
        detail: span.getAttribute("detail"),
        match: span.getAttribute("match")
    };
}



/**
 * @brief Envoi automatique des données.
 */
function autoSend()
{
    clearTimeout(timeout);

    timeout = setTimeout(() => 
    {
    	const info = getEventInformation();
    	if (!info)
    	{
        	const data = JSON.stringify(info, null, 4);

        	socket.emit("modifyEvent", info.id, data);

        	if (window.DEBUG)
            	console.log("Infomation d'évènement envoyé :", data);
        }
    }, 500);

    return ;
}
