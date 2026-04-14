/**
 * @file comparison.js
 *
 * @brief Logique de la page de comparaison.
 *
 * Demande les données de tous les type de support connectés et les affiche sur un graphique multi-courbes. Gère dynamiquement les connexions et déconnexions en temps réel via SocketIO.
 */

// ============================================================================
//  Import des bibliothèques
// ============================================================================

import { createChart } from "../Utils/board.js";
import { subtractSeconds } from "../Utils/time.js";
import { dataToString, typeToString } from "../Utils/stringConversion.js";

// ============================================================================
//  Initialisation
// ============================================================================

const socket = io();

// Création du titre de la page
document.querySelector("h1").textContent = `Comparison ${dataToString(window.data)} entre les ${typeToString(window.type)}`;

if (window.DEBUG)
    console.log("[Comparison] Initialisation - Demande des données");

// Création du graphique multi-courbes (vide au départ, alimenté par les événements)
const canva = document.getElementById("chart");
const ctx   = canva.getContext("2d");
const canvaX = document.getElementById("chartX");
const ctxX   = canvaX.getContext("2d");
const canvaY = document.getElementById("chartY");
const ctxY   = canvaY.getContext("2d");
const canvaZ = document.getElementById("chartZ");
const ctxZ   = canvaZ.getContext("2d");
let chart = null;

// Demande des données initiales
if (window.type == "Supporter" && window.data == "heart_rate")
{
    chart = createChart(ctx, [], "BPM", 40, 200, 10);
    socket.emit("getSupporterHeartRateAll");
}
else if (window.type == "StadiumBleacher" && window.data == "accelerometer")
{
    chartX = createChart(ctxX, [], "", -32768, 32767, 1000);
    chartY = createChart(ctxY, [], "", -32768, 32767, 1000);
    chartZ = createChart(ctxZ, [], "", -32768, 32767, 1000);
    canvaX.parentElement.classList.remove("display-none");
    canvaY.parentElement.classList.remove("display-none");
    canvaZ.parentElement.classList.remove("display-none");
    canva.parentElement.classList.add("display-none");
    socket.emit("getStadiumBleacherAccelerometerAll");
}
else if (window.type == "StadiumBleacher" && window.data == "acoustic")
{
    chart = createChart(ctx, [], "DB", 55, 120, 5);
    socket.emit("getStadiumBleacherAcousticAll");
}
else
{
    if (window.DEBUG)
        console.log(`[Comparison] Initialisation - Type de données ou type de support inconnu: type=${window.type} data=${window.data}`);
}

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception des fréquence cardiaque initiales de tous les supporters connectés.
 *
 * @param {Array<{id: number, name: string, color: string, heartRate: number}>} dataList Liste des données de chaque supporter connecté.
 */
socket.on("getSupporterHeartRateAllResponse", (dataList) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] getSupporterHeartRateAllResponse - Réception des données de ${dataList.length} supporter(s)`);

        for (const data of dataList)
        {
            if (window.DEBUG)
                console.log(`[Comparison] getSupporterHeartRateAllResponse - Ajout du supporter '${data.name}' (HR=${data.heartRate} bpm)`);

            _addToGraphic(chart, data.name, data.color);
            _fillGraphicData(chart, data.name, data.heartRate);
        }
    });

/**
 * @brief Réception des données acoustiques initiales de toutes les tribunes connectées.
 *
 * @param {Array<{id: number, name: string, color: string, acoustic: number}>} dataList Liste des données de chaque tribune connecté.
 */
socket.on("getStadiumBleacherAcousticAllResponse", (dataList) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] getStadiumBleacherAcousticAllResponse - Réception des données de ${dataList.length} tribune(s)`);

        for (const data of dataList)
        {
            if (window.DEBUG)
                console.log(`[Comparison] getStadiumBleacherAcousticAllResponse - Ajout de la tribune '${data.name}' (ACOUSTIC=${data.acoustic} db)`);

            _addToGraphic(chart, data.name, data.color);
            _fillGraphicData(chart, data.name, data.acoustic);
        }
    });

/**
 * @brief Réception des données de l'accéléromètre initiales de toutes les tribunes connectées.
 *
 * @param {Array<{id: number, name: string, color: string, accelerometer: [number, number, number]}>} dataList Liste des données de chaque tribune connecté.
 */
socket.on("getStadiumBleacherAccelerometerAllResponse", (dataList) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] getStadiumBleacherAccelerometerAllResponse - Réception des données de ${dataList.length} tribune(s)`);

        for (const data of dataList)
        {
            if (window.DEBUG)
                console.log(`[Comparison] getStadiumBleacherAccelerometerAllResponse - Ajout de la tribune '${data.name}' (ACCELEROMETER=${data.accelerometer})`);

            // Séparation des coordonnées
            const [x, y, z] = splitCoord(data.accelerometer)

            _addToGraphic(chartX, data.name, data.color);
            _fillGraphicData(chartX, data.name, x);
            _addToGraphic(chartY, data.name, data.color);
            _fillGraphicData(chartY, data.name, y);
            _addToGraphic(chartZ, data.name, data.color);
            _fillGraphicData(chartZ, data.name, z);
        }
    });

/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{name: string, heartRate: number}} data
 *        Nouvelles données du supporter.
 */
socket.on("newSupporterHeartRate", (data) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] newSupporterHeartRate - Nouvelle mesure pour '${data.name}' (HR=${data.heartRate} bpm)`);

        _fillGraphicData(chart, data.name, data.heartRate);
    });

