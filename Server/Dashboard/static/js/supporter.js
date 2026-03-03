/**
 * @file supporter.js
 *
 * @brief Logique de la page de détail d'un supporter.
 *
 * Demande les données initiales du supporter identifié par window.id, met à jour l'affichage et le graphique à chaque nouvelle notification reçue via SocketIO.
 */

// ============================================================================
//  Import des bibliothèques
// ============================================================================

import { createChart } from "./Utils/board.js";
import { subtractSeconds } from "./Utils/time.js";

// ============================================================================
//  Initialisation
// ============================================================================

const socket = io();

if (window.DEBUG)
    console.log(`[Supporter] Initialisation - Demande des données du supporter id=${window.id}`);

// Création du graphique de fréquence cardiaque
const canva = document.getElementById("chart");
const ctx   = canva.getContext("2d");
const chart = createChart(ctx, [{ title: window.name, color: window.color }]);

// Demande des données initiales du supporter
// window.id est utilisé explicitement pour éviter toute ambiguïté avec une
// variable locale non définie
socket.emit("getSupporterData", window.id);

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception des données initiales du supporter.
 *
 * @param {{id: number, heartRate: number, average: number, minimum: number, maximum: number}} data Données du supporter.
 */
socket.on("getSupporterDataResponse", (data) =>
    {
        if (data.id !== window.id)
            return;

        if (window.DEBUG)
            console.log(`[Supporter] getSupporterDataResponse - Réception des données initiales (HR=${data.heartRate} bpm)`);

        _displayData(data.heartRate, data.average, data.minimum, data.maximum);
        _fillGraphic(chart, data.heartRate);
    });

/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{id: number, heartRate: number, average: number, minimum: number, maximum: number}} data Nouvelles données du supporter.
 */
socket.on("newSupporterData", (data) =>
    {
        if (data.id !== window.id)
            return;

        if (window.DEBUG)
            console.log(`[Supporter] newSupporterData - Nouvelle mesure reçue (HR=${data.heartRate} bpm)`);

        _displayData(data.heartRate, data.average, data.minimum, data.maximum);
        _fillGraphic(chart, data.heartRate);
    });

/**
 * @brief Déconnexion du supporter actuellement affiché.
 *
 * @param {number} supporterId Identifiant du supporter déconnecté.
 */
socket.on("supporterDisconnection", (supporterId) =>
    {
        if (supporterId !== window.id)
            return;

        if (window.DEBUG)
            console.log(`[Supporter] supporterDisconnection - Supporter id=${window.id} déconnecté`);

        _showDisconnectMessage();
    });

/**
 * @brief Fermeture du serveur.
 */
socket.on("serverClose", () =>
    {
        if (window.DEBUG)
            console.log("[Supporter] serverClose - Fermeture du serveur, redirection vers l'accueil");

        window.location.href = "/";
    });

// ============================================================================
//  Fonctions internes
// ============================================================================

/**
 * @brief Affiche un overlay de déconnexion pendant 5 secondes.
 */
function _showDisconnectMessage()
{
    if (window.DEBUG)
        console.log("[Supporter] _showDisconnectMessage - Affichage de l'overlay de déconnexion");

    // Overlay plein écran semi-transparent
    const overlay = document.createElement("div");
    overlay.style.position        = "fixed";
    overlay.style.top             = "0";
    overlay.style.left            = "0";
    overlay.style.width           = "100vw";
    overlay.style.height          = "100vh";
    overlay.style.backgroundColor = "rgba(0, 0, 0, 0.6)";
    overlay.style.display         = "flex";
    overlay.style.alignItems      = "center";
    overlay.style.justifyContent  = "center";
    overlay.style.zIndex          = "9999";

    // Message centré
    const message = document.createElement("div");
    message.textContent            = "Supporter déconnecté";
    message.style.backgroundColor = "#fff";
    message.style.padding          = "30px 50px";
    message.style.borderRadius     = "8px";
    message.style.fontSize         = "24px";
    message.style.fontWeight       = "bold";
    message.style.color            = "red";
    message.style.boxShadow        = "0 10px 30px rgba(0,0,0,0.3)";

    overlay.appendChild(message);
    document.body.appendChild(overlay);

    // Suppression automatique après 5 secondes
    setTimeout(() =>
        {
            if (window.DEBUG)
                console.log("[Supporter] _showDisconnectMessage - Suppression de l'overlay");

            overlay.remove();
        }, 5000);
}

/**
 * @brief Met à jour les éléments DOM affichant les statistiques du supporter.
 *
 * @param {number} heartRate Dernière fréquence cardiaque en bpm.
 * @param {number} average   Moyenne des fréquences cardiaques en bpm.
 * @param {number} minimum   Minimum enregistré en bpm.
 * @param {number} maximum   Maximum enregistré en bpm.
 */
function _displayData(heartRate, average, minimum, maximum)
{
    if (window.DEBUG)
        console.log(`[Supporter] _displayData - HR=${heartRate} bpm, avg=${average}, min=${minimum}, max=${maximum}`);

    document.getElementById("heart-rate").textContent = heartRate[heartRate.length - 1];
    document.getElementById("average").textContent    = average;
    document.getElementById("minimum").textContent    = minimum;
    document.getElementById("maximum").textContent    = maximum;
}

/**
 * @brief Ajoute un nouveau point de fréquence cardiaque sur le graphique.
 *
 * @param {Chart}  chart     Instance Chart.js cible.
 * @param {number} heartRate Valeur de fréquence cardiaque en bpm.
 */
function _fillGraphic(chart, heartRate)
{
    const now = new Date();

    for (let i=heartRate.length - 1; i >= 0; i--)
    {
        if (heartRate[i] != 0)
        { 
            // Heure de la mesure formatée HH:MM:SS comme label de l'axe X
            const time = new Date(subtractSeconds(now, i));
            const timestamp = time.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

            if (window.DEBUG)
                console.log(`[Supporter] _fillGraphic - Ajout du point HR=${heartRate[i]} bpm à t=${timestamp}`);

            chart.data.labels.push(timestamp);
            chart.data.datasets[0].data.push(heartRate[i]);

            // Limite l'historique affiché à 100 points
            if (chart.data.labels.length > 100)
            {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
        }
    }

    // Mise à jour sans animation pour un rendu temps réel fluide
    chart.update("none");
}
