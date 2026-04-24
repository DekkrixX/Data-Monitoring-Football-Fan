/**
 * @file configuration.js
 * 
 * @brief Logique de la page de configuration du contrôle d'évènement.
 * 
 * Ajoute un écouteur d'évènements sur le bouton de sauvegarde.
 */

const socket = io();

// Ajout d'un écouteur de click
const button = document.getElementById("save");
button.addEventListener("click", (event) =>
{
    event.preventDefault();

    // Créer un objet JSON vide pour la configuration
    const configuration = {
        "name": document.querySelector('input[name="name"]').value, // Récupère le nom de la configuration
        "config": []
    };

    // Récupérer toutes les catégories (div avec classe 'category')
    const categories = document.querySelectorAll('.category');

    categories.forEach((category) =>
    {
        const categoryObj = 
        {
            "category": category.querySelector('h2').textContent, // Récupérer le nom de la catégorie
            "event": [] // Initialiser la liste des événements pour chaque catégorie
        };

        // Récupérer tous les événements dans cette catégorie
        const events = category.querySelectorAll('.event');
        
        events.forEach((eventElement) =>
        {
            const eventObj = 
            {
                "name": eventElement.querySelector('label').textContent, // Récupérer le nom de l'événement
                "code": eventElement.querySelector('input').getAttribute('code'), // Récupérer le code de l'événement via l'attribut 'code'
                "enable": eventElement.querySelector('input').checked // Vérifier si la checkbox est cochée
            };
            categoryObj.event.push(eventObj); // Ajouter l'événement à la catégorie
        });

        configuration.config.push(categoryObj); // Ajouter la catégorie à la configuration
    });

    if (window.DEBUG)
        console.log(`[Configuration] Configuration à sauvegarder: ${JSON.stringify(configuration, null, 4)}`);
    socket.emit("saveConfiguration", JSON.stringify(configuration, null, 4));
});


/**
 * @brief Affiche l'erreur de sauvegarde de la configuration.
 */
socket.on("getSaveConfigurationError", () =>
{
	const p = document.getElementById("error");
	p.classList.remove("hidden");
});



/**
 * @brief Enregistre la sauvegarde de la configuration.
 */
socket.on("getSaveConfiguration", () =>
{
	window.location.href = "/event/preparation";
});


/**
 * @brief Change l'état de span de chechbox.
 * 
 * @param span Le span checkbox.
 */
function toggleCheck(span)
{
    const input = span.previousElementSibling;
    input.checked = !input.checked;
    span.classList.toggle('checked');

    return ;
}

window.toggleCheck = toggleCheck;