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

from flask_socketio import emit

from Server.Config.setting import Config
from Server.Utils.data import createSupporterHeartRateForClient, getNameOfSupporter, getColorOfSupporter, createStadiumBleacherAccelerometerForClient, createStadiumBleacherAcousticForClient, getNameOfStadiumBleacher, getColorOfStadiumBleacher
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
##
def registerSocketioHandlers(socketio, supporterList, stadiumBleacherList):

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



    return
