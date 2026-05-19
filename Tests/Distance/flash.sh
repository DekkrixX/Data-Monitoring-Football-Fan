##
# @file flash.sh
#
# @brief Flash un binaire sur une carte ESP32.
#
# @see out.sh
# @see Fonction usage() ou lancer le script avec --help
##

# =============================================================================
#  Import
# =============================================================================

source "$(dirname "${BASH_SOURCE[0]}")/../../Scripts/out.sh"

# =============================================================================
#  Code de sortie
# =============================================================================

argumentErrorCode=1                ##< @brief Arguments manquants ou invalides.
portNotFoundErrorCode=2            ##< @brief Port série introuvable.

# =============================================================================
#  Flag
# =============================================================================

VERBOSE=0 ##< @brief Mode verbeux (désactivé par défaut, activé par -v / --verbose).

# =============================================================================
#  Variable globale
# =============================================================================

path="$(dirname "${BASH_SOURCE[0]}")/../.." ##< @brief Chemin du projet.

# =============================================================================
#  Fonctions utilitaires
# =============================================================================

##
# @brief Affiche le manuel d'usage du script.
#
# @param name Nom du script.
##
function usage()
{
    local name=$(basename "${0}")

    echo -e "${_WHITE}COMMANDE${_RESET}"
    echo -e "\t${_MAGENTA}${name} <cible>"${_RESET}
    echo ""
    echo -e "${_WHITE}DESCRIPTION${_RESET}"
    echo -e "\tFlash un binaire sur une carte ESP32."
    echo ""
    echo -e "${_WHITE}OPTIONS${_RESET}"
    echo -e "\t-h | --help"
    echo -e "\t\tAffiche cette aide."
    echo -e "\t\tExemple: ${name} --help"
    echo -e "\t-v | --verbose"
    echo -e "\t\tActive les messages de debug détaillés."
    echo -e "\t\tExemple: ${name} --verbose /dev/ttyACM0"
    echo ""
    echo -e "${_WHITE}ARGUMENTS${_RESET}"
    echo -e "\t<port>"
    echo -e "\t\tPort sur lequel la carte est branché."
    echo -e "\t\tExemple: ${name} /dev/ttyACM0"

    return
}

# =============================================================================
#  Point d'entrée du script
# =============================================================================

##
# @brief Parsing des arguments et exécution du script.
#
# @param $@ Tous les arguments du script.
##
function main()
{
    # Affichage de l'aide si demandé
    if [[ "${1}" == "-h" || "${1}" == "--help" ]]
    then
        usage
        exit 0
    fi
    # Parsing de l'option -v/--verbose en première position
    if [ "${1}" = "-v" ] || [ "${1}" = "--verbose" ]
    then
        VERBOSE=1
        debug "Mode verbeux activé."
        shift  # Retire -v/--verbose de la liste des arguments
    fi

    # Vérification du nombre d'arguments
    if [[ "${#}" -ne 1 ]]
    then
        error "${argumentErrorCode}" "Nombre d'arguments insuffisant. Au moins 1 argument est requis: <cible>."
    fi

    local port="${1}"

    # Vérifie l'installation de l'environnement virtuel
    if [ ! -e "${path}/.venv/platformio-env" ]
    then
        info "Installation de l'environnement virtuel 'platformio-env'"
        debug "Package: Python3"
        sudo apt install -y python3
        debug "Package: Python3-venv"
        sudo apt install -y python3-venv
        debug "Création de l'environnement virtuel python"
        mkdir -p "${path}/.venv"
        debug "Environnement virtuel: PlatformIO"
        python3 -m venv "${path}/.venv/platformio-env"
        debug "Package: PlatformIO"
        "${path}"/.venv/platformio-env/bin/pip install platformio
    fi

    # Vérifie que le port série sélectionné est ouvert
    if [ -e "${port}" ]
    then
        debug "Flash du device."

        # Efface la mémoire flash
        "${path}"/.venv/platformio-env/bin/pio run -t erase --upload-port "${port}" --project-dir Tests/Distance
        # Montage du système de fichier LittleFS
        mkdir -p "${path}/Tests/Distance/data"
        "${path}"/.venv/platformio-env/bin/pio run -t uploadfs --upload-port "${port}" --project-dir Tests/Distance
        # Flash de la carte
        "${path}"/.venv/platformio-env/bin/pio run -t upload --upload-port "${port}" --project-dir Tests/Distance
    else
        error "${portNotFoundErrorCode}" "Le port série '${port}' sélectionné n'est pas ouvert."
    fi

    return ;
}

# Lancement du script avec tous les arguments
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
    main "${@}"
fi
