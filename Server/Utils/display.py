##
# @file display.py
#
# @brief Utilitaires d'affichage console.
##


# =============================================================================
#  Affichage
# =============================================================================

def printBanner(title, width=80):
    ##
    # @brief Affiche une bannière encadrée dans la console avec le titre aligné à gauche.
    #
    # @param title Texte à afficher dans la bannière.
    # @param width Largeur totale de la bannière en caractères (défaut : 80).
    ##

    print("╔" + "═" * (width - 2) + "╗")
    print("║" + " " * (width - 2) + "║")
    print("║" + title + " " * ((width - 2) - len(title)) + "║")
    print("║" + " " * (width - 2) + "║")
    print("╚" + "═" * (width - 2) + "╝")
