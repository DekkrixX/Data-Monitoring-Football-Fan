/**
 * @file index.js
 *
 * @brief Logique de la page d'accueil du dashboard.
 *
 * Demande la liste des supporters connectés au serveur, affiche une carte par supporter et gère dynamiquement les connexions et déconnexions en temps réel via SocketIO.
 */

// ============================================================================
//  Import des bibliothèques
// ============================================================================

import { supporterCard, comparisonCard } from "./Utils/board.js";

// ============================================================================
//  Initialisation
// ============================================================================

const socket = io();

if (DEBUG)
    console.log("[Index] Initialisation - Demande de la liste des supporters connectés");

// Demande de la liste des supporters actuellement connectés
socket.emit("getSupporter");

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception de la liste initiale des supporters connectés.
 *
 * @param {Array<{id: number, name: string}>} dataList Liste des supporters actuellement connectés.
 */
socket.on("getSupporterResponse", (dataList) =>
    {
        if (DEBUG)
            console.log(`[Index] getSupporterResponse - Réception de ${dataList.length} supporter(s)`);

        const grid = document.getElementById("grid");

        for (const data of dataList)
        {
            if (DEBUG)
                console.log(`[Index] getSupporterResponse - Ajout du supporter id=${data.id} (${data.name})`);

            const element = supporterCard(data.id, data.name, data.color);
            grid.appendChild(element);
        }

        // La carte de comparaison n'est pertinente qu'à partir de 2 supporters
        if (dataList.length >= 2)
        {
            if (DEBUG)
                console.log("[Index] getSupporterResponse - Ajout de la carte de comparaison");

            const comparison = comparisonCard();
            grid.appendChild(comparison);
        }
    });

/**
 * @brief Connexion d'un nouveau supporter en temps réel.
 *
 * @param {{id: number, name: string, color: string}} data Données du supporter qui vient de se connecter.
 */
socket.on("supporterConnection", (data) =>
    {
        if (DEBUG)
            console.log(`[Index] supporterConnection - Nouveau supporter id=${data.id} (${data.name})`);

        const grid    = document.getElementById("grid");
        const element = supporterCard(data.id, data.name, data.color);

        const comparisonEl = grid.querySelector("#comparison");

        if (comparisonEl !== null)
        {
            // Insère la nouvelle carte avant la carte de comparaison existante
            grid.insertBefore(element, comparisonEl);
        }
        else
        {
            grid.appendChild(element);

            // Compte les cartes de supporter présentes (exclut #comparison)
            const supporterCount = grid.querySelectorAll(".card:not(#comparison)").length;

            // Crée la carte de comparaison dès que deux supporters sont affichés
            if (supporterCount >= 2)
            {
                if (DEBUG)
                    console.log("[Index] supporterConnection - Ajout de la carte de comparaison");

                const comparison = comparisonCard();
                grid.appendChild(comparison);
            }
        }
    });

/**
 * @brief Déconnexion d'un supporter en temps réel.
 *
 * @param {number} id Identifiant du supporter déconnecté.
 */
socket.on("supporterDisconnection", (id) =>
    {
        if (DEBUG)
            console.log(`[Index] supporterDisconnection - Déconnexion du supporter id=${id}`);

        const grid        = document.getElementById("grid");
        const cardToRemove = grid.querySelector("#s" + id);

        if (cardToRemove)
            cardToRemove.remove();

        // Retire la carte de comparaison si moins de 2 supporters restent
        const supporterCount = grid.querySelectorAll(".card:not(#comparison)").length;

        if (supporterCount < 2)
        {
            const comparisonEl = grid.querySelector("#comparison");
            if (comparisonEl)
            {
                if (DEBUG)
                    console.log("[Index] supporterDisconnection - Suppression de la carte de comparaison (moins de 2 supporters)");

                comparisonEl.remove();
            }
        }
    });

/**
 * @brief Fermeture du serveur.
 */
socket.on("serverClose", () =>
    {
        if (DEBUG)
            console.log("[Index] serverClose - Fermeture du serveur, rechargement de la page");

        window.location.href = "/";
    });
