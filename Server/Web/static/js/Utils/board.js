/**
 * @file board.js
 *
 * @brief Composants UI et utilitaires graphiques partagés entre les pages.
 *
 * Fournit les fonctions de création des cartes supporter et comparaison affichées sur la page d'accueil, ainsi que la factory createChart() utilisée par les pages supporter et comparaison.
 */

// ============================================================================
//  Carte supporter (page d'accueil)
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
        console.log(`[Board] supporterCard - Création de la carte pour le supporter id=${id} (${name})`);

    // Création de la carte
    const card = document.createElement("div");
    card.id = "s" + id;
    card.classList.add("card");

    // Redirection vers la page de détail du supporter au clic
    card.addEventListener("click", () =>
        {
            if (DEBUG)
                console.log(`[Board] supporterCard - Clic sur la carte du supporter id=${id}, redirection vers /supporter/${id}`);

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
        console.log(`[Board] stadiumBleacherCard - Création de la carte pour la tribune id=${id} (${name})`);

    // Création de la carte
    const card = document.createElement("div");
    card.id = "b" + id;
    card.classList.add("card");

    // Redirection vers la page de détail de la tribune au clic
    card.addEventListener("click", () =>
        {
            if (DEBUG)
                console.log(`[Board] stadiumBleacherCard - Clic sur la carte du supporter id=${id}, redirection vers /stadiumBleacher/${id}`);

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

// ============================================================================
//  Carte comparaison (page d'accueil)
// ============================================================================

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
        console.log("[Board] comparisonCard - Création de la carte de comparaison");

    // Création de la carte
    const card = document.createElement("div");
    card.id = "comparison" + type;
    card.classList.add("card");

    // Redirection vers la page de comparaison au clic
    card.addEventListener("click", () =>
        {
            if (DEBUG)
                console.log("[Board] comparisonCard - Clic sur la carte de comparaison, redirection vers /comparison");

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

// ============================================================================
//  Création du graphique Chart.js
// ============================================================================

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
        console.log(`[Board] createChart - Création du graphique avec ${list.length} dataset(s)`);

    // Construction des datasets à partir de la liste fournie
    const datasetList = list.map((element) =>
        {
            if (window.DEBUG)
                console.log(`[Board] createChart - Dataset: label='${element.title}', color='${element.color}'`);

            return {
                label:           element.title,
                data:            [],
                borderColor:     element.color,
                backgroundColor: element.color + "33", // Couleur de fond avec opacité 20%
                fill:            true,
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
        console.log("[Board] createChart - Graphique créé");

    return chart;
}
