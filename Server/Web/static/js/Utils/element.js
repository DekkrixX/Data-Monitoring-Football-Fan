/**
 * @file element.js
 *
 * @brief Composants UI et utilitaires graphiques partagés entre les pages.
 *
 * Fournit les fonctions de création d'éléments HTML.
 */

// ============================================================================
//  Fonction de création de composant HTML
// ============================================================================

/**
 * @brief Crée et retourne une carte HTML cliquable représentant un supporter.
 *
 * @param {number} id    Identifiant unique du supporter.
 * @param {string} name  Nom d'affichage du supporter.
 * @param {string} color Code couleur du supporter
 *
 * @returns {HTMLDivElement} Élément div prêt à être inséré dans le DOM.
 */
export function supporterCard(id, name, color)
{
    if (DEBUG)
        console.log(`[Element] supporterCard - Création de la carte pour le supporter id=${id} (${name})`);

    // Création de la carte
    const card = document.createElement("div");
    card.id = "s" + id;
    card.classList.add("card");

    // Redirection vers la page de détail du supporter au clic
    card.addEventListener("click", () =>
        {
            if (DEBUG)
                console.log(`[Element] supporterCard - Clic sur la carte du supporter id=${id}, redirection vers /supporter/${id}`);

            window.location.href = "/supporter/" + id;
        });

    // Création des éléments texte
    const pName = document.createElement("p");
    pName.textContent = name;
    pName.classList.add("name");
    pName.style.color = color;

    const pId = document.createElement("p");
    pId.textContent = "Supporter n°" + id;
    pId.classList.add("id");

    card.appendChild(pName);
    card.appendChild(pId);

    return card;
}



/**
 * @brief Crée et retourne une carte HTML cliquable représentant une tribune.
 *
 * @param {number} id    Identifiant unique de la tribune.
 * @param {string} name  Nom d'affichage de la tribune.
 * @param {string} color Code couleur de la tribune
 *
 * @returns {HTMLDivElement} Élément div prêt à être inséré dans le DOM.
 */
export function stadiumBleacherCard(id, name, color)
{
    if (DEBUG)
        console.log(`[Element] stadiumBleacherCard - Création de la carte pour la tribune id=${id} (${name})`);

    // Création de la carte
    const card = document.createElement("div");
    card.id = "b" + id;
    card.classList.add("card");

    // Redirection vers la page de détail de la tribune au clic
    card.addEventListener("click", () =>
        {
            if (DEBUG)
                console.log(`[Element] stadiumBleacherCard - Clic sur la carte du supporter id=${id}, redirection vers /stadiumBleacher/${id}`);

            window.location.href = "/stadiumBleacher/" + id;
        });

    // Création des éléments texte
    const pName = document.createElement("p");
    pName.textContent = name;
    pName.classList.add("name");
    pName.style.color = color;

    const pId = document.createElement("p");
    pId.textContent = "Tribune n°" + id;
    pId.classList.add("id");

    card.appendChild(pName);
    card.appendChild(pId);

    return card;
}



/**
 * @brief Crée et retourne la carte HTML de comparaison entre supporters ou tribunes.
 * 
 * @param type  Type de comparaison.
 * @param data  Type de données de comparaison.
 * @param titre Titre de la carte.
 *
 * @returns {HTMLDivElement} Élément div prêt à être inséré dans le DOM.
 */
export function comparisonCard(type, data, titre)
{
    if (DEBUG)
        console.log("[Element] comparisonCard - Création de la carte de comparaison");

    // Création de la carte
    const card = document.createElement("div");
    card.id = "comparison" + type;
    card.classList.add("card");

    // Redirection vers la page de comparaison au clic
    card.addEventListener("click", () =>
        {
            if (DEBUG)
                console.log("[Element] comparisonCard - Clic sur la carte de comparaison, redirection vers /comparison");

            window.location.href = "/comparison/" + type + "/" + data;
        });

    // Création des éléments texte
    const pName = document.createElement("p");
    pName.textContent = titre;
    pName.classList.add("name");

    const pId = document.createElement("p");
    pId.textContent = "Comparaison";
    pId.classList.add("id");

    card.appendChild(pName);
    card.appendChild(pId);

    return card;
}



/**
 * @brief Crée et retourne un graphique Chart.js de type "line" configuré
 *        pour afficher des données en temps réel.
 *
 * @param {CanvasRenderingContext2D} ctx               Contexte 2D du canvas cible.
 * @param {Array<{title: string, color: string}>} list Liste des courbes à créer.
 * @param {string} value                               Unité des valeurs.
 * @param {number} min                                 Borne minimal des valeurs.
 * @param {number} max                                 Borne maximal des valeurs.
 * @param {number} step                                Pas entre les valeurs.
 *
 * @returns {Chart} Instance Chart.js prête à l'emploi.
 */
