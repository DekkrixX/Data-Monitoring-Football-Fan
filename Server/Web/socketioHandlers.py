##
# @file socketioHandlers.py
#
# @brief Enregistrement des gestionnaires d'événements SocketIO de l'interface web.
#
# Déclare les handlers pour les événements "getSupporter", "getSupporterData" et "getSupporterDataAll" émis par les clients web.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

import json
from flask_socketio import emit
from datetime import datetime, timedelta

from Server.Config.setting import Config
from Server.Utils.data import createSupporterHeartRateForClient, getNameOfSupporter, getColorOfSupporter, createStadiumBleacherAccelerometerForClient, createStadiumBleacherAcousticForClient, getNameOfStadiumBleacher, getColorOfStadiumBleacher
from Server.Utils.event import createNewEventConfiguration
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/SocketIO")

# =============================================================================
#  Enregistrement des gestionnaires SocketIO
# =============================================================================

##
# @brief Enregistre tous les gestionnaires d'événements SocketIO.
#
# @param socketio            Instance SocketIO de l'application.
# @param supporterList       Liste partagée des objets Supporter actifs.
# @param stadiumBleacherList Liste partagée des objets StadiumBleacher actifs.
# @param postgresqlClient    Client PosgreSQL.
##
def registerSocketioHandlers(socketio, supporterList, stadiumBleacherList, postgresqlClient):

# =============================================================================
#  Liste des supporters
# =============================================================================

    ##
    # @brief Envoie la liste de tous les supporters actifs au client.
    ##
    @socketio.on("getSupporter")
    def handleGetSupporter():
        logger.info("[SocketIO] Réception de 'getSupporter'")

        payload = [{"id": s.supporterId, "name": s.name, "color": getColorOfSupporter(s.supporterId)} for s in supporterList]
        socketio.emit("getSupporterResponse", payload)

        return

# =============================================================================
#  Données d'un supporter spécifique
# =============================================================================

    ##
    # @brief Envoie les données complètes d'un supporter (heartRate, average, minimum, maximum).
    #
    # @param supporterId Identifiant du supporter demandé.
    ##
    @socketio.on("getSupporterHeartRate")
    def handleGetSupporterHeartRate(supporterId):
        logger.info(f"[SocketIO] Réception de 'getSupporterHeartRate' pour le supporter id={supporterId}")

        name  = getNameOfSupporter(supporterId)
        color = getColorOfSupporter(supporterId)

        for supporter in supporterList:
            if supporter.getId() == int(supporterId):
                payload = createSupporterHeartRateForClient(supporterId, name, color, supporter.heartRate.getHeartRate())
                payload.update({
                    "average": supporter.heartRate.getAverage(),
                    "minimum": supporter.heartRate.getMinimum(),
                    "maximum": supporter.heartRate.getMaximum(),
                })
                socketio.emit("getSupporterHeartRateResponse", payload)
                return

        logger.warning(f"[SocketIO] Aucun supporter trouvé avec l'id={supporterId}")

        return

# =============================================================================
#  Données de tous les supporters
# =============================================================================

    ##
    # @brief Envoie la liste des dernières fréquences cardiaques de tous les supporters actifs.
    ##
    @socketio.on("getSupporterHeartRateAll")
    def handleGetSupporterHeartRateAll():
        logger.info("[SocketIO] Réception de 'getSupporterHeartRateAll'")

        payload = []
        for supporter in supporterList:
            name  = getNameOfSupporter(supporter.getId())
            color = getColorOfSupporter(supporter.getId())
            data  = createSupporterHeartRateForClient(supporter.getId(), name, color, supporter.heartRate.getHeartRate())
            payload.append(data)

        socketio.emit("getSupporterHeartRateAllResponse", payload)

        return

# =============================================================================
#  Liste des tribunes
# =============================================================================

    ##
    # @brief Envoie la liste de toutes les tribunes actives au client.
    ##
    @socketio.on("getStadiumBleacher")
    def handleGetStadiumBleacher():
        logger.info("[SocketIO] Réception de 'getStadiumBleacher'")

        payload = [{"id": b.stadiumBleacherId, "name": b.name, "color": getColorOfSupporter(b.stadiumBleacherId)} for b in stadiumBleacherList]
        socketio.emit("getStadiumBleacherResponse", payload)

        return

