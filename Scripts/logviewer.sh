##
# @file logviewer.sh
#
# @brief Visualisation colorisée de fichiers de log.
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

argumentErrorCode=1     ##< @brief Arguments manquants ou invalides.
fileNotFoundErrorCode=2 ##< @brief Fichier source introuvable.

# =============================================================================
#  Flag
# =============================================================================

VERBOSE=0 ##< @brief Mode verbeux (désactivé par défaut, activé par -v / --verbose).

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
    echo -e "\t${_MAGENTA}${name} <fichier.log>"${_RESET}
    echo ""
    echo -e "${_WHITE}DESCRIPTION${_RESET}"
    echo -e "\tVisualise un fichier de log avec coloration syntaxique par niveau."
    echo ""
    echo -e "${_WHITE}OPTIONS${_RESET}"
    echo -e "\t-h | --help"
    echo -e "\t\tAffiche cette aide."
    echo -e "\t\tExemple: ${name} --help"
    echo -e "\t-v | --verbose"
    echo -e "\t\tActive les messages de debug détaillés."
    echo -e "\t\tExemple: ${name} --verbose file.log"
    echo -e "\t-d | --data"
    echo -e "\t\tActive la lecture de log de données."
    echo -e "\t\tExemple: ${name} --data data.log"
    echo ""
    echo -e "${_WHITE}ARGUMENTS${_RESET}"
    echo -e "\t<fichier.log>"
    echo -e "\t\tChemin vers le fichier de log à visualiser."
    echo -e "\t\tExemple: ${name} app.log"
    echo ""
    echo -e ${_WHITE}"NAVIGATION (less)"${_RESET}
    echo -e "\t${_DIM}Flèches / j / k${_RESET}    Défiler ligne par ligne"
    echo -e "\t${_DIM}Space / b${_RESET}          Page suivante / précédente"
    echo -e "\t${_DIM}g / G${_RESET}              Aller au début / à la fin"
    echo -e "\t${_DIM}q${_RESET}                  Quitter"

    return
}

# =============================================================================
#  Fonctions métier
# =============================================================================

##
# @brief Parse le fichier de logs.
#
# @param file Nom du fichier de logs.
##
function parseLogFile()
{
    local file="${1}"

    # Compteurs par niveau
    local countInfo=0
    local countWarning=0
    local countError=0
    local countTotal=0

    # En-tête avec le nom du fichier
    echo -e "${_WHITE}╔══════════════════════════════════════════════════════════════╗${_RESET}"
    echo -e "${_WHITE}║  $(printf "%-60s" "Fichier : $(basename "${file}")")║${_RESET}"
    echo -e "${_WHITE}╚══════════════════════════════════════════════════════════════╝${_RESET}"
    echo ""

    # Lecture et colorisation ligne par ligne
    while IFS= read -r line
    do
        (( countTotal++ ))

        if echo "${line}" | grep -q "\[INFO\]"
        then
            (( countInfo++ ))
            echo -e "${_CYAN}${line}${_RESET}"

        elif echo "${line}" | grep -q "\[WARNING\]"
        then
            (( countWarning++ ))
            echo -e "${_YELLOW}${line}${_RESET}"

        elif echo "${line}" | grep -q "\[ERROR\]"
        then
            (( countError++ ))
            echo -e "${_RED}${line}${_RESET}"

        else
            # Ligne sans niveau reconnu
            echo "${line}"
        fi

    done < "${file}"

    # Pied de page avec les statistiques de parsing
    echo ""
    echo -e "${_WHITE}╔══════════════════════════════════════════════════════════════╗${_RESET}"
    echo -e "${_WHITE}║  Résumé                                                      ║${_RESET}"
    echo -e "${_WHITE}╠══════════════════════════════════════════════════════════════╣${_RESET}"
    echo -e "${_WHITE}║  $(printf "%-60s" "Total   : ${countTotal}")║${_RESET}"
    echo -e "${_WHITE}║  $(printf "%-86s" "${_CYAN}INFO${_RESET}${_WHITE}    : ${countInfo}")║${_RESET}"
    echo -e "${_WHITE}║  $(printf "%-86s" "${_YELLOW}WARNING${_RESET}${_WHITE} : ${countWarning}")║$_RESET"
    echo -e "${_WHITE}║  $(printf "%-86s" "${_RED}ERROR${_RESET}${_WHITE}   : ${countError}")║${_RESET}"
    echo -e "${_WHITE}╚══════════════════════════════════════════════════════════════╝${_RESET}"

    return
}



##
# @brief Parse un fichier de logs de données.
#
# @param file Nom du fichier de logs.
##
function parseDataFile()
{
    local file="${1}"
 
    # Déclarer un tableau associatif
    declare -A keyCounts
 
    echo -e "${_WHITE}╔══════════════════════════════════════════════════════════════╗${_RESET}"
    echo -e "${_WHITE}║  $(printf "%-60s" "Fichier : $(basename "${file}")")║${_RESET}"
    echo -e "${_WHITE}╚══════════════════════════════════════════════════════════════╝${_RESET}"
    echo ""

    # Lire le fichier ligne par ligne
    while IFS= read -r line; do
        # Extraire la clé (entre "] " et ":")
        local key="$(echo "${line}" | sed -E 's/^.*\] ([^:]+):.*$/\1/')"

        # Incrémenter le compteur si clé non vide
        if [[ -n "${key}" ]]; then
            (( keyCounts["${key}"]++ ))
        fi

        if echo "${line}" | grep -q "\[INFO\]"
        then
            (( countInfo++ ))
            echo -e "${_CYAN}${line}${_RESET}"

        elif echo "${line}" | grep -q "\[WARNING\]"
        then
            (( countWarning++ ))
            echo -e "${_YELLOW}${line}${_RESET}"

        elif echo "${line}" | grep -q "\[ERROR\]"
        then
            (( countError++ ))
            echo -e "${_RED}${line}${_RESET}"

        else
            # Ligne sans niveau reconnu
            echo "${line}"
        fi
    done < "${file}"
 
    # Résumé : nombre de lignes par clé
    echo ""
    echo -e "${_WHITE}╔══════════════════════════════════════════════════════════════╗${_RESET}"
    echo -e "${_WHITE}║  Résumé des données                                          ║${_RESET}"
    echo -e "${_WHITE}╠══════════════════════════════════════════════════════════════╣${_RESET}"

    printf "%s\n" "${!keyCounts[@]}" | sort | while IFS= read -r key
    do
        local count="${keyCounts["${key}"]}"
        echo -e "${_WHITE}║  $(printf "%-87s" "${_MAGENTA}${key}${_RESET}${_WHITE} : ${count} entrée(s)")║${_RESET}"
    done
 
    echo -e "${_WHITE}╚══════════════════════════════════════════════════════════════╝${_RESET}"
 
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
    # Affichage de l'aide si demandé ou si aucun argument n'est fourni
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
    if [[ "${#}" -gt 2 ]]
    then
        error "${argumentErrorCode}" "Nombre d'arguments insuffisant. Au moins 1 argument est requis: <file>."
    fi

    local file=""
    local mode="log"

    for arg in "${@}"
    do
        if [[ "${arg}" == "-d" || "${arg}" == "--data" ]]
        then
            mode="data"
        else
            file="${arg}"
        fi
    done

    # Validation du fichier avant parsing
    if [[ -z "${file}" ]]
    then
        error "${argumentErrorCode}" "Aucun fichier spécifié."
    fi
    # Vérification de l'existence du fichier
    if [[ ! -f "$file" ]]
    then
        error "${fileNotFoundErrorCode}" "Le fichier '${file}' n'existe pas."
    fi

    # Affichage paginé via less
    # -R : interprète les codes couleur ANSI
    # -S : désactive le retour à la ligne automatique
    # -N : affiche les numéros de ligne
    # -M : affiche le pourcentage de progression en bas
    if [[ "${mode}" == "data" ]]
    then
        debug "Lecture de fichier de logs de données."
        parseDataFile "${file}" | less -R -S -N -M --prompt=" Navigation : [Flèches/j/k] Défiler  [Space/b] Page  [g/G] Début/Fin  [q] Quitter  --"
    else
        debug "Lecture de fichier de logs global."
        parseLogFile "${file}" | less -R -S -N -M --prompt=" Navigation : [Flèches/j/k] Défiler  [Space/b] Page  [g/G] Début/Fin  [q] Quitter  --"
    fi
}

# Lancement du script avec tous les arguments
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
    main "${@}"
fi