export function createChart(ctx, list, value, min, max, step)
{
    if (window.DEBUG)
        console.log(`[Element] createChart - Création du graphique avec ${list.length} dataset(s)`);

    // Construction des datasets à partir de la liste fournie
    const datasetList = list.map((element) =>
        {
            if (window.DEBUG)
                console.log(`[Element] createChart - Dataset: label='${element.title}', color='${element.color}'`);

            return {
                label:           element.title,
                data:            [],
                borderColor:     element.color,
                backgroundColor: element.color + "33", // Couleur de fond avec opacité 20%
                fill:            false,
                tension:         0.4,
                pointRadius:     4,
                borderWidth:     3
            };
        });

    // Création du graphique Chart.js
    const chart = new Chart(ctx, {
        type: "line",
        data: {
            labels:   [],
            datasets: datasetList
        },
        options: {
            responsive:          true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    title: {
                        display: true,
                        text:    value,
                        color:   "#333",
                        font:    { size: 14, weight: "bold" }
                    },
                    beginAtZero: false,
                    min:         min,
                    max:         max,
                    ticks:       { stepSize: step }
                },
                x: {
                    title: {
                        display: true,
                        text:    "Temps",
                        color:   "#333",
                        font:    { size: 14, weight: "bold" }
                    },
                    ticks: { maxTicksLimit: 20 }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color:     "#333",
                        boxWidth:  20,
                        boxHeight: 12,
                        padding:   15,
                        font:      { size: 18, weight: "bold" }
                    }
                }
            }
        }
    });

    if (window.DEBUG)
        console.log("[Element] createChart - Graphique créé");

    return chart;
}



/**
 * @brief Crée et retourne un évènement.
 *
 * @param {string}   name    Nom de l'évènement.
 * @param {number}   code    Code de l'évènement.
 * @param {number}   matchId Identifiant du match.
 * @param {socketio} socket  Socket de connexion au serveur.
 *
 * @returns {HTMLDivElement} Élément div prêt à être inséré dans le DOM.
 */
export function createEvent(name, code, matchId, socket)
{
    if (window.DEBUG)
        console.log(`[Element] createEvent - Création de l'évènement : ${name}`);

    // Création de l'élément
    const div = document.createElement("div");
    const info = document.createElement("span");
    const p = document.createElement("p");
    const buttons = document.createElement("div");
    const removeImg = document.createElement("img");
    const modifyImg = document.createElement("img");

    if (window.matchMedia("(prefers-color-scheme: dark)").matches)
        removeImg.src = window.deleteDarkIcon;
    else
        removeImg.src = window.deleteLightIcon
    if (window.matchMedia("(prefers-color-scheme: dark)").matches)
        modifyImg.src = window.modifyDarkIcon;
    else
        modifyImg.src = window.modifyLightIcon;

    info.classList.add("hidden");
    info.setAttribute("code", code);
    info.setAttribute("minute_number", null);
    info.setAttribute("match_minute", null);
    info.setAttribute("team", null);
    info.setAttribute("player", null);
    info.setAttribute("offending_player", null);
    info.setAttribute("victim_player", null);
    info.setAttribute("out_player", null);
    info.setAttribute("in_player", null);
    info.setAttribute("detail", null);
    info.setAttribute("match", matchId);
    p.appendChild(document.createElement("span"));
    p.textContent = name;
    p.name = name;
    removeImg.alt = "Icone de suppression";
    modifyImg.alt = "Icone de modification";
    div.appendChild(info);
    div.appendChild(p);
    buttons.appendChild(modifyImg);
    buttons.appendChild(removeImg);
    div.appendChild(buttons);

    // Ajout des évènements de modification et suppression de l'évènement
    removeImg.addEventListener("click", () =>
    {
        if (window.DEBUG)
            console.log(`[Element] createElement - Suppression de l'évènement : ${p.textContent}`);

        const eventSelected = document.getElementById("event-selected");
        if (eventSelected.querySelector("p").textContent == info.getAttribute("id"))
            eventSelected.classList.add("hidden");
        div.remove();
        socket.emit("deleteEvent", info.getAttribute("id"));
    });
    modifyImg.addEventListener("click", () =>
    {
        if (window.DEBUG)
            console.log(`[Element] Modification de l'évènement : ${p.textContent}`);

        const eventSelected = document.getElementById("event-selected");
        eventSelected.classList.remove("hidden");

        const h3 = eventSelected.querySelector("h3");
        const idEventSelected = eventSelected.querySelector("p");

        h3.textContent = p.textContent;
        idEventSelected.textContent = info.getAttribute("id");

        undisplayEventInformation();

        // Afficher les champs dynamiques
        for (const category of JSON.parse(window.configInformation))
        {
            const foundEvent = category.event.find(e => e.name === p.name);
            if (foundEvent)
            {
                for (const field of foundEvent.data)
                    displayEventInformation(field);
            }
        }

        const bindInput = (name, attr) =>
        {
            const input = eventSelected.querySelector(`input[name='${name}']`);
            if (!input)
                return ;

            // Définir valeur par défaut si elle existe
            const value = info.getAttribute(attr);
            if (value !== null)
                input.value = value;

            // Update du span au changement
            input.oninput = () =>
            {
                info.setAttribute(attr, input.value);
                if (info.getAttribute("match_minute") != "null")
                {
                    const event = document.querySelector(`#event-list span[id='${info.getAttribute("id")}']`).nextElementSibling;
                    event.textContent = `${info.getAttribute("match_minute")}' ${event.name}`;
                }
            };
        };

        bindInput("Timestamp", "ts");
        bindInput("Minute de jeu", "match_minute");
        bindInput("Nombre de minutes", "minute_number");
        bindInput("Cause", "detail");

        const bindSelect = (name, attr, optionAttr) =>
        {
            const select = eventSelected.querySelector(`select[name='${name}']`);
            if (!select)
                return ;

            const value = info.getAttribute(attr);

            // Définir valeur par défaut si elle existe
            if (value !== null)
            {
                const option = select.querySelector(`option[${optionAttr}='${value}']`);
                if (option)
                    select.value = option.value;
            }

            // Update du span au changement
            select.onchange = () =>
            {
                const selectedOption = select.options[select.selectedIndex];
                if (selectedOption)
                {
                    info.setAttribute(attr, selectedOption.getAttribute(optionAttr));
                }
            };
        };

        bindSelect("Équipe", "team", "teamId");
        bindSelect("Joueur", "player", "playerId");
        bindSelect("Joueur fautif", "offending_player", "playerId");
        bindSelect("Joueur victime", "victim_player", "playerId");
        bindSelect("Joueur sortant", "out_player", "playerId");
        bindSelect("Joueur entrant", "in_player", "playerId");
    });

    return div;
}