# =============================================================================
#  Données d'une tribune spécifique
# =============================================================================

    ##
    # @brief Envoie les données complètes d'une tribune (accelerometer, average, minimum, maximum).
    #
    # @param stadiumBleacherId Identifiant de la tribune demandé.
    ##
    @socketio.on("getStadiumBleacherAccelerometer")
    def handleGetStadiumBleacherAccelerometer(stadiumBleacherId):
        logger.info(f"[SocketIO] Réception de 'getStadiumBleacherAccelerometer' pour la tribune id={stadiumBleacherId}")

        name  = getNameOfStadiumBleacher(stadiumBleacherId)
        color = getColorOfStadiumBleacher(stadiumBleacherId)

        for stadiumBleacher in stadiumBleacherList:
            if stadiumBleacher.getId() == int(stadiumBleacherId):
                payload = createStadiumBleacherAccelerometerForClient(stadiumBleacherId, name, color, stadiumBleacher.accelerometer.getAccelerometer())
                payload.update({
                    "average": stadiumBleacher.accelerometer.getAverage(),
                    "minimum": stadiumBleacher.accelerometer.getMinimum(),
                    "maximum": stadiumBleacher.accelerometer.getMaximum(),
                })
                socketio.emit("getStadiumBleacherAccelerometerResponse", payload)
                return

        logger.warning(f"[SocketIO] Aucune tribune trouvé avec l'id={stadiumBleacherId}")

        return



    ##
    # @brief Envoie les données complètes d'une tribune (acoustic, average, minimum, maximum).
    #
    # @param stadiumBleacherId Identifiant de la tribune demandé.
    ##
    @socketio.on("getStadiumBleacherAcoustic")
    def handleGetStadiumBleacherAcoustic(stadiumBleacherId):
        logger.info(f"[SocketIO] Réception de 'getStadiumBleacherAcoustic' pour la tribune id={stadiumBleacherId}")

        name  = getNameOfStadiumBleacher(stadiumBleacherId)
        color = getColorOfStadiumBleacher(stadiumBleacherId)

        for stadiumBleacher in stadiumBleacherList:
            if stadiumBleacher.getId() == int(stadiumBleacherId):
                payload = createStadiumBleacherAcousticForClient(stadiumBleacherId, name, color, stadiumBleacher.acoustic.getAcoustic())
                payload.update({
                    "average": stadiumBleacher.acoustic.getAverage(),
                    "minimum": stadiumBleacher.acoustic.getMinimum(),
                    "maximum": stadiumBleacher.acoustic.getMaximum(),
                })
                socketio.emit("getStadiumBleacherAcousticResponse", payload)
                return

        logger.warning(f"[SocketIO] Aucune tribune trouvé avec l'id={stadiumBleacherId}")

        return

# =============================================================================
#  Données de toutes les tribunes
# =============================================================================

    ##
    # @brief Envoie la liste des dernières mesure de l'accéléromètre de toutes les tribunes actives.
    ##
    @socketio.on("getStadiumBleacherAccelerometerAll")
    def handleGetStadiumBleacherAccelerometerAll():
        logger.info("[SocketIO] Réception de 'getStadiumBleacherAccelerometerAll'")

        payload = []
        for stadiumBleacher in stadiumBleacherList:
            name  = getNameOfStadiumBleacher(stadiumBleacher.getId())
            color = getColorOfStadiumBleacher(stadiumBleacher.getId())
            data  = createStadiumBleacherAccelerometerForClient(stadiumBleacher.getId(), name, color, stadiumBleacher.accelerometer.getAccelerometer())
            payload.append(data)

        socketio.emit("getStadiumBleacherAccelerometerAllResponse", payload)

        return



    ##
    # @brief Envoie la liste des dernières mesure acoustique de toutes les tribunes actives.
    ##
    @socketio.on("getStadiumBleacherAcousticAll")
    def handleGetStadiumBleacherAcousticAll():
        logger.info("[SocketIO] Réception de 'getStadiumBleacherAcousticAll'")

        payload = []
        for stadiumBleacher in stadiumBleacherList:
            name  = getNameOfStadiumBleacher(stadiumBleacher.getId())
            color = getColorOfStadiumBleacher(stadiumBleacher.getId())
            data  = createStadiumBleacherAcousticForClient(stadiumBleacher.getId(), name, color, stadiumBleacher.acoustic.getAcoustic())
            payload.append(data)

        socketio.emit("getStadiumBleacherAcousticAllResponse", payload)

        return

