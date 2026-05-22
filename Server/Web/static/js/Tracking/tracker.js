/**
 * @file tracker.js
 *
 * @brief Logique de la page de détail d'un tracker.
 *
 * Demande les données initiales du tracker identifié par window.id, met à jour l'affichage et le graph à chaque nouvelle notification reçue via SocketIO.
 */

// ============================================================================
//  Import des bibliothèques
// ============================================================================


// ============================================================================
//  Initialisation
// ============================================================================

const socket = io();

// Création du graph du tracking de l'objet
const canvas = document.getElementById("graph");
const ctx    = canvas.getContext("2d");

/**
 * @brief Met à jour automatiquement la taille du canvas.
 */
function resizeCanvas()
{
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;

    return ;
}

window.addEventListener("resize", resizeCanvas);
resizeCanvas();

if (window.DEBUG)
    console.log(`[Tracker] Initialisation - Demande des données du tracker id=${window.id}`);

// Demande de la position du tracker actuellement connectés
socket.emit("getTrackerPosition", window.id);

// ============================================================================
//  Événements SocketIO
// ============================================================================

/**
 * @brief Réception des données initiales du tracker.
 *
 * @param {{id: number, position: number, zone: list}} data Données du tracker.
 */
socket.on("getTrackerPositionResponse", (data) =>
{
    if (data.id !== window.id)
        return;

    if (window.DEBUG)
        console.log(`[Tracker] getTrackerPositionResponse - Réception des données initiales (POSITION=${data.position})`);

    if (data.position != "")
        _update(data.position, data.zone, data.color, data.lastPositions);
});



/**
 * @brief Réception d'une nouvelle mesure en temps réel.
 *
 * @param {{id: number, position: number}} data Nouvelles données du tracker.
 */
socket.on("newTrackerPosition", (data) =>
{
    if (data.id !== window.id)
        return;

    if (window.DEBUG)
        console.log(`[Tracker] newTracker - Nouvelle mesure reçue (POSITION=${data.position})`);

    _update(data.position, data.zone, data.color, data.lastPositions);
});



/**
 * @brief Déconnexion du tracker actuellement affiché.
 *
 * @param {number} trackerId Identifiant du tracker déconnecté.
 */
socket.on("trackerDisconnection", (trackerId) =>
{
    if (trackerId !== window.id)
        return;

    if (window.DEBUG)
        console.log(`[Tracker] trackerDisconnection - Tracker id=${window.id} déconnecté`);

    _showDisconnectMessage();
});



/**
 * @brief Fermeture du serveur.
 */
socket.on("serverClose", () =>
{
    if (window.DEBUG)
        console.log("[Tracker] serverClose - Fermeture du serveur, redirection vers l'accueil");

    window.location.href = "/tracking";
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
        console.log("[Tracker] _showDisconnectMessage - Affichage de l'overlay de déconnexion");

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
    message.textContent            = "Tracker déconnecté";
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
            console.log("[Tracker] _showDisconnectMessage - Suppression de l'overlay");

        overlay.remove();
    }, 5000);

    return ;
}



/**
 * @brief Converti les coordonnées réel en coordonnées canvas.
 * 
 * @param x Coordonnées x réel.
 * @param y Coordonnées y réel.
 * 
 * @return {x, y} Les coordonnées canvas.
 */
function _convertToCanvas(x, y)
{
    return {
        x: canvas.width / 2 + x,
        y: canvas.height / 2 - y
    };
}



/**
 * @brief Dessine la zone de tracking.
 * 
 * @param zone Les points du polygone formant la zone de tracking.
 */
function _drawTrackingZone(zone)
{
    ctx.beginPath();

    const first = _convertToCanvas(zone[0].x, zone[0].y);
    ctx.moveTo(first.x, first.y);

    for (let index=1; index < zone.length; index++)
    {
        const point = _convertToCanvas(zone[index].x, zone[index].y);
        ctx.lineTo(point.x, point.y);
    }

    ctx.closePath();

    ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue("--graph-zone");
    ctx.lineWidth = 5;
    ctx.stroke();

	return ;
}



/**
 * @brief Dessine l'objet tracké.
 * 
 * @param position Nouvelle position de l'objet.
 * @param color    Couleur du point.
 */
function _drawTrackingObject(position, color)
{
    const point = _convertToCanvas(position[0], position[1]);

    ctx.beginPath();
    ctx.arc(point.x, point.y, 15, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(128, 128, 128, 0.2)";
    ctx.fill();

    ctx.beginPath();
    ctx.arc(point.x, point.y, 6, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();

	return ;
}



/**
 * @brief Dessine le chemin fait par l'objet tracké.
 * 
 * @param position     Nouvelle position de l'objet.
 * @param lastPosition Historique des positions de l'objet.
 * @param color        Couleur du tracé.
 */
function _drawTrace(position, lastPositions, color)
{
    if (lastPositions.length === 0)
        return;

    ctx.beginPath();

    // Dessiner le chemin entre tous les points stockés dans lastPositions
    const firstPoint = _convertToCanvas(lastPositions[0], lastPositions[1]);
    ctx.moveTo(firstPoint.x, firstPoint.y);

    for (let index = 2; index < lastPositions.length; index += 2)
    {
        const point = _convertToCanvas(lastPositions[index], lastPositions[index + 1]);
        ctx.lineTo(point.x, point.y);
    }

    // Ajouter le segment final vers la position actuelle
    const currentPoint = _convertToCanvas(position[0], position[1]);
    ctx.lineTo(currentPoint.x, currentPoint.y);

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.stroke();

    return ;
}



/**
 * @brief Boucle de dessin du tracking.
 * 
 * @param position      Position de l'objet tracké.
 * @param zone          Délimitation de la zone de tracking.
 * @param color         Couleur du point.
 * @param lastPositions Historique des positions de l'objet.
 */
function _update(position, zone, color, lastPositions)
{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

	_drawTrackingZone(zone);
	_drawTrackingObject(position, color);
    _drawTrace(position, lastPositions, color);

	return ;
}
