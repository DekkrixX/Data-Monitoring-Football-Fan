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

import { createChart } from "../Utils/element.js";
import { subtractSeconds } from "../Utils/time.js";

// ============================================================================
//  Initialisation
// ============================================================================

const socket = io();

if (window.DEBUG)
    console.log(`[StadiumBleacher] Initialisation - Demande des données de la tribune id=${window.id}`);

let selectedGraph = 0;
changeDisplayGraph(selectedGraph);

// Création du graphique d'accélération
const canvaAccelerometer = document.getElementById("chart_accelerometer");
const ctxAccelerometer   = canvaAccelerometer.getContext("2d");
const chartAccelerometer = createChart(ctxAccelerometer, [{title: window.name, color: window.color}], "m/s2", 0, 19.62, 1.5);

// Création du graphique acoustic
const canvaAcoustic = document.getElementById("chart_acoustic");
const ctxAcoustic   = canvaAcoustic.getContext("2d");
const chartAcoustic = createChart(ctxAcoustic, [{ title: window.name, color: window.color}], "DB", 0, 160, 10);

// Demande des données initiales de la tribune
// window.id est utilisé explicitement pour éviter toute ambiguïté avec une
// variable locale non définie
socket.emit("getStadiumBleacherAccelerometer", window.id);
socket.emit("getStadiumBleacherAcoustic", window.id);

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception des données initiales de la tribune.
 *
 * @param {{id: number, accelerometer: [number, number, number], average: number, minimum: number, maximum: number}} data Données de la tribune.
 */
socket.on("getStadiumBleacherAccelerometerResponse", (data) =>
{
    if (data.id !== window.id)
        return;

    if (window.DEBUG)
        console.log(`[StadiumBleacher] getStadiumBleacherAccelerometerResponse - Réception des données initiales (ACCELEROMETER=${data.accelerometer})`);

    if (data.accelerometer != "")
    {
        _displayData(data.accelerometer, data.average, data.minimum, data.maximum, "accelerometer");
        _fillGraphicData(chartAccelerometer, data.accelerometer, "accelerometer");
    }
    else
        _displayData(["-"], "-", "-", "-", "accelerometer");
});



/**
 * @brief Réception des données initiales de la tribune.
 *
 * @param {{id: number, acoustic: number, average: number, minimum: number, maximum: number}} data Données de la tribune.
 */
socket.on("getStadiumBleacherAcousticResponse", (data) =>
{
    if (data.id !== window.id)
        return;

    if (window.DEBUG)
        console.log(`[StadiumBleacher] getStadiumBleacherAcousticResponse - Réception des données initiales (ACOUSTIC=${data.acoustic})`);

    if (data.acoustic != "")
    {
        _displayData(data.acoustic, data.average, data.minimum, data.maximum, "acoustic");
        _fillGraphicData(chartAcoustic, data.acoustic, "acoustic");
    }
    else
        _displayData(["-"], "-", "-", "-", "acoustic");
});



/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{id: number, accelerometer: [number, number, number], average: number, minimum: number, maximum: number}} data Nouvelles données de la tribune.
 */
socket.on("newStadiumBleacherAccelerometer", (data) =>
{
    if (data.id !== window.id)
        return;

    if (window.DEBUG)
        console.log(`[StadiumBleacher] newStadiumBleacherAccelerometer - Nouvelle mesure reçue (ACCELEROMETER=${data.accelerometer})`);

    _displayData(data.accelerometer, data.average, data.minimum, data.maximum, "accelerometer");
    _fillGraphicData(chartAccelerometer, data.accelerometer, "accelerometer");
});



/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{id: number, acoustic: number, average: number, minimum: number, maximum: number}} data Nouvelles données de la tribune.
 */
socket.on("newStadiumBleacherAcoustic", (data) =>
{
    if (data.id !== window.id)
        return;

    if (window.DEBUG)
        console.log(`[StadiumBleacher] newStadiumBleacherAcoustic - Nouvelle mesure reçue (ACOUSTIC=${data.acoustic})`);

    _displayData(data.acoustic, data.average, data.minimum, data.maximum, "acoustic");
    _fillGraphicData(chartAcoustic, data.acoustic, "acoustic");
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



// Bouton de sélection
const prev = document.getElementById("prev");
const next = document.getElementById("next");
prev.addEventListener("click", () =>
{
    if (selectedGraph != 0)
    {
        selectedGraph--;
        changeDisplayGraph(selectedGraph);
    }
    if (selectedGraph == 0)
        prev.classList.add("hidden");
    next.classList.remove("hidden");
});
next.addEventListener("click", () =>
{
    if (selectedGraph != window.numberGraph - 1)
    {
        selectedGraph++;
        changeDisplayGraph(selectedGraph);
    }
    if (selectedGraph == window.numberGraph - 1)
        next.classList.add("hidden");
    prev.classList.remove("hidden");
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

    return ;
}

/**
 * @brief Met à jour les éléments DOM affichant les statistiques de la tribune.
 *
 * @param {number} data    Dernière donnée enregistré.
 * @param {number} average Moyenne enregistré.
 * @param {number} minimum Minimum enregistré.
 * @param {number} maximum Maximum enregistré.
 */
function _displayData(data, average, minimum, maximum, type)
{
    if (window.DEBUG)
        console.log(`[StadiumBleacher] _displayData - DATA=${accelerometer}, avg=${average}, min=${minimum}, max=${maximum} type=${type}`);

    const grid = document.getElementById(type);
    grid.querySelector(`.${type}`).textContent = data[data.length - 1];
    grid.querySelector(".average").textContent = average;
    grid.querySelector(".minimum").textContent = minimum;
    grid.querySelector(".maximum").textContent = maximum;

    return ;
}

/**
 * @brief Ajoute un nouveau point d'accélération sur le graphique.
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
                    console.log(`[StadiumBleacher] _fillGraphicData - Ajout du point DATA=${data[i]} à t=${timestamp}`);

            if (type == "acoustic" || type == "accelerometer")
            {
                chart.data.labels.push(timestamp);
                chart.data.datasets[0].data.push(data[i]);
            }
            else
            {
                if (window.DEBUG)
                    console.log(`[StadiumBleacher] _fillGraphicData - Type de données inconnue: ${type}`);
            }

            // Limite l'historique affiché à 100 points
            if (chart.data.labels.length > 100)
            {
                if (type == "acoustic" || type == "accelerometer")
                {
                    chart.data.labels.shift();
                    chart.data.datasets[0].data.shift();
                }
            }
        }
    }

    // Mise à jour sans animation pour un rendu temps réel fluide
    chart.update("none");

    return ;
}



/**
 * @brief Change le graphe à afficher
 * 
 * @param selectedGraph Indice du graphe sélectionné.
 */
function changeDisplayGraph(selectedGraph)
{
    if (window.DEBUG)
        console.log("[StadiumBleacher] Changement de graphe");

    const main = document.querySelector("main");

    for (let index=0; index < main.childElementCount; index+=2)
    {
        console.log(`index=${index} (mod2=${index / 2})`);
        if (index / 2 == selectedGraph)
        {
            main.children[index].classList.remove("hidden");
            main.children[index + 1].classList.remove("hidden");
        }
        else
        {
            main.children[index].classList.add("hidden");
            main.children[index + 1].classList.add("hidden");
        }
    }

    return ;
}
