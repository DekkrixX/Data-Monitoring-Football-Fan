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
from Server.Utils.data import createSupporterDataForClient, getNameOfSupporter, getColorOfSupporter
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/SocketIO")

# =============================================================================
#  Enregistrement des gestionnaires SocketIO
# =============================================================================

def registerSocketioHandlers(socketio, supporterList, stadiumBleacherList):
    ##
    # @brief Enregistre tous les gestionnaires d'événements SocketIO.
    #
    # @param socketio      Instance SocketIO de l'application.
    # @param supporterList Liste partagée des objets Supporter actifs.
    # @param stadiumBleacherList Liste partagée des objets StadiumBleacher actifs.
    ##

# =============================================================================
#  Liste des supporters
# =============================================================================

    @socketio.on("getSupporter")
    def handleGetSupporter():
        ##
        # @brief Envoie la liste de tous les supporters actifs au client.
        ##

        logger.info("[SocketIO] Réception de 'getSupporter'")

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

        logger.info(f"[SocketIO] Réception de 'getSupporterData' pour le supporter id={supporterId}")

        name  = getNameOfSupporter(supporterId)
        color = getColorOfSupporter(supporterId)

        for supporter in supporterList:
            if supporter.getId() == int(supporterId):
                payload = createSupporterDataForClient(supporterId, name, color, supporter.heartRate.getHeartRate())
                payload.update({
                    "average": supporter.heartRate.getAverage(),
                    "minimum": supporter.heartRate.getMinimum(),
                    "maximum": supporter.heartRate.getMaximum(),
                })
                socketio.emit("getSupporterDataResponse", payload)
                return

        logger.warning(f"[SocketIO] Aucun supporter trouvé avec l'id={supporterId}")

# =============================================================================
#  Données de tous les supporters
# =============================================================================

    @socketio.on("getSupporterDataAll")
    def handleGetSupporterDataAll():
        ##
        # @brief Envoie la liste des dernières fréquences cardiaques de tous les supporters actifs.
        ##

        logger.info("[SocketIO] Réception de 'getSupporterDataAll'")

        payload = []
        for supporter in supporterList:
            name  = getNameOfSupporter(supporter.getId())
            color = getColorOfSupporter(supporter.getId())
            data  = createSupporterDataForClient(supporter.getId(), name, color, supporter.heartRate.getHeartRate())
            payload.append(data)

        socketio.emit("getSupporterDataAllResponse", payload)

# =============================================================================
#  Liste des tribunes
# =============================================================================

    @socketio.on("getStadiumBleacher")
    def handleGetStadiumBleacher():
        ##
        # @brief Envoie la liste de toutes les tribunes actives au client.
        ##

        logger.info("[SocketIO] Réception de 'getStadiumBleacher'")

        payload = [{"id": b.stadiumBleacherId, "name": b.name, "color": getColorOfSupporter(b.stadiumBleacherId)} for b in stadiumBleacherList]
        socketio.emit("getStadiumBleacherResponse", payload)

# =============================================================================
#  Données d'une tribune spécifique
# =============================================================================

    @socketio.on("getStadiumBleacherData")
    def handleGetStadiumBleacherData(stadiumBleacherId):
        ##
        # @brief Envoie les données complètes d'une tribune (accelerometer,
        #        average, minimum, maximum).
        #
        # @param stadiumBleacherId Identifiant de la tribune demandé.
        ##

        logger.info(f"[SocketIO] Réception de 'getStadiumBleacherData' pour la tribune id={stadiumBleacherId}")

        name  = getNameOfStadiumBleacher(stadiumBleacherId)
        color = getColorOfStadiumBleacher(stadiumBleacherId)

        for stadiumBleacher in stadiumBleacherList:
            if stadiumBleacher.getId() == int(stadiumBleacherId):
                payload = createStadiumBleacherDataForClient(supporterId, name, color, stadiumBleacher.accelerometer.getAccelerometer())
                payload.update({
                    "average": stadiumBleacher.accelerometer.getAverage(),
                    "minimum": stadiumBleacher.accelerometer.getMinimum(),
                    "maximum": stadiumBleacher.accelerometer.getMaximum(),
                })
                socketio.emit("getStadiumBleacherDataResponse", payload)
                return

        logger.warning(f"[SocketIO] Aucune tribune trouvé avec l'id={stadiumBleacherId}")

# =============================================================================
#  Données de toutes les tribunes
# =============================================================================

    @socketio.on("getStadiumBleacherDataAll")
    def handleGetStadiumBleacherDataAll():
        ##
        # @brief Envoie la liste des dernières mesure de l'accéléromètre de toutes les tribunes actives.
        ##

        logger.info("[SocketIO] Réception de 'getStadiumBleacherDataAll'")

        payload = []
        for stadiumBleacher in stadiumBleacherList:
            name  = getNameOfStadiumBleacher(stadiumBleacher.getId())
            color = getColorOfStadiumBleacher(stadiumBleacher.getId())
            data  = createStadiumBleacherDataForClient(stadiumBleacher.getId(), name, color, stadiumBleacher.accelerometer.getAccelerometer())
            payload.append(data)

        socketio.emit("getStadiumBleacherDataAllResponse", payload)
