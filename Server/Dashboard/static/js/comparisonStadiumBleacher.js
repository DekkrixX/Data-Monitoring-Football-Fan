/**
 * @file comparisonStadiumBleacher.js
 *
 * @brief Logique de la page de comparaison des tribunes.
 *
 * Demande les données de tous les tribunes connectés et les affiche sur un graphique multi-courbes, une courbe par tribune. Gère dynamiquement les connexions et déconnexions en temps réel via SocketIO.
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
    console.log("[ComparisonStadiumBleacher] Initialisation - Demande des données de toutes les tribunes");

// Création du graphique multi-courbes (vide au départ, alimenté par les événements)
const canva = document.getElementById("chart");
const ctx   = canva.getContext("2d");
const chart = createStadiumBleacherChart(ctx, []);

// Demande des données initiales de toutes les tribunes connectés
socket.emit("getStadiumBleacherDataAll");

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception des données initiales de toutes les tribunes connectés.
 *
 * @param {Array<{id: number, name: string, color: string, accelerometer: [number, number, number]}>} dataList Liste des données de chaque tribune connecté.
 */
socket.on("getStadiumBleacherDataAllResponse", (dataList) =>
    {
        if (window.DEBUG)
            console.log(`[ComparisonStadiumBleacher] getStadiumBleacherDataAllResponse - Réception des données de ${dataList.length} tribune(s)`);

        for (const data of dataList)
        {
            if (window.DEBUG)
                console.log(`[ComparisonStadiumBleacher] getStadiumBleacherDataAllResponse - Ajout de la tribune '${data.name}' (ACCELEROMETER=${data.accelerometer})`);

            _addStadiumBleacherToGraphic(chart, data.name, data.color);
            _fillGraphic(chart, data.name, data.accelerometer);
        }
    });

/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{name: string, accelerometer: [number, number, number]}} data
 *        Nouvelles données du supporter.
 */
socket.on("newStadiumBleacherData", (data) =>
    {
        if (window.DEBUG)
            console.log(`[ComparisonStadiumBleacher] newStadiumBleacherData - Nouvelle mesure pour '${data.name}' (ACCELEROMETER=${data.accelerometer})`);

        _fillGraphic(chart, data.name, data.accelerometer);
    });

/**
 * @brief Connexion d'une nouvelle tribune en temps réel.
 *
 * @param {{name: string, color: string}} data
 *        Données de la tribune qui vient de se connecter.
 */
socket.on("stadiumBleacherConnection", (data) =>
    {
        if (window.DEBUG)
            console.log(`[ComparisonStadiumBleacher] stadiumBleacherConnection - Nouvelle tribune '${data.name}', ajout de la courbe`);

        _addStadiumBleacherToGraphic(chart, data.name, data.color);
    });

/**
 * @brief Déconnexion d'une tribune en temps réel.
 *
 * @param {string} stadiumBleacherName Nom de la tribune déconnecté.
 */
socket.on("stadiumBleacherDisconnection", (stadiumBleacherName) =>
    {
        if (window.DEBUG)
            console.log(`[ComparisonStadiumBleacher] stadiumBleacherDisconnection - Suppression de la courbe de la tribune '${stadiumBleacherName}'`);

        _removeStadiumBleacherFromGraphic(chart, stadiumBleacherName);
    });

/**
 * @brief Fermeture du serveur.
 */
socket.on("serverClose", () =>
    {
        if (window.DEBUG)
            console.log("[ComparisonStadiumBleacher] serverClose - Fermeture du serveur, redirection vers l'accueil");

        window.location.href = "/";
    });

// ============================================================================
//  Fonctions internes
// ============================================================================

/**
 * @brief Ajoute un nouveau point d'accélération sur la courbe d'une tribune.
 *
 * @param {Chart}  chart         Instance Chart.js cible.
 * @param {string} name          Nom du supporter (label de la courbe).
 * @param {number} accelerometer Mesure de l'accéléromètre.
 */
function _fillGraphic(chart, name, accelerometer)
{
    const index = chart.data.datasets.findIndex(d => d.label === `${name} x`);

    if (index === -1)
    {
        if (window.DEBUG)
            console.log(`[ComparisonStadiumBleacher] _fillGraphic - Courbe '${name}' introuvable, point ignoré`);
        return;
    }

    const now = new Date();

    for (let i=accelerometer.length - 1; i >= 0; i--)
    {
        if (accelerometer[i] != 0)
        {
            // Heure de la mesure formatée HH:MM:SS comme label de l'axe X
            const time = new Date(subtractSeconds(now, i * window.accelerometerGyroscopeSensorDelay));
            const timestamp = time.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

            if (window.DEBUG)
                console.log(`[ComparisonStadiumBleacher] _fillGraphic - Ajout du point ACCELEROMETER=${accelerometer[i]} pour '${name}' à t=${timestamp}`);

            for (let j=0; j < 3; j++)
                chart.data.datasets[index + j].data.push({ x: timestamp, y: accelerometer[i][j] });

            // Limite l'historique affiché à 100 points
            if (chart.data.datasets[index].data.length > 100)
            {
                for (let j=0; j < 3; j++)
                    chart.data.datasets[index + j].data.shift();
            }
        }
    }

    // Mise à jour sans animation pour un rendu temps réel fluide
    chart.update("none");
}

/**
 * @brief Ajoute une nouvelle courbe vide pour une tribune sur le graphique.
 *
 * @param {Chart}  chart Instance Chart.js cible.
 * @param {string} name  Nom de la tribune.
 * @param {string} color Couleur CSS de la courbe (ex : "#FF0000").
 */
function _addStadiumBleacherToGraphic(chart, name, color)
{
    // Vérifie qu'une courbe portant ce nom n'existe pas déjà
    const alreadyExists = chart.data.datasets.some(d => d.label === `${name} x`);

    if (alreadyExists)
    {
        if (window.DEBUG)
            console.log(`[ComparisonStadiumBleacher] _addStadiumBleacherToGraphic - Courbe '${name}' déjà présente, ajout ignoré`);
        return;
    }

    if (window.DEBUG)
        console.log(`[ComparisonStadiumBleacher] _addStadiumBleacherToGraphic - Ajout de la courbe '${name}' (color='${color}')`);

    // Couleurs dérivées
    const colorX = color;                   // couleur originale
    const colorY = adjustColor(color, -30); // plus foncée
    const colorZ = adjustColor(color, +30); // plus claire

    // Création des courbes des points (x, y, z)
    chart.data.datasets.push({
        label: `${name} x`,
        data: [],
        borderColor: colorX,
        fill: false,
        tension: 0.4,
        pointRadius: 4,
        borderWidth: 3
    });

    chart.data.datasets.push({
        label: `${name} y`,
        data: [],
        borderColor: colorY,
        fill: false,
        tension: 0.4,
        pointRadius: 4,
        borderWidth: 3
    });

    chart.data.datasets.push({
        label: `${name} z`,
        data: [],
        borderColor: colorZ,
        fill: false,
        tension: 0.4,
        pointRadius: 4,
        borderWidth: 3
    });

    chart.update("none");
}

/**
 * @brief Retire la courbe d'une tribune du graphique.
 *
 * @param {Chart}  chart Instance Chart.js cible.
 * @param {string} name  Nom de la tribune.
 */
function _removeStadiumBleacherFromGraphic(chart, name)
{
    const index = chart.data.datasets.findIndex(d => d.label === `${name} x`);

    if (index === -1)
    {
        if (window.DEBUG)
            console.log(`[ComparisonStadiumBleacher] _removeStadiumBleacherFromGraphic - Courbe '${name}' introuvable, suppression ignorée`);
        return;
    }

    if (window.DEBUG)
        console.log(`[ComparisonStadiumBleacher] _removeStadiumBleacherFromGraphic - Suppression de la courbe '${name}'`);

    chart.data.datasets.splice(index, 1);
    chart.update("none");
}
