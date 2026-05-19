/**
 * @file system.js
 * 
 * @brief Logique de la page de de log des informations système.
 * 
 * Ajoute un écouteur de nouvelles informations.
 */

const socket = io();

/**
 * @brief Affiche un nouveau messsage d'informations système.
 */
socket.on("newSystemInfo", (message) =>
{
	if (window.DEBUG)
		console.log(`[System] Nouveau message : ${message}`);

	const log = document.getElementById("log");
	const p = document.createElement("p");
	p.textContent = message;
	log.appendChild(p);
});
