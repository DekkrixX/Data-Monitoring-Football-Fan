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

import { supporterCard, stadiumBleacherCard, comparisonCard } from "./Utils/board.js";

// ============================================================================
//  Initialisation
// ============================================================================

const socket = io();

if (DEBUG)
    console.log("[Index] Initialisation - Demande de la liste des supporters connectés");

// Demande de la liste des supporters actuellement connectés
socket.emit("getSupporter");
// Demande de la liste des tribunes actuellement connectés
socket.emit("getStadiumBleacher")

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

        const grid = document.getElementById("gridSupporter");

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

            const comparison = comparisonCard("Supporter");
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

        const grid    = document.getElementById("gridSupporter");
        const element = supporterCard(data.id, data.name, data.color);

        const comparisonEl = grid.querySelector("#comparisonSupporter");

        if (comparisonEl !== null)
        {
            // Insère la nouvelle carte avant la carte de comparaison existante
            grid.insertBefore(element, comparisonEl);
        }
        else
        {
            grid.appendChild(element);

            // Compte les cartes de supporter présentes (exclut #comparisonSupporter)
            const supporterCount = grid.querySelectorAll(".card:not(#comparisonSupporter)").length;

            // Crée la carte de comparaison dès que deux supporters sont affichés
            if (supporterCount >= 2)
            {
                if (DEBUG)
                    console.log("[Index] supporterConnection - Ajout de la carte de comparaison");

                const comparison = comparisonCard("Supporter");
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

        const grid        = document.getElementById("gridSupporter");
        const cardToRemove = grid.querySelector("#s" + id);

        if (cardToRemove)
            cardToRemove.remove();

        // Retire la carte de comparaison si moins de 2 supporters restent
        const supporterCount = grid.querySelectorAll(".card:not(#comparisonSupporter)").length;

        if (supporterCount < 2)
        {
            const comparisonEl = grid.querySelector("#comparisonSupporter");
            if (comparisonEl)
            {
                if (DEBUG)
                    console.log("[Index] supporterDisconnection - Suppression de la carte de comparaison (moins de 2 supporters)");

                comparisonEl.remove();
            }
        }
    });

/**
 * @brief Réception de la liste initiale des tribunes connectés.
 *
 * @param {Array<{id: number, name: string}>} dataList Liste des tribunes actuellement connectés.
 */
socket.on("getStadiumBleacherResponse", (dataList) =>
    {
        if (DEBUG)
            console.log(`[Index] getStadiumBleacherResponse - Réception de ${dataList.length} tribune(s)`);

        const grid = document.getElementById("gridStadiumBleacher");

        for (const data of dataList)
        {
            if (DEBUG)
                console.log(`[Index] getStadiumBleacherResponse - Ajout de la tribune id=${data.id} (${data.name})`);

            const element = stadiumBleacherCard(data.id, data.name, data.color);
            grid.appendChild(element);
        }

        // La carte de comparaison n'est pertinente qu'à partir de 2 tribunes
        if (dataList.length >= 2)
        {
            if (DEBUG)
                console.log("[Index] getStadiumBleacherResponse - Ajout de la carte de comparaison");

            const comparison = comparisonCard("StadiumBleacher");
            grid.appendChild(comparison);
        }
    });

/**
 * @brief Connexion d'une nouvelle tribune en temps réel.
 *
 * @param {{id: number, name: string, color: string}} data Données de la tribune qui vient de se connecter.
 */
socket.on("stadiumBleacherConnection", (data) =>
    {
        if (DEBUG)
            console.log(`[Index] stadiumBleacherConnection - Nouvelle tribune id=${data.id} (${data.name})`);

        const grid    = document.getElementById("gridStadiumBleacher");
        const element = stadiumBleacherCard(data.id, data.name, data.color);

        const comparisonEl = grid.querySelector("#comparisonStadiumBleacher");

        if (comparisonEl !== null)
        {
            // Insère la nouvelle carte avant la carte de comparaison existante
            grid.insertBefore(element, comparisonEl);
        }
        else
        {
            grid.appendChild(element);

            // Compte les cartes de tribunes présentes (exclut #comparisonStadiumBleacher)
            const stadiumBleacherCount = grid.querySelectorAll(".card:not(#comparisonSupporter)").length;

            // Crée la carte de comparaison dès que deux tribunes sont affichés
            if (stadiumBleacherCount >= 2)
            {
                if (DEBUG)
                    console.log("[Index] stadiumBleacherConnection - Ajout de la carte de comparaison");

                const comparison = comparisonCard("StadiumBleacher");
                grid.appendChild(comparison);
            }
        }
    });

/**
 * @brief Déconnexion d'une tribune en temps réel.
 *
 * @param {number} id Identifiant de la tribune déconnecté.
 */
socket.on("stadiumBleacherDisconnection", (id) =>
    {
        if (DEBUG)
            console.log(`[Index] stadiumBleacherDisconnection - Déconnexion de la tribune id=${id}`);

        const grid        = document.getElementById("gridStadiumBleacher");
        const cardToRemove = grid.querySelector("#b" + id);

        if (cardToRemove)
            cardToRemove.remove();

        // Retire la carte de comparaison si moins de 2 tribunes restent
        const stadiumBleacherCount = grid.querySelectorAll(".card:not(#comparisonStadiumBleacher)").length;

        if (stadiumBleacherCount < 2)
        {
            const comparisonEl = grid.querySelector("#comparisonStadiumBleacher");
            if (comparisonEl)
            {
                if (DEBUG)
                    console.log("[Index] stadiumBleacherDisconnection - Suppression de la carte de comparaison (moins de 2 tribunes)");

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
