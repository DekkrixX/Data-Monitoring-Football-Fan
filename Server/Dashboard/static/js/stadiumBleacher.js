/**
 * @file stadiumBleacher.js
 *
 * @brief Logique de la page de détail d'une tribune.
 *
 * Demande les données initiales de la tribune identifié par window.id, met à jour l'affichage et le graphique à chaque nouvelle notification reçue via SocketIO.
 */

// ============================================================================
//  Import des bibliothèques
// ============================================================================

import { createStadiumBleacherChart } from "./Utils/board.js";
import { subtractSeconds } from "./Utils/time.js";
import { adjustColor } from "./Utils/color.js";

// ============================================================================
//  Initialisation
// ============================================================================

const socket = io();

if (window.DEBUG)
    console.log(`[StadiumBleacher] Initialisation - Demande des données de la tribune id=${window.id}`);

// Création du graphique d'accélération
const canva = document.getElementById("chart");
const ctx   = canva.getContext("2d");
const chart = createStadiumBleacherChart(ctx, []);

// Couleurs dérivées
const colorX = color;                   // couleur originale
const colorY = adjustColor(color, -30); // plus foncée
const colorZ = adjustColor(color, +30); // plus claire

// Création des courbes des points (x, y, z)
chart.data.datasets.push({
    label: "x",
    data: [],
    borderColor: colorX,
    fill: false,
    tension: 0.4,
    pointRadius: 4,
    borderWidth: 3
});

chart.data.datasets.push({
    label: "y",
    data: [],
    borderColor: colorY,
    fill: false,
    tension: 0.4,
    pointRadius: 4,
    borderWidth: 3
});

chart.data.datasets.push({
    label: "z",
    data: [],
    borderColor: colorZ,
    fill: false,
    tension: 0.4,
    pointRadius: 4,
    borderWidth: 3
});

// Demande des données initiales de la tribune
// window.id est utilisé explicitement pour éviter toute ambiguïté avec une
// variable locale non définie
socket.emit("getStadiumBleacherData", window.id);

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception des données initiales de la tribune.
 *
 * @param {{id: number, accelerometer: [number, number, number], average: number, minimum: number, maximum: number}} data Données de la tribune.
 */
socket.on("getStadiumBleacherDataResponse", (data) =>
    {
        if (data.id !== window.id)
            return;

        if (window.DEBUG)
            console.log(`[StadiumBleacher] getStadiumBleacherDataResponse - Réception des données initiales (ACCELEROMETER=${data.accelerometer})`);

        _displayData(data.accelerometer, data.average, data.minimum, data.maximum);
        _fillGraphic(chart, data.accelerometer);
    });

/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{id: number, accelerometer: [number, number, number], average: number, minimum: number, maximum: number}} data Nouvelles données de la tribune.
 */
socket.on("newStadiumBleacherData", (data) =>
    {
        if (data.id !== window.id)
            return;

        if (window.DEBUG)
            console.log(`[StadiumBleacher] newStadiumBleacherData - Nouvelle mesure reçue (ACCELEROMETER=${data.accelerometer})`);

        _displayData(data.accelerometer, data.average, data.minimum, data.maximum);
        _fillGraphic(chart, data.accelerometer);
    });

/**
 * @brief Déconnexion de la tribune actuellement affiché.
 *
 * @param {number} stadiumBleacherId Identifiant de la tribune déconnecté.
 */
socket.on("stadiumBleacherDisconnection", (stadiumBleacherId) =>
    {
        if (stadiumBleacherId !== window.id)
            return;

        if (window.DEBUG)
            console.log(`[StadiumBleacher] stadiumBleacherDisconnection - Tribune id=${window.id} déconnecté`);

        _showDisconnectMessage();
    });

/**
 * @brief Fermeture du serveur.
 */
socket.on("serverClose", () =>
    {
        if (window.DEBUG)
            console.log("[StadiumBleacher] serverClose - Fermeture du serveur, redirection vers l'accueil");

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
        console.log("[StadiumBleacher] _showDisconnectMessage - Affichage de l'overlay de déconnexion");

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
    message.textContent            = "Tribune déconnecté";
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
                console.log("[StadiumBleacher] _showDisconnectMessage - Suppression de l'overlay");

            overlay.remove();
        }, 5000);
}

/**
 * @brief Met à jour les éléments DOM affichant les statistiques de la tribune.
 *
 * @param {number} accelerometer Dernière mesure de l'accéléromètre.
 * @param {number} average       Moyenne des mesure de l'accéléromètre.
 * @param {number} minimum       Minimum enregistré en bpm.
 * @param {number} maximum       Maximum enregistré en bpm.
 */
function _displayData(accelerometer, average, minimum, maximum)
{
    if (window.DEBUG)
        console.log(`[StadiumBleacher] _displayData - ACCELEROMETER=${accelerometer}, avg=${average}, min=${minimum}, max=${maximum}`);

    const lastAccelerometer = accelerometer[accelerometer.length - 1]
    console.log(`TEST=${lastAccelerometer}`)
    document.getElementById("accelerometer").textContent = `(${lastAccelerometer[0]}, ${lastAccelerometer[1]}, ${lastAccelerometer[2]})`;
    document.getElementById("average").textContent       = average;
    document.getElementById("minimum").textContent       = minimum;
    document.getElementById("maximum").textContent       = maximum;
}

/**
 * @brief Ajoute un nouveau point d'accélération sur le graphique.
 *
 * @param {Chart}  chart         Instance Chart.js cible.
 * @param {number} accelerometer Mesure d'accélération.
 */
function _fillGraphic(chart, accelerometer)
{
    const now = new Date();

    for (let i=accelerometer.length - 1; i >= 0; i--)
    {
        if (accelerometer[i] != 0)
        { 
            // Heure de la mesure formatée HH:MM:SS comme label de l'axe X
            const time = new Date(subtractSeconds(now, i));
            const timestamp = time.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

            if (window.DEBUG)
                    console.log(`[StadiumBleacher] _fillGraphic - Ajout du point ACCELEROMETER=${accelerometer[i]} à t=${timestamp}`);

            chart.data.labels.push(timestamp);
            for (let j=0; j < 3; j++)
                chart.data.datasets[j].data.push(accelerometer[i][j]);

            // Limite l'historique affiché à 100 points
            if (chart.data.labels.length > 100)
            {
                chart.data.labels.shift();
                for (let j=0; j < 3; j++)
                    chart.data.datasets[j].data.shift();
            }
        }
    }

    // Mise à jour sans animation pour un rendu temps réel fluide
    chart.update("none");
}