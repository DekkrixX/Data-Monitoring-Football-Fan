##
# @file readSerialLog.sh
#
# @brief Lecture et sauvegarde de dumps de logs via port série.
#
# @see out.sh
# @see Fonction usage() ou lancer le script avec --help
##

# =============================================================================
#  Import
# =============================================================================

source "$(dirname "${BASH_SOURCE[0]}")/out.sh"

# =============================================================================
#  Code de sortie
# =============================================================================

argumentErrorCode=1 ##< @brief Arguments manquants ou invalides.

# =============================================================================
#  Flag
# =============================================================================

VERBOSE=0 ##< @brief Mode verbeux (désactivé par défaut, activé par -v / --verbose).

# =============================================================================
#  Configuration du port série
# =============================================================================

baudRate=115200        ##< @brief Baud rate de la transmission UART.
logDir="./Logs/Device" ##< @brief Dossier de destination des logs.

# =============================================================================
#  Marqueurs de protocole (doivent correspondre au firmware)
# =============================================================================

dumpErrorPrefix="<<<ERROR:"      ##< @brief Repère d'erreur lors du dumps des logs.
dumpStart="<<<DUMP_START>>>"     ##< @brief Repère de debut du dumps des logs.
fileStartPrefix="<<<FILE_START:" ##< @brief Repère de début de fichier lors du dumps des logs.
fileEnd="<<<FILE_END>>>"         ##< @brief Repère de fin de fichier lors du dumps des logs.
dumpEnd="<<<DUMP_END>>>"         ##< @brief Repère de fin de dumps des logs.

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
    echo -e "\t${_MAGENTA}${name} <port>"${_RESET}
    echo ""
    echo -e "${_WHITE}DESCRIPTION${_RESET}"
    echo -e "\tLit le port série spécifié et sauvegarde les fichiers reçus lors d'un dump ESP32."
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
    echo -e "\t\tChemin vers le port série à écouter."
    echo -e "\t\tExemple: ${name} /dev/ttyUSB0"

    return
}

# =============================================================================
#  Fonctions métier
# =============================================================================

##
# @brief Attente de l'ouverture d'un port série.
#
# @param port Nom du port série.
##
function waitForPort()
{
    local port="${1}"

    # Si le port n'est pas encore disponible, attendre qu'il apparaisse
    if [[ ! -e "${port}" ]]
    then
        info "En attente du port '${port}'."

        while [[ ! -e "${port}" ]]
        do
            sleep 1
        done

        info "Port '${port}' détecté."
    fi

    return
}



##
# @brief Configure la communication avec un port série.
#
# @param port Nom du port série
##
function configurePort()
{
    local port="${1}"

    # Configuration du port série en mode raw 8N1 sans echo
    stty -F "${port}" "${baudRate}" raw cs8 -cstopb -parenb -echo

    return
}



##
# @brief Parse les dumps de logs via le port série.
#
# @param port Nom du port série.
##
function parseDump()
{
    local port="${1}"

    # État du parsing
    local inDump=false
    local currentFile=""
    local fileName=""
    local filesReceived=0

    # Lecture du port
    while IFS= read -r line <&3
    do
        # Nettoyage des caractères de contrôle résiduels
        line="$(echo "${line}" | tr -d '\r')"

        # Ignorer tout ce qui précède le marqueur de début de dump
        [[ "${inDump}" == false ]] && continue

        # Erreur remontée par le firmware
        if [[ "${line}" == "${dumpErrorPrefix}"* ]]
        then
            echo -e ${_RED}"[ERROR] Firmware : ${line}"${_RESET}
            continue
        fi

        # Début du dump
        if [[ "${line}" == "${dumpStart}" ]]
        then
            inDump=true
            mkdir -p "${logDir}"
            info "Dump démarré"

            continue
        fi

        # Début d'un fichier
        if [[ "${line}" == "${fileStartPrefix}"* ]]
        then
            # Extraction du chemin depuis le marqueur : <<<FILE_START:/Logs/mqtt.log>>> -> /Logs/mqtt.log
            currentFile="$(echo "${line}" | sed "s|${fileStartPrefix}||;s|>>>.*||")"
            fileName="$(basename "${currentFile}")"

            # Création du dossier parent si nécessaire
            mkdir -p "$(dirname "${logDir}/${fileName}")"

            # Création ou vidage du fichier destination
            > "${logDir}/${fileName}"

            debug "Réception du fichier : ${fileName}"

            continue
        fi

        # Fin d'un fichier
        if [[ "${line}" == "${fileEnd}" ]]
        then
            if [[ -n "${currentFile}" ]]
            then
                debug "Fichier sauvegardé : ${logDir}/${fileName}"

                filesReceived=$((filesReceived + 1))
                currentFile=""
            fi
            continue
        fi

        # Fin du dump
        if [[ "${line}" == "${dumpEnd}" ]]
        then
            info "Dump terminé"
            echo ""
            echo -e "${_WHITE}╔══════════════════════════════════════════════════╗${_RESET}"
            echo -e "${_WHITE}║  Résumé                                          ║${_RESET}"
            echo -e "${_WHITE}╠══════════════════════════════════════════════════╣${_RESET}"
            echo -e "${_WHITE}║ $(printf "%-76s" "Fichiers reçus : ${_GREEN}${filesReceived}${_RESET}${_WHITE}")║${_RESET}"
            echo -e "${_WHITE}║ $(printf "%-75s" "Dossier        : ${_MAGENTA}${logDir}${_RESET}${_WHITE}")║${_RESET}"
            echo -e "${_WHITE}╚══════════════════════════════════════════════════╝${_RESET}"

            break
        fi

        # Écriture des logs
        if [[ -n "${currentFile}" ]]
        then
            echo "${line}" >> "${logDir}/${fileName}"
        fi

    done 3<"${port}"

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
        error "${argumentErrorCode}" "Nombre d'arguments insuffisant. Au moins 1 argument est requis: <port>."
    fi

    local port="${1}"

    # Attente et configuration du port série
    waitForPort "${port}"
    configurePort "${port}"

    debug "Port    : $port"
    debug "Dossier : $logDir"
    info "En attente du dump ESP32"

    # Lecture et parsing du dump série
    parseDump "${port}"

    return
}

# Lancement du script avec tous les arguments
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
    main "${@}"
fi
