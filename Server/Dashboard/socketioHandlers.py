##
# @file socketioHandlers.py
#
# @brief Enregistrement des gestionnaires d'événements SocketIO du dashboard.
#
# Déclare les handlers pour les événements "getSupporter", "getSupporterData" et "getSupporterDataAll" émis par les clients web.
##


# =============================================================================
#  Import des bibliothèques
# =============================================================================

from flask_socketio import emit

from Server.Config.setting import Config
from Server.Utils.data import createDataForClient, getNameOfSupporter, getColorOfSupporter

# =============================================================================
#  Enregistrement des gestionnaires SocketIO
# =============================================================================

def registerSocketioHandlers(socketio, supporterList):
    ##
    # @brief Enregistre tous les gestionnaires d'événements SocketIO.
    #
    # @param socketio      Instance SocketIO de l'application.
    # @param supporterList Liste partagée des objets Supporter actifs.
    ##

# =============================================================================
#  Liste des supporters
# =============================================================================

    @socketio.on("getSupporter")
    def handleGetSupporter():
        ##
        # @brief Envoie la liste de tous les supporters actifs au client.
        ##

        if Config.DEBUG:
            print("[SocketIO] Réception de 'getSupporter'")

        payload = [{"id": s.supporterId, "name": s.name, "color": getColorOfSupporter(s.supporterId)} for s in supporterList]
        socketio.emit("getSupporterResponse", payload)

# =============================================================================
#  Données d'un supporter spécifique
# =============================================================================

    @socketio.on("getSupporterData")
    def handleGetSupporterData(supporterId):
        ##
        # @brief Envoie les données complètes d'un supporter (heartRate,
        #        average, minimum, maximum).
        #
        # @param supporterId Identifiant du supporter demandé.
        ##

        if Config.DEBUG:
            print(f"[SocketIO] Réception de 'getSupporterData' pour le supporter id={supporterId}")

        name  = getNameOfSupporter(supporterId)
        color = getColorOfSupporter(supporterId)

        for supporter in supporterList:
            if supporter.getId() == int(supporterId):
                payload = createDataForClient(supporterId, name, color, supporter.heartRate.getHeartRate())
                payload.update({
                    "average": supporter.heartRate.getAverage(),
                    "minimum": supporter.heartRate.getMinimum(),
                    "maximum": supporter.heartRate.getMaximum(),
                })
                socketio.emit("getSupporterDataResponse", payload)
                return

        if Config.DEBUG:
            print(f"[SocketIO] Aucun supporter trouvé avec l'id={supporterId}")

# =============================================================================
#  Données de tous les supporters
# =============================================================================

    @socketio.on("getSupporterDataAll")
    def handleGetSupporterDataAll():
        ##
        # @brief Envoie la liste des dernières fréquences cardiaques de tous les supporters actifs.
        ##

        if Config.DEBUG:
            print("[SocketIO] Réception de 'getSupporterDataAll'")

        payload = []
        for supporter in supporterList:
            name  = getNameOfSupporter(supporter.getId())
            color = getColorOfSupporter(supporter.getId())
            data  = createDataForClient(supporter.getId(), name, color, supporter.heartRate.getHeartRate())
            payload.append(data)

        socketio.emit("getSupporterDataAllResponse", payload)
