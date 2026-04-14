##
# @file routes.py
#
# @brief Enregistrement des routes HTTP et des gestionnaires d'erreurs Flask.
#
# Déclare toutes les pages web du dashboard et les pages d'erreur HTTP standard (400, 401, 403, 404, 408, 500).
##


# =============================================================================
#  Import des bibliothèques
# =============================================================================

from flask import render_template

from Server.Config.setting import Config
from Server.Utils.data import getColorOfSupporter, getColorOfStadiumBleacher
from Server.Utils.logger import Logger

# =============================================================================
#  Création du logger
# =============================================================================

logger = Logger("Serveur/Routes")

# =============================================================================
#  Enregistrement des routes
# =============================================================================

def registerRoutes(app, supporterList, stadiumBleacherList):
    ##
    # @brief Enregistre toutes les routes HTTP et les gestionnaires d'erreurs sur l'application Flask.
    #
    # @param app                 Instance Flask de l'application.
    # @param supporterList       Liste partagée des objets Supporter actifs.
    # @param stadiumBleacherList Liste partagée des objets StadiumBleacher actifs.
    ##

    logger.info("[Routes] Enregistrement des routes et gestionnaires d'erreurs")

# =============================================================================
#  Pages principales
# =============================================================================

    @app.route("/")
    def index():
        ##
        # @brief Page d'accueil : liste tous les supporters actifs.
        ##
        return render_template("Dashboard/index.html", debug=int(Config.DEBUG))


    @app.route("/supporter/<int:supporter_id>")
    def supporterPage(supporter_id):
        ##
        # @brief Page de détail d'un supporter.
        #
        # @param supporter_id Identifiant du supporter extrait de l'URL. Le type <int:…> garantit la conversion automatique par Flask et la compatibilité avec supporter.getId().
        ##

        for supporter in supporterList:
            if supporter.getId() == supporter_id:
                return render_template(
                    "Dashboard/supporter.html",
                    debug=int(Config.DEBUG),
                    id=supporter.getId(),
                    name=supporter.getName(),
                    color=getColorOfSupporter(supporter.getId()),
                    sensorDelay=Config.SENSOR_DELAY
                )

        return render_template("Dashboard/supporter.html", debug=int(Config.DEBUG)), 404


    @app.route("/stadiumBleacher/<int:stadium_bleacher_id>")
    def stadiumBleacherPage(stadium_bleacher_id):
        ##
        # @brief Page de détail d'une tribune.
        #
        # @param stadium_bleacher_id Identifiant de la tribune extrait de l'URL. Le type <int:…> garantit la conversion automatique par Flask et la compatibilité avec stadiumBleacher.getId().
        ##

        for stadiumBleacher in stadiumBleacherList:
            if stadiumBleacher.getId() == stadium_bleacher_id:
                return render_template(
                    "Dashboard/stadiumBleacher.html",
                    debug=int(Config.DEBUG),
                    id=stadiumBleacher.getId(),
                    name=stadiumBleacher.getName(),
                    color=getColorOfStadiumBleacher(stadiumBleacher.getId()),
                    sensorDelay=Config.SENSOR_DELAY
                )

        return render_template("Dashboard/stadiumBleacher.html", debug=int(Config.DEBUG)), 404


    @app.route("/comparison/<string:type>/<string:data>")
    def comparisonPage(type, data):
        ##
        # @brief Page de comparaison des données de tous les supporters ou toutes les tribunes du stade.
        #
        # @param type Type de comparaison extrait de l'URL. Le type <string:…> garantit la convertion automatique par Flask.
        # @param data Type de données extrait de l'URL. Le type <string:…> garantit la convertion automatique par Flask.
        ##

        return render_template("Dashboard/comparison.html", debug=int(Config.DEBUG), color="black", sensorDelay=Config.SENSOR_DELAY, data=data, type=type)

# =============================================================================
#  Pages de contrôle
# =============================================================================

    @app.route("/event")
    def eventPage():
        ##
        # @brief Page de conrôle des évènements.
        ##

        return render_template("Control/event.html", debug=int(Config.DEBUG))


    @app.route("/event/preparation")
    def preparationPage():
        ##
        # @brief Page de préparation d'avant match.
        ##

        return render_template("Control/preparation.html", debug=int(Config.DEBUG))

# =============================================================================
#  Gestionnaires d'erreurs HTTP
# =============================================================================

    @app.errorhandler(400)
    def badRequest(error):
        return render_template("Control/error.html", code=400), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template("Control/error.html", code=401), 401

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("Control/error.html", code=403), 403

    @app.errorhandler(404)
    def pageNotFound(error):
        return render_template("Control/error.html", code=404), 404

    @app.errorhandler(408)
    def timeout(error):
        return render_template("Control/error.html", code=408), 408

    @app.errorhandler(500)
    def internalError(error):
        return render_template("Control/error.html", code=500), 500
