function newEvent(name, code)
{
	console.log(`[Event] Nouvelle évènement : ${name}`);

	const eventList = document.getElementById("event-list");

	const div = document.createElement("div");
	const p = document.createElement("p");
	p.textContent = name;
	const buttons = document.createElement("div");
	const removeImg = document.createElement("img");
	if (window.matchMedia("(prefers-color-scheme: dark)").matches)
		removeImg.src = window.deleteDarkIcon;
	else
		removeImg.src = window.deleteLightIcon
	removeImg.alt = "Icone de suppression";
	const modifyImg = document.createElement("img");
	if (window.matchMedia("(prefers-color-scheme: dark)").matches)
		modifyImg.src = window.modifyDarkIcon;
	else
		modifyImg.src = window.modifyLightIcon;
	modifyImg.alt = "Icone de modification";
	div.appendChild(p);
	buttons.appendChild(modifyImg);
	buttons.appendChild(removeImg);
	div.appendChild(buttons);

	eventList.appendChild(div);

	return ;
}

window.newEvent = newEvent;