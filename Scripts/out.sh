##
# @file out.sh
#
# @brief Module d'affichage de message sur la sortie d'erreur.
##

# =============================================================================
#  Code de couleur ANSI
# =============================================================================

_RESET="\033[1;0m"    ##< @brief Réinitialise le style et la couleur du texte.
_BLACK="\033[1;30m"   ##< @brief Texte noir.
_RED="\033[1;31m"     ##< @brief Texte rouge.
_GREEN="\033[1;32m"   ##< @brief Texte vert.
_YELLOW="\033[1;33m"  ##< @brief Texte jaune.
_BLUE="\033[1;34m"    ##< @brief Texte bleu.
_MAGENTA="\033[1;35m" ##< @brief Texte magenta.
_CYAN="\033[1;36m"    ##< @brief Texte cyan.
_GRAY="\033[1;37m"    ##< @brief Texte gris clair.
_WHITE="\033[1m"      ##< @brief Texte blanc.
_DIM="\033[2m"

# =============================================================================
#  Fonction métier
# =============================================================================

##
# @brief Affiche un message de debug.
#
# @brief message Message de debug.
##
function debug()
{
    local message="${1}"

    if [ "${VERBOSE}" -eq 1 ]
    then
        echo -e "${_WHITE}[DEBUG] ${message}${_RESET}" >&2
    fi

    return
}


##
# @brief Affiche un message d'information
#
# @param message Message d'information
##
function info()
{
    local message="${1}"

    echo -e "${_CYAN}[INFO] ${message}${_RESET}" >&2

    return
}


##
# @brief Affiche un message d'avertissement.
#
# @param message Message d'avertissement.
##
function warning()
{
    local message="${1}"

    echo -e "${_YELLOW}[AVERTISSEMENT] ${message}${_RESET}" >&2

    return
}


##
# @brief Affiche un message d'erreur et termine le programme avec un code d'erreur.
#
# @param code    Code d'erreur.
# @param message Message d'erreur.
##
function error()
{
    local code="${1}"
    local message="${2}"

    echo -e "${_RED}[ERREUR:${code}] ${message}${_RESET}" >&2

    exit "${code}"
}