# =============================================================================
#  Données d'avant match
# =============================================================================
    
    ##
    # @brief Réception des infomations d'avant match
    #
    # @param data  Informations d'avant match.
    ##
    @socketio.on("matchInformation")
    def handleMatchInformation(data):
        logger.info("[SocketIO] Réception de 'matchInformation'")
        logger.info(f"[SocketIO] Mise à jour des données d'avant match : {data}")
        data = json.loads(data)

        for player in data["domicile"]["player"]:
            try:
                player["number"] = int(player["number"])
            except:
                player["number"] = 0
            postgresqlClient.execute("UPDATE player SET team = %s, name = %s, player_number = %s WHERE id = %s", (int(data["domicile"]["id"]), player["name"], player["number"], int(player["id"])))
        for player in data["exterieur"]["player"]:
            try:
                player["number"] = int(player["number"])
            except:
                player["number"] = 0
            postgresqlClient.execute("UPDATE player SET team = %s, name = %s, player_number = %s WHERE id = %s", (int(data["exterieur"]["id"]), player["name"], player["number"], int(player["id"])))
        postgresqlClient.execute("UPDATE team SET name = %s, coach = %s WHERE id = %s", (data["domicile"]["team"], data["domicile"]["coach"], int(data["domicile"]["id"])))
        postgresqlClient.execute("UPDATE team SET name = %s, coach = %s WHERE id = %s", (data["exterieur"]["team"], data["exterieur"]["coach"], int(data["exterieur"]["id"])))
        postgresqlClient.execute("UPDATE match SET domicile = %s, exterieur = %s, config = %s, stadium = %s WHERE id = %s", (int(data["domicile"]["id"]), int(data["exterieur"]["id"]), data["config"], data["stadium"], int(data["id"])));

        return



    ##
    # @brief Réception d'une nouvelle configuration d'évènements.
    #
    # @param config Configuration à enregistrer.
    ##
    @socketio.on("saveConfiguration")
    def handleSaveConfiguration(config):
        logger.info("[SocketIO] Réception de 'saveConfiguration'");

        if createNewEventConfiguration(config, matchInformation):
            socketio.emit("getSaveConfiguration");
        else:
            socketio.emit("getSaveConfigurationError");

        return

