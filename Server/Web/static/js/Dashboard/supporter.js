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

import { createChart } from "../Utils/board.js";
import { subtractSeconds } from "../Utils/time.js";

// ============================================================================
//  Initialisation
// ============================================================================

const socket = io();

if (window.DEBUG)
    console.log(`[Supporter] Initialisation - Demande des données du supporter id=${window.id}`);

// Création du graphique de fréquence cardiaque
const canvaHeartRate = document.getElementById("chart_heart-rate");
const ctxHeartRate   = canvaHeartRate.getContext("2d");
const chartHeartRate = createChart(ctxHeartRate, [{ title: window.name, color: window.color }], "BPM", 40, 200, 10);

// Demande des données initiales du supporter
// window.id est utilisé explicitement pour éviter toute ambiguïté avec une
// variable locale non définie
socket.emit("getSupporterHeartRate", window.id);

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception des données initiales du supporter.
 *
 * @param {{id: number, heartRate: number, average: number, minimum: number, maximum: number}} data Données du supporter.
 */
socket.on("getSupporterHeartRateResponse", (data) =>
    {
        if (data.id !== window.id)
            return;

        if (window.DEBUG)
            console.log(`[Supporter] getSupporterHeartRateResponse - Réception des données initiales (HR=${data.heartRate} bpm)`);

        if (data.heartRate != "")
        {
            _displayData(data.heartRate, data.average, data.minimum, data.maximum, "heart-rate");
            _fillGraphicData(chartHeartRate, data.heartRate, "heart-rate");
        }
        else
            _displayData(["-"], "-", "-", "-", "heart-rate");
    });

/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{id: number, heartRate: number, average: number, minimum: number, maximum: number}} data Nouvelles données du supporter.
 */
socket.on("newSupporterHeartRate", (data) =>
    {
        if (data.id !== window.id)
            return;

        if (window.DEBUG)
            console.log(`[Supporter] newSupporterHeartRate - Nouvelle mesure reçue (HR=${data.heartRate} bpm)`);

        _displayData(data.heartRate, data.average, data.minimum, data.maximum, "heart-rate");
        _fillGraphicData(chartHeartRate, data.heartRate, "heart-rate");
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
 * @param {number} data    Dernière donnée enregistré.
 * @param {number} average Moyenne enregistré.
 * @param {number} minimum Minimum enregistré.
 * @param {number} maximum Maximum enregistré.
 * @param {string} type    Type de données.
 */
function _displayData(data, average, minimum, maximum, type)
{
    if (window.DEBUG)
        console.log(`[Supporter] _displayData - DATA=${data}, avg=${average}, min=${minimum}, max=${maximum} type=${type}`);

    const grid = document.getElementById(type);
    grid.querySelector(`.${type}`).textContent = data[data.length - 1];
    grid.querySelector(".average").textContent = average;
    grid.querySelector(".minimum").textContent = minimum;
    grid.querySelector(".maximum").textContent = maximum;
}

/**
 * @brief Ajoute un nouveau point de données sur le graphique.
 *
 * @param {Chart}  chart Instance Chart.js cible.
 * @param {number} data  Valeur de la donnée.
 * @param {number} type  Type de données.
 */
function _fillGraphicData(chart, data, type)
{
    const now = new Date();

    for (let i=data.length - 1; i >= 0; i--)
    {
        if (data[i] != 0)
        { 
            // Heure de la mesure formatée HH:MM:SS comme label de l'axe X
            const time = new Date(subtractSeconds(now, i * window.sensorDelay));
            const timestamp = time.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

            if (window.DEBUG)
                console.log(`[Supporter] _fillGraphicData - Ajout du point DATA=${data[i]} à t=${timestamp}`);

            if (type == "heart-rate")
            {
                chart.data.labels.push(timestamp);
                chart.data.datasets[0].data.push(data[i]);
            }
            else
            {
                if (window.DEBUG)
                console.log(`[Supporter] _fillGraphicData - Type de données inconnue: ${type}`);
            }

            // Limite l'historique affiché à 100 points
            if (chart.data.labels.length > 100)
            {
                if (type == "heart-rate")
                {
                    chart.data.labels.shift();
                    chart.data.datasets[0].data.shift();
                }
            }
        }
    }

    // Mise à jour sans animation pour un rendu temps réel fluide
    chart.update("none");
}
