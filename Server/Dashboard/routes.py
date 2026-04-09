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
from Server.Utils.data import getColorOfSupporter
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

# ==========================================================================
#  Pages principales
# ==========================================================================

    @app.route("/")
    def index():
        ##
        # @brief Page d'accueil : liste tous les supporters actifs.
        ##
        return render_template("index.html", debug=int(Config.DEBUG))


    @app.route("/supporter/<int:supporterId>")
    def supporterPage(supporter_id):
        ##
        # @brief Page de détail d'un supporter.
        #
        # @param supporter_id Identifiant du supporter extrait de l'URL. Le type <int:…> garantit la conversion automatique par Flask et la compatibilité avec supporter.getId().
        ##

        for supporter in supporterList:
            if supporter.getId() == supporterId:
                return render_template(
                    "supporter.html",
                    debug=int(Config.DEBUG),
                    id=supporter.getId(),
                    name=supporter.getName(),
                    color=getColorOfSupporter(supporter.getId())
                )

        return render_template("supporter.html", debug=int(Config.DEBUG)), 404


    @app.route("/stadiumBleacher/<int:stadiumBleacherId>")
    def stadiumBleacherPage(stadiumBleacherId)
        ##
        # @TODO
        ##
        return render_template("stadiumBleacher.html", debug=int(Config.DEBUG)), 404


    @app.route("/comparison")
    def comparisonPage():
        ##
        # @brief Page de comparaison des données de tous les supporters.
        ##
        return render_template("comparison.html", debug=int(Config.DEBUG)), 404


    @app.route("/comparison/stadiumBleacher")
    def comparisonStadiumBleacherPage():
        ##
        # @TODO
        ##
        return render_template("comparisonStadiumBleacher.html", debug=int(Config.DEBUG)), 404

# ==========================================================================
#  Gestionnaires d'erreurs HTTP
# ==========================================================================

    @app.errorhandler(400)
    def badRequest(error):
        return render_template("error.html", code=400), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template("error.html", code=401), 401

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("error.html", code=403), 403

    @app.errorhandler(404)
    def pageNotFound(error):
        return render_template("error.html", code=404), 404

    @app.errorhandler(408)
    def timeout(error):
        return render_template("error.html", code=408), 408

    @app.errorhandler(500)
    def internalError(error):
        return render_template("error.html", code=500), 500
