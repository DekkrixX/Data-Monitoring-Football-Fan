##
# @file event.py
#
# @brief Gestion des évènements.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

import json
import os
from datetime import datetime

from Server.Config.setting import Config
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/Event")

# =============================================================================
#  Configuration
# =============================================================================

##
# @brief Charge une configuration de contôle d'évènement.
#
# @param config Le nom de la configuration à charger.
#
# @return La configuration de contrôle d'évènement.
##
def loadConfiguration(config):
    filePath = Config.PATH["data"] + "Event-Configuration/" + config + ".json"

    try:
        logger.info(f"[Event] Lecture du fichier de configuration : '{filePath}'")

        with open(filePath, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        message = f"[Event] Fichier de configuration introuvable : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message)

    except json.JSONDecodeError as e:
        message = f"[Event] Fichier de configuration invalide (JSON malformé) : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message) from e

    return ""



##
# @brief Charge les information des configurations de contôle d'évènement.
#
# @return Les information des configurations de contrôle d'évènement.
##
def loadConfigurationInformation():
    filePath = Config.PATH["data"] + "event.json"

    try:
        logger.info(f"[Event] Lecture du fichier d'information des configuration : '{filePath}'")

        with open(filePath, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        message = f"[Event] Fichier d'information des configuration introuvable : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message)

    except json.JSONDecodeError as e:
        message = f"[Event] Fichier d'information des configuration invalide (JSON malformé) : '{filePath}'"
        logger.error(message)
        raise RuntimeError(message) from e

    return ""



##
# @brief Renvoi la liste des configurations de contrôle d'évènement.
#
# @return La liste des configurations de contrôle d'évènement.
##
def getConfigurationList():
	configurationList = []
	
	for file in os.listdir(Config.PATH["data"] + "Event-Configuration"):
		config = loadConfiguration(file.replace(".json", ""))
		configurationList.append(config["name"])

	logger.info(f"[Event] Liste des configuration: {configurationList}")

	return configurationList



##
# @brief Créer une nouvelle configuration d'évènement.
#
# @param confg            Nouvelle configuration à créé.
# @param matchInformation Enregistre des informations d'avant match.
#
# @return True si la nouvelle configuration à été créé.
# @retrun False sinon.
##
def createNewEventConfiguration(config, matchInfomation):
    configurationList = getConfigurationList()

    name = json.loads(config)["name"]
    for configuration in configurationList:
        if configuration == name:
            return False

    logger.info(f"[Event] Configuration à sauvegarder: {config}")

    filePath = Config.PATH["data"] + "Event-Configuration/" + name + ".json"
    with open(filePath, 'w') as f:
        f.write(config)

    matchInfomation["config"] = name;

    return True

# =============================================================================
#  Données d'avant match
# =============================================================================

##
# @brief Charge les informations d'avant match.
#
# @param postgresqlClient Client PostgreSQL.
#
# @return Les informations d'avant match et si les dernières informatons sont valide.
##
def loadMatchInformation(postgresqlClient):
    matchId = postgresqlClient.fetch("SELECT id FROM match ORDER BY ts DESC LIMIT 1")
    if matchId:
        matchId = matchId[0]["id"]
        event = postgresqlClient.fetch("SELECT code FROM event WHERE match = %s ORDER BY ts DESC LIMIT 1", (matchId,))
        lastInformation = True if not event or event[0]["code"] != 12 else False
    if not matchId or not lastInformation:
        # Création d'un nouveaux match
        matchId = postgresqlClient.execute("INSERT INTO match (ts) VALUES (%s) RETURNING id", (datetime.now().strftime("%Y/%m/%d %H:%M:%S"),), returning=True)["id"]
        domicileId = postgresqlClient.execute("INSERT INTO team (name) VALUES (NULL) RETURNING id", returning=True)["id"]
        exterieurId = postgresqlClient.execute("INSERT INTO team (name) VALUES (NULL) RETURNING id", returning=True)["id"]
        domicilePlayerId = []
        for _ in range(20):
            domicilePlayerId.append(postgresqlClient.execute("INSERT INTO player (name) VALUES (NULL) RETURNING id", returning=True)["id"])
        exterieurPlayerId = []
        for _ in range(20):
            exterieurPlayerId.append(postgresqlClient.execute("INSERT INTO player (name) VALUES (NULL) RETURNING id", returning=True)["id"])
        postgresqlClient.execute("UPDATE match SET domicile = %s, exterieur = %s WHERE id = %s", (domicileId, exterieurId, matchId))
        for idf in domicilePlayerId:
            postgresqlClient.execute("UPDATE player SET team = %s WHERE id = %s", (domicileId, idf))
        for idf in exterieurPlayerId:
            postgresqlClient.execute("UPDATE player SET team = %s WHERE id = %s", (exterieurId, idf))
        lastInformation = False;

    matchInformation = {"domicile": {"player": []}, "exterieur": {"player": []}}
    matchInformation["id"] = matchId
    config = postgresqlClient.fetch("SELECT config FROM match WHERE id = %s", (matchId,))
    matchInformation["config"] = config[0]["config"] if config and config[0]["config"] else "Default"
    stadium = postgresqlClient.fetch("SELECT stadium FROM match WHERE id = %s", (matchId,))
    matchInformation["stadium"] = stadium[0]["stadium"]
    domicileTeam = postgresqlClient.fetch("SELECT team.name, team.id FROM team, match WHERE match.id = %s AND match.domicile = team.id", (matchId,))
    matchInformation["domicile"]["team"] = domicileTeam[0]["name"]
    matchInformation["domicile"]["id"] = domicileTeam[0]["id"]
    domicileCoach = postgresqlClient.fetch("SELECT team.coach FROM team, match WHERE match.id = %s AND match.domicile = team.id", (matchId,))
    matchInformation["domicile"]["coach"] = domicileCoach[0]["coach"]
    exterieurTeam = postgresqlClient.fetch("SELECT team.name, team.id FROM team, match WHERE match.id = %s AND match.exterieur = team.id", (matchId,))
    matchInformation["exterieur"]["team"] = exterieurTeam[0]["name"]
    matchInformation["exterieur"]["id"] = exterieurTeam[0]["id"]
    exterieurCoach = postgresqlClient.fetch("SELECT team.coach FROM team, match WHERE match.id = %s AND match.exterieur = team.id", (matchId,))
    matchInformation["exterieur"]["coach"] = exterieurCoach[0]["coach"]
    domicilePlayer = postgresqlClient.fetch("SELECT player.name, player.player_number, player.id FROM player, team, match WHERE match.id = %s AND match.domicile = team.id AND team.id = player.team", (matchId,))
    exterieurPlayer = postgresqlClient.fetch("SELECT player.name, player.player_number, player.id FROM player, team, match WHERE match.id = %s AND match.exterieur = team.id AND team.id = player.team", (matchId,))
    for i in range(20):
        matchInformation["domicile"]["player"].append({"name": domicilePlayer[i]["name"], "number": domicilePlayer[i]["player_number"], "id": domicilePlayer[i]["id"]})
    for i in range(20):
        matchInformation["exterieur"]["player"].append({"name": exterieurPlayer[i]["name"], "number": exterieurPlayer[i]["player_number"], "id": exterieurPlayer[i]["id"]})

    logger.info(f"[Event] Chargement des informations du match: {matchInformation}")

    return matchInformation, lastInformation
