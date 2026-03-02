/**
 * @file comparison.js
 *
 * @brief Logique de la page de comparaison des supporters.
 *
 * Demande les données de tous les supporters connectés et les affiche sur un graphique multi-courbes, une courbe par supporter. Gère dynamiquement les connexions et déconnexions en temps réel via SocketIO.
 */

// ============================================================================
//  Import des bibliothèques
// ============================================================================

import { createChart } from "./Utils/board.js";

// ============================================================================
//  Initialisation
// ============================================================================

const socket = io();

if (window.DEBUG)
    console.log("[Comparison] Initialisation - Demande des données de tous les supporters");

// Création du graphique multi-courbes (vide au départ, alimenté par les événements)
const canva = document.getElementById("chart");
const ctx   = canva.getContext("2d");
const chart = createChart(ctx, []);

// Demande des données initiales de tous les supporters connectés
socket.emit("getSupporterDataAll");

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception des données initiales de tous les supporters connectés.
 *
 * @param {Array<{id: number, name: string, color: string, heartRate: number}>} dataList Liste des données de chaque supporter connecté.
 */
socket.on("getSupporterDataAllResponse", (dataList) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] getSupporterDataAllResponse - Réception des données de ${dataList.length} supporter(s)`);

        for (const data of dataList)
        {
            if (window.DEBUG)
                console.log(`[Comparison] getSupporterDataAllResponse - Ajout du supporter '${data.name}' (HR=${data.heartRate} bpm)`);

            _addSupporterToGraphic(chart, data.name, data.color);
            _fillGraphic(chart, data.name, data.heartRate);
        }
    });

/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{name: string, heartRate: number}} data
 *        Nouvelles données du supporter.
 */
socket.on("newSupporterData", (data) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] newSupporterData - Nouvelle mesure pour '${data.name}' (HR=${data.heartRate} bpm)`);

        _fillGraphic(chart, data.name, data.heartRate);
    });

/**
 * @brief Connexion d'un nouveau supporter en temps réel.
 *
 * @param {{name: string, color: string}} data
 *        Données du supporter qui vient de se connecter.
 */
socket.on("supporterConnection", (data) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] supporterConnection - Nouveau supporter '${data.name}', ajout de la courbe`);

        _addSupporterToGraphic(chart, data.name, data.color);
    });

/**
 * @brief Déconnexion d'un supporter en temps réel.
 *
 * @param {string} supporterName Nom du supporter déconnecté.
 */
socket.on("supporterDisconnection", (supporterName) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] supporterDisconnection - Suppression de la courbe du supporter '${supporterName}'`);

        _removeSupporterFromGraphic(chart, supporterName);
    });

/**
 * @brief Fermeture du serveur.
 */
socket.on("serverClose", () =>
    {
        if (window.DEBUG)
            console.log("[Comparison] serverClose - Fermeture du serveur, redirection vers l'accueil");

        window.location.href = "/";
    });

// ============================================================================
//  Fonctions internes
// ============================================================================

/**
 * @brief Ajoute un nouveau point de fréquence cardiaque sur la courbe d'un
 *        supporter.
 *
 * @param {Chart}  chart     Instance Chart.js cible.
 * @param {string} name      Nom du supporter (label de la courbe).
 * @param {number} heartRate Valeur de fréquence cardiaque en bpm.
 */
function _fillGraphic(chart, name, heartRate)
{
    const index = chart.data.datasets.findIndex(d => d.label === name);

    if (index === -1)
    {
        if (window.DEBUG)
            console.log(`[Comparison] _fillGraphic - Courbe '${name}' introuvable, point ignoré`);
        return;
    }

    // Heure courante formatée HH:MM:SS comme label de l'axe X
    const now       = new Date();
    const timestamp = now.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

    if (window.DEBUG)
        console.log(`[Comparison] _fillGraphic - Ajout du point HR=${heartRate} bpm pour '${name}' à t=${timestamp}`);

    chart.data.datasets[index].data.push({ x: timestamp, y: heartRate });

    // Limite l'historique affiché à 100 points
    if (chart.data.datasets[index].data.length > 100)
        chart.data.datasets[index].data.shift();

    // Mise à jour sans animation pour un rendu temps réel fluide
    chart.update("none");
}

/**
 * @brief Ajoute une nouvelle courbe vide pour un supporter sur le graphique.
 *
 * @param {Chart}  chart Instance Chart.js cible.
 * @param {string} name  Nom du supporter (utilisé comme label de la courbe).
 * @param {string} color Couleur CSS de la courbe (ex : "#FF0000").
 */
function _addSupporterToGraphic(chart, name, color)
{
    // Vérifie qu'une courbe portant ce nom n'existe pas déjà
    const alreadyExists = chart.data.datasets.some(d => d.label === name);

    if (alreadyExists)
    {
        if (window.DEBUG)
            console.log(`[Comparison] _addSupporterToGraphic - Courbe '${name}' déjà présente, ajout ignoré`);
        return;
    }

    if (window.DEBUG)
        console.log(`[Comparison] _addSupporterToGraphic - Ajout de la courbe '${name}' (color='${color}')`);

    chart.data.datasets.push({
        label:           name,
        data:            [],
        borderColor:     color,
        backgroundColor: color + "33", // Couleur de fond avec opacité 20%
        fill:            true,
        tension:         0.4,
        pointRadius:     4,
        borderWidth:     3
    });

    chart.update("none");
}

/**
 * @brief Retire la courbe d'un supporter du graphique.
 *
 * @param {Chart}  chart Instance Chart.js cible.
 * @param {string} name  Nom du supporter (label de la courbe à supprimer).
 */
function _removeSupporterFromGraphic(chart, name)
{
    const index = chart.data.datasets.findIndex(d => d.label === name);

    if (index === -1)
    {
        if (window.DEBUG)
            console.log(`[Comparison] _removeSupporterFromGraphic - Courbe '${name}' introuvable, suppression ignorée`);
        return;
    }

    if (window.DEBUG)
        console.log(`[Comparison] _removeSupporterFromGraphic - Suppression de la courbe '${name}'`);

    chart.data.datasets.splice(index, 1);
    chart.update("none");
}
