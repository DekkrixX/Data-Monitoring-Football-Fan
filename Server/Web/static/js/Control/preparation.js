/**
 * @file preparation.js
 * 
 * @brief Logique de la page de préparation d'avant match.
 * 
 * Ajoute un écouteur d'évènements sur le select pour la création d'une nouvelle configuration.
 */

let timeout;
const socket = io();

// Ajout d'un écouteur de changement
const select = document.getElementById("config");
select.addEventListener("change", () => 
{
	if (window.DEBUG)
		console.log(`[Preparation] Changement de configuration: ${select.value}`);
	
	// Redirection vers la création d'une nouvelle configuration
	if (select.value === "Nouvelle configuration")
		window.location.href = "/event/configuration";
});

// Mise à jour du match
document.addEventListener("DOMContentLoaded", () =>
{
    const domicileTeam = document.querySelector("#domicile input[name='team']");
    const exterieurTeam = document.querySelector("#exterieur input[name='team']");
    const matchInput = document.querySelector("#match input[name='match']");

    function updateMatchName()
    {
        const domicile = domicileTeam.value || "";
        const exterieur = exterieurTeam.value || "";

        matchInput.value = `${domicile} - ${exterieur}`;

        if (window.DEBUG)
        	console.log(`[Preparation] Mise à jour du match: ${matchInput.value}`);

        return ;
    }

    // Écoute les changements sur les deux inputs
    domicileTeam.addEventListener("input", updateMatchName);
    exterieurTeam.addEventListener("input", updateMatchName);

    // Initialisation
    updateMatchName();
});



// Envoi des données d'avant match
document.addEventListener("DOMContentLoaded", () =>
{
    const inputs = document.querySelectorAll("input, select");

    inputs.forEach(input =>
    {
        input.addEventListener("input", autoSend);
        input.addEventListener("change", autoSend);
    });
});



/**
 * @brief Récupération des informations d'avant match.
 */
function getMatchInformation()
{
    const domicileForm = document.getElementById("domicile");
    const exterieurForm = document.getElementById("exterieur");
    const matchForm = document.getElementById("match");

    function getTeamData(form)
    {
        const data =
        {
            team: form.querySelector("input[name='team']").value,
            coach: form.querySelector("input[name='coach']").value,
            player: []
        };

        for (let i = 0; i <= 19; i++)
        {
            const name = form.querySelector(`input[name='player${i}']`).value;
            const number = form.querySelector(`input[name='numero${i}']`).value;

            data.player.push({name: name, number: number});
        }

        return data;
    }

    const matchInformation = 
    {
        domicile: getTeamData(domicileForm),
        exterieur: getTeamData(exterieurForm),
        stadium: matchForm.querySelector("input[name='stadium']").value,
        config: matchForm.querySelector("#config").value
    };

    return matchInformation;
}



/**
 * @brief Envoi automatique des données
 */
function autoSend()
{
    clearTimeout(timeout);

    timeout = setTimeout(() => 
    {
        const data = JSON.stringify(getMatchInformation(), null, 4);

        socket.emit("matchInformation", data);

        if (window.DEBUG)
            console.log("Infomation du match envoyé :", data);
    }, 500);

    return ;
}