/**
 * @brief Affiche un champ d'information d'évènement.
 *
 * @param {string} info Le type d'information.
 */
function displayEventInformation(info)
{
    switch (info)
    {
        case "Timestamp":
            document.querySelector("input[name='Timestamp']").parentElement.classList.remove("hidden");
            break;

        case "Minute de jeu":
            document.querySelector("input[name='Minute de jeu']").parentElement.classList.remove("hidden");
            break;

        case "Équipe":
            document.querySelector("select[name='Équipe']").classList.remove("hidden");
            break;

        case "Joueur":
            document.querySelector("select[name='Joueur']").classList.remove("hidden");
            break;

        case "Joueur fautif":
            document.querySelector("select[name='Joueur fautif']").classList.remove("hidden");
            break;

        case "Joueur sortant":
            document.querySelector("select[name='Joueur sortant']").classList.remove("hidden");
            break;

        case "Joueur entrant":
            document.querySelector("select[name='Joueur entrant']").classList.remove("hidden");
            break;

        case "Joueur victime":
            document.querySelector("select[name='Joueur victime']").classList.remove("hidden");
            break;

        case "Cause":
            document.querySelector("input[name='Cause']").parentElement.classList.remove("hidden");
            break;

        default:
            if (window.DEBUG)
                console.log(`[Element] createEventInformation - Information '${info}' inconnu`);
            break;
    }

    return ;
}



/**
 * @brief Supprime l'affichage des champs d'information d'évènement.
 */
function undisplayEventInformation()
{
    document.querySelector("input[name='Timestamp']").parentElement.classList.add("hidden");
    document.querySelector("input[name='Minute de jeu']").parentElement.classList.add("hidden");
    document.querySelector("select[name='Équipe']").classList.add("hidden");
    document.querySelector("select[name='Joueur']").classList.add("hidden");
    document.querySelector("select[name='Joueur fautif']").classList.add("hidden");
    document.querySelector("select[name='Joueur sortant']").classList.add("hidden");
    document.querySelector("select[name='Joueur entrant']").classList.add("hidden");
    document.querySelector("select[name='Joueur victime']").classList.add("hidden");
    document.querySelector("input[name='Cause']").parentElement.classList.add("hidden");

    return ;
}
