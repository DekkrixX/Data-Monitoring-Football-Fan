##
# @file time.py
#
# @brief Utilitaires de manipulation du temps.
#
# Fournit des fonctions de calcul sur les objets Date JavaScript, utilisées pour la gestion des horodatages dans le dashboard.
##

# =============================================================================
#  Import des bibliothèques
# =============================================================================

from datetime import datetime, timedelta

# =============================================================================
#  Fonction
# =============================================================================

##
# @brief Soustrait un nombre de secondes à un objet Date et retourne le résultat en millisecondes depuis l'epoch Unix.
#
# @param time    Objet Date de référence.
# @param seconds Nombre de secondes à soustraire. Doit être positif.
#
# @returns Timestamp en millisecondes correspondant à @p time moins @p seconds secondes.
##
def subtract_seconds(time, seconds):
    result = time - timedelta(seconds=seconds)
    return result