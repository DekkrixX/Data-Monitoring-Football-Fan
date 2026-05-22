/**
 * @file index.js
 *
 * @brief Logique de la page d'accueil du dashboard de tracking.
 *
 * Demande la liste des tracker connectés au serveur, affiche une carte par tracker et gère dynamiquement les connexions et déconnexions en temps réel via SocketIO.
 */

// ============================================================================
//  Import des bibliothèques
// ============================================================================

import { trackerCard } from "../Utils/element.js";

// ============================================================================
//  Initialisation
// ============================================================================

const socket = io();

if (window.DEBUG)
    console.log("[Index] Initialisation - Demande de la liste des trackers connectés");

// Demande de la liste des trackers actuellement connectés
socket.emit("getTracker");

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception de la liste initiale des trackers connectés.
 *
 * @param {Array<{id: number, name: string}>} dataList Liste des trackers actuellement connectés.
 */
socket.on("getTrackerResponse", (dataList) =>
{
    if (window.DEBUG)
        console.log(`[Index] getTrackerResponse - Réception de ${dataList.length} tracker(s)`);

    const grid = document.getElementById("grid");

    for (const data of dataList)
    {
        if (window.DEBUG)
            console.log(`[Index] getTrackerResponse - Ajout du tracker id=${data.id} (${data.name})`);

        const element = trackerCard(data.id, data.name, data.color);
        grid.appendChild(element);
    }
});



/**
 * @brief Connexion d'un nouveau tracker en temps réel.
 *
 * @param {{id: number, name: string, color: string}} data Données du tracker qui vient de se connecter.
 */
socket.on("trackerConnection", (data) =>
{
    if (window.DEBUG)
        console.log(`[Index] trackerConnection - Nouveau tracker id=${data.id} (${data.name})`);

    const grid    = document.getElementById("grid");
    const element = trackerCard(data.id, data.name, data.color);

    grid.appendChild(element);
});



/**
 * @brief Déconnexion d'un tracker en temps réel.
 *
 * @param {number} id Identifiant du tracker déconnecté.
 */
socket.on("trackerDisconnection", (id) =>
{
    if (window.DEBUG)
        console.log(`[Index] trackerDisconnection - Déconnexion du tracker id=${id}`);

    const grid        = document.getElementById("grid");
    const cardToRemove = grid.querySelector("#t" + id);

    if (cardToRemove)
        cardToRemove.remove();
});



/**
 * @brief Fermeture du serveur.
 */
socket.on("serverClose", () =>
{
    if (window.DEBUG)
        console.log("[Index] serverClose - Fermeture du serveur, rechargement de la page");

    window.location.href = "/tracking";
});