/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{name: string, acoustic: number}} data
 *        Nouvelles données d'une tribune.
 */
socket.on("newStadiumBleacherAcoustic", (data) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] newStadiumBleacherAcoustic - Nouvelle mesure pour '${data.name}' (ACOUSTIC=${data.acoustic} db)`);

        _fillGraphicData(chart, data.name, data.acoustic);
    });

/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{name: string, accelerometer: [number, number, number]}} data
 *        Nouvelles données d'une tribune.
 */
socket.on("newStadiumBleacherAcoustic", (data) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] newStadiumBleacherAcoustic - Nouvelle mesure pour '${data.name}' (ACOUSTIC=${data.acoustic} db)`);

        // Séparation des coordonnées
        const [x, y, z] = splitCoord(data.accelerometer)

        _fillGraphicData(chartX, data.name, x);
        _fillGraphicData(chartY, data.name, y);
        _fillGraphicData(chartZ, data.name, z)
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
            console.log(`[ComparisonSupporter] supporterConnection - Nouveau supporter '${data.name}', ajout de la courbe`);

        _addToGraphic(chart, data.name, data.color);
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
            console.log(`[Comparison] stadiumBleacherConnection - Nouvelle tribune '${data.name}', ajout de la courbe`);

        _addToGraphic(chart, data.name, data.color);
        _addToGraphic(chartX, data.name, data.color);
        _addToGraphic(chartY, data.name, data.color);
        _addToGraphic(chartZ, data.name, data.color);
    });

/**
 * @brief Déconnexion d'un supporter en temps réel.
 *
 * @param {string} supporterName Nom du supporter déconnecté.
 */
socket.on("supporterDisconnection", (supporterName) =>
    {
        if (window.DEBUG)
            console.log(`[ComparisonSupporter] supporterDisconnection - Suppression de la courbe du supporter '${supporterName}'`);

        _removeFromGraphic(chart, supporterName);
    });

/**
 * @brief Déconnexion d'une tribune en temps réel.
 *
 * @param {string} stadiumBleacherName Nom de la tribune déconnecté.
 */
socket.on("stadiumBleacherDisconnection", (stadiumBleacherName) =>
    {
        if (window.DEBUG)
            console.log(`[Comparison] stadiumBleacherDisconnection - Suppression de la courbe de la tribune '${stadiumBleacherName}'`);

        _removeFromGraphic(chart, stadiumBleacherName);
        _removeFromGraphic(chartX, stadiumBleacherName);
        _removeFromGraphic(chartY, stadiumBleacherName);
        _removeFromGraphic(chartZ, stadiumBleacherName);
    });

/**
 * @brief Fermeture du serveur.
 */
socket.on("serverClose", () =>
    {
        if (window.DEBUG)
            console.log("[ComparisonSupporter] serverClose - Fermeture du serveur, redirection vers l'accueil");

        window.location.href = "/";
    });

// ============================================================================
//  Fonctions internes
// ============================================================================

/**
 * @brief Ajoute un nouveau point de données sur la courbe.
 *
 * @param {Chart}  chart Instance Chart.js cible.
 * @param {string} name  Label de la courbe.
 * @param {number} data  Valeur des données.
 */
function _fillGraphicData(chart, name, data)
{
    const index = chart.data.datasets.findIndex(d => d.label === name);

    if (index === -1)
    {
        if (window.DEBUG)
            console.log(`[Comparison] _fillGraphicData - Courbe '${name}' introuvable, point ignoré`);
        return;
    }

    const now = new Date();

    for (let i=data.length - 1; i >= 0; i--)
    {
        if (data[i] != 0)
        {
            // Heure de la mesure formatée HH:MM:SS comme label de l'axe X
            const time = new Date(subtractSeconds(now, i * window.sensorDelay));
            const timestamp = time.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

            if (window.DEBUG)
                console.log(`[Comparison] _fillGraphic - Ajout du point DATA=${data[i]} pour '${name}' à t=${timestamp}`);

            chart.data.datasets[index].data.push({ x: timestamp, y: data[i] });

            // Limite l'historique affiché à 100 points
            if (chart.data.datasets[index].data.length > 100)
                chart.data.datasets[index].data.shift();
        }
    }

    // Mise à jour sans animation pour un rendu temps réel fluide
    chart.update("none");
}

/**
 * @brief Ajoute une nouvelle courbe vide pour un supporter sur le graphique.
 *
 * @param {Chart}  chart Instance Chart.js cible.
 * @param {string} name  Label de la courbe.
 * @param {string} color Couleur CSS de la courbe (ex : "#FF0000").
 */
function _addToGraphic(chart, name, color)
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
 * @param {string} name  Label de la courbe à supprimer.
 */
function _removeFromGraphic(chart, name)
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

// ============================================================================
//  Fonction utilitaire
// ============================================================================

/**
 * @brief Sépare les coordonnées dans trois tableau.
 * 
 * @param array Tableau à séparer.
 * 
 * @return {{array} {array} {array}} Les tableaux de chaque coordonnées.
 */
function splitCoord(array) 
{
  // Initialiser les tableaux pour x, y et z
  let xArray = [];
  let yArray = [];
  let zArray = [];

  // Parcourir le tableau d'entrées et extraire chaque valeur de x, y et z
  array.forEach(([x, y, z]) => {
    xArray.push(x);
    yArray.push(y);
    zArray.push(z);
  });

  // Retourner les trois tableaux
  return [xArray, yArray, zArray];
}