# =============================================================================
#  Données d'évènements
# =============================================================================

    ##
    # @brief Envoi les données complètes des évènements du match.
    ##
    @socketio.on("getEventAll")
    def handleGetEventAll(matchId):
        logger.info("[SocketIO] Réception de 'getEventAll'")

        events = postgresqlClient.fetch("SELECT * FROM event WHERE match = %s ORDER BY ts", (matchId,))

        for event in events:
            event["ts"] = event["ts"].strftime("%Y/%m/%d %H:%M:%S");

        socketio.emit("getEventAllResponse", events);
        
        return

    ##
    # @brief Réception d'un nouvel évènement.
    ##
    @socketio.on("newEvent")
    def handleNewEvent(code, matchId):
        logger.info(f"[SocketIO] Réception de 'newEvent': code:{code}, matchId:{matchId}")

        ts = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # Calcul de la minute de jeu
        reference = None
        if code not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 32, 33, 34, 35, 36, 37, 38]:
            events = postgresqlClient.fetch("SELECT code, ts FROM event WHERE match = %s ORDER BY ts DESC", (matchId,))
            for event in events:
                delta = datetime.strptime(ts, "%Y/%m/%d %H:%M:%S") - event["ts"]
                minute =  delta.total_seconds() // 60
                if event["code"] == 7:
                    reference = 106 + minute
                    break
                elif event["code"] == 5:
                    reference = 91 + minute
                    break
                elif event["code"] == 3:
                    reference = 46 + minute
                    break
                elif event["code"] == 1:
                    reference = 1 + minute
                    break

        idf = postgresqlClient.execute("INSERT INTO event (code, ts, match_minute, match) VALUES (%s, %s, %s, %s) RETURNING id", (code, ts, reference, matchId), returning=True)["id"]

        socketio.emit("newEventResponse", {"id": idf, "ts": ts, "match_minute": reference})

        return




    ##
    # @brief Suppression d'un évènement.
    #
    # @param idf Identifiant de l'évènement.
    ##
    @socketio.on("deleteEvent")
    def handleDeleteEvent(idf):
        logger.info(f"[SocketIO] Réception de 'deleteEvent': id:{idf}")

        postgresqlClient.execute("DELETE FROM event WHERE id = %s", (idf,))

        return



    ##
    # @brief Modification d'un évènement.
    #
    # @param idf  Identifiant de l'évènement.
    # @param data Données modifiées.
    ##
    @socketio.on("modifyEvent")
    def handleModifyEvent(idf, data):
        def toInt(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

        logger.info(f"[SocketIO] Réception de 'modifyEvent': id:{idf} données:{data}")
        data = json.loads(data)

        # Vérifie la cohérence entre le timestamp et la minute de jeu
        lastData = postgresqlClient.fetch("SELECT ts, match_minute FROM event WHERE id = %s", (idf,))
        logger.warning(f"{lastData}")
        events = postgresqlClient.fetch("SELECT code, ts FROM event WHERE match = %s ORDER BY ts DESC", (toInt(data["match"]),))

        if lastData[0]["match_minute"] != toInt(data["match_minute"]) and toInt(data["match_minute"]):
            for event in events:
                if event["code"] == 7:
                    data["ts"] = (event["ts"] + timedelta(minutes=toInt(data["match_minute"]) - 106)).strftime("%Y/%m/%d %H:%M:%S")
                    break
                elif event["code"] == 5:
                    data["ts"] = (event["ts"] + timedelta(minutes=toInt(data["match_minute"]) - 91)).strftime("%Y/%m/%d %H:%M:%S")
                    break
                elif event["code"] == 3:
                    data["ts"] = (event["ts"] + timedelta(minutes=toInt(data["match_minute"]) - 46)).strftime("%Y/%m/%d %H:%M:%S")
                    break
                elif event["code"] == 1:
                    data["ts"] = (event["ts"] + timedelta(minutes=toInt(data["match_minute"]) - 1)).strftime("%Y/%m/%d %H:%M:%S")
                    break

        elif lastData[0]["ts"].strftime("%Y/%m/%d %H:%M:%S") != data["ts"]:
            for event in events:
                delta = datetime.strptime(data["ts"], "%Y/%m/%d %H:%M:%S") - event["ts"]
                minute =  delta.total_seconds() // 60
                if event["code"] == 7:
                    data["match_minute"] = 106 + minute
                    break
                elif event["code"] == 5:
                    data["match_minute"] = 91 + minute
                    break
                elif event["code"] == 3:
                    data["match_minute"] = 46 + minute
                    break
                elif event["code"] == 1:
                    data["match_minute"] = 1 + minute
                    break

        logger.warning(f"{data['ts']}")
        logger.warning(f"{data['match_minute']}")

        postgresqlClient.execute("UPDATE event SET ts = %s, minute_number = %s, match_minute = %s, team = %s, player = %s, offending_player = %s, victim_player = %s, out_player = %s, in_player = %s, detail = %s, match = %s WHERE id = %s",(data["ts"], toInt(data["minute_number"]), toInt(data["match_minute"]), toInt(data["team"]), toInt(data["player"]), toInt(data["offending_player"]), toInt(data["victim_player"]), toInt(data["out_player"]), toInt(data["in_player"]), data["detail"], toInt(data["match"]), idf))

        a = postgresqlClient.fetch("SELECT * FROM event WHERE id = %s", (idf,))
        logger.warning(f"{a}")

        socketio.emit("modifyEventResponse", {"id": idf, "ts": data["ts"], "match_minute": data["match_minute"]})

        return



    return
