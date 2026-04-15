# =============================================================================
# logviewer.sh - Visualisation colorisée de fichiers de log
#
# Dépendances : less
# Usage       : voir la fonction usage() ci-dessous ou lancer avec --help
# =============================================================================

# =============================================================================
#  Codes de couleur ANSI
# =============================================================================

_RESET="\033[1;0m"
_RED="\033[1;31m"
_YELLOW="\033[1;33m"
_CYAN="\033[1;36m"
_WHITE="\033[1m"
_MAGENTA="\033[1;35m"
_DIM="\033[2m"

# =============================================================================
#  Fonctions utilitaires
# =============================================================================

function usage()
{
    local name=$(basename "$0")

    echo -e $_WHITE"COMMANDE"$_RESET
    echo -e "\t$_MAGENTA$name <fichier.log>"$_RESET
    echo ""
    echo -e $_WHITE"DESCRIPTION"$_RESET
    echo -e "\tVisualise un fichier de log avec coloration syntaxique par niveau."
    echo -e "\tLes niveaux reconnus sont [INFO], [WARNING] et [ERROR]."
    echo -e "\tLe fichier est affiché dans less avec numérotation et barre de progression."
    echo ""
    echo -e $_WHITE"OPTIONS"$_RESET
    echo -e "\t-h | --help"
    echo -e "\t\tAffiche cette aide."
    echo -e "\t\tExemple: $name --help"
    echo -e "\t-d | --data"
    echo -e "\t\tActive la lecture de log de données."
    echo -e "\t\tExemple: $name --data data.log"
    echo ""
    echo -e $_WHITE"ARGUMENTS"$_RESET
    echo -e "\t<fichier.log>"
    echo -e "\t\tChemin vers le fichier de log à visualiser."
    echo -e "\t\tDoit être un fichier régulier, lisible, avec l'extension .log."
    echo -e "\t\tDoit contenir au moins une entrée [INFO], [WARNING] ou [ERROR]."
    echo -e "\t\tExemple: $name app.log"
    echo ""
    echo -e $_WHITE"NAVIGATION (less)"$_RESET
    echo -e "\t${_DIM}Flèches / j / k$_RESET    Défiler ligne par ligne"
    echo -e "\t${_DIM}Space / b$_RESET          Page suivante / précédente"
    echo -e "\t${_DIM}g / G$_RESET              Aller au début / à la fin"
    echo -e "\t${_DIM}q$_RESET                  Quitter"

    return
}

# =============================================================================
#  Fonctions métier
# =============================================================================

function checkLogFile()
{
    local file="$1"

    # Vérification de l'existence du fichier
    if [[ ! -e "$file" ]]
    then
        echo -e $_RED"[ERREUR] Le fichier '$file' n'existe pas."$_RESET >&2
        exit 1
    fi

    # Vérification que c'est un fichier régulier (pas un répertoire, lien, etc.)
    if [[ ! -f "$file" ]]
    then
        echo -e $_RED"[ERREUR] '$file' n'est pas un fichier régulier."$_RESET >&2
        exit 1
    fi

    # Vérification de l'extension .log
    if [[ "${file##*.}" != "log" ]]
    then
        echo -e $_RED"[ERREUR] '$file' n'est pas un fichier .log."$_RESET >&2
        exit 1
    fi

    # Vérification des permissions de lecture
    if [[ ! -r "$file" ]]
    then
        echo -e $_RED"[ERREUR] Permission refusée pour '$file'."$_RESET >&2
        exit 1
    fi

    return
}

function parseLogFile()
{
    local file="$1"

    # Compteurs par niveau
    local countInfo=0
    local countWarning=0
    local countError=0
    local countTotal=0

    # En-tête avec le nom du fichier
    echo -e "$_WHITE╔══════════════════════════════════════════════════════════════╗$_RESET"
    echo -e "$_WHITE║  $(printf "%-60s" "Fichier : $(basename "$file")")║$_RESET"
    echo -e "$_WHITE╚══════════════════════════════════════════════════════════════╝$_RESET"
    echo ""

    # Lecture et colorisation ligne par ligne
    while IFS= read -r line
    do
        countTotal=$((countTotal + 1))

        if echo "$line" | grep -q "\[INFO\]"
        then
            countInfo=$((countInfo + 1))
            echo -e "$_CYAN$line$_RESET"

        elif echo "$line" | grep -q "\[WARNING\]"
        then
            countWarning=$((countWarning + 1))
            echo -e "$_YELLOW$line$_RESET"

        elif echo "$line" | grep -q "\[ERROR\]"
        then
            countError=$((countError + 1))
            echo -e "$_RED$line$_RESET"

        else
            # Ligne sans niveau reconnu
            echo "$line"
        fi

    done < "$file"

    # Pied de page avec les statistiques de parsing
    echo ""
    echo -e "$_WHITE╔══════════════════════════════════════════════════════════════╗$_RESET"
    echo -e "$_WHITE║  Résumé                                                      ║$_RESET"
    echo -e "$_WHITE╠══════════════════════════════════════════════════════════════╣$_RESET"
    echo -e "$_WHITE║  $(printf "%-60s" "Total   : ${countTotal}")║${_RESET}"
    echo -e "$_WHITE║  $(printf "%-86s" "${_CYAN}INFO$_RESET$_WHITE    : $countInfo")║$_RESET"
    echo -e "$_WHITE║  $(printf "%-86s" "${_YELLOW}WARNING$_RESET$_WHITE : ${countWarning}")║$_RESET"
    echo -e "$_WHITE║  $(printf "%-86s" "${_RED}ERROR$_RESET$_WHITE   : ${countError}")║$_RESET"
    echo -e "$_WHITE╚══════════════════════════════════════════════════════════════╝$_RESET"

    return
}



function parseDataFile()
{
    local file="$1"
 
    # Déclarer un tableau associatif
    declare -A keyCounts
 
    echo -e "$_WHITE╔══════════════════════════════════════════════════════════════╗$_RESET"
    echo -e "$_WHITE║  $(printf "%-60s" "Fichier : $(basename "$file")")║$_RESET"
    echo -e "$_WHITE╚══════════════════════════════════════════════════════════════╝$_RESET"
    echo ""

    # Lire le fichier ligne par ligne
    while IFS= read -r line; do
        # Extraire la clé (entre "] " et ":")
        local key=$(echo "$line" | sed -E 's/^.*\] ([^:]+):.*$/\1/')

        # Incrémenter le compteur si clé non vide
        if [[ -n "$key" ]]; then
            ((keyCounts["$key"]++))
        fi

        if echo "$line" | grep -q "\[INFO\]"
        then
            countInfo=$((countInfo + 1))
            echo -e "$_CYAN$line$_RESET"

        elif echo "$line" | grep -q "\[WARNING\]"
        then
            countWarning=$((countWarning + 1))
            echo -e "$_YELLOW$line$_RESET"

        elif echo "$line" | grep -q "\[ERROR\]"
        then
            countError=$((countError + 1))
            echo -e "$_RED$line$_RESET"

        else
            # Ligne sans niveau reconnu
            echo "$line"
        fi
    done < "$file"
 
    # Résumé : nombre de lignes par clé
    echo ""
    echo -e "$_WHITE╔══════════════════════════════════════════════════════════════╗$_RESET"
    echo -e "$_WHITE║  Résumé des données                                          ║$_RESET"
    echo -e "$_WHITE╠══════════════════════════════════════════════════════════════╣$_RESET"

    printf "%s\n" "${!keyCounts[@]}" | sort | while IFS= read -r key
    do
        local count=${keyCounts["$key"]}
        echo -e "$_WHITE║  $(printf "%-87s" "${_MAGENTA}${key}${_RESET}${_WHITE} : ${count} entrée(s)")║$_RESET"
    done
 
    echo -e "$_WHITE╚══════════════════════════════════════════════════════════════╝$_RESET"
 
    return
}

# =============================================================================
#  Point d'entrée du script
# =============================================================================

function main()
{
    # Affichage de l'aide si demandé ou si aucun argument n'est fourni
    if [[ "$1" == "-h" || "$1" == "--help" || $# -eq 0 ]]
    then
        usage
        exit 0
    fi

    # Vérification du nombre d'arguments
    if [[ $# -gt 2 ]]
    then
        usage
        exit 1
    fi

    local file=""
    local mode="log"
 
    for arg in "$@"
    do
        if [[ "$arg" == "-d" || "$arg" == "--data" ]]
        then
            mode="data"
        else
            file="$arg"
        fi
    done

    # Validation du fichier avant parsing
    if [[ -z "$file" ]]
    then
        echo -e $_RED"[ERREUR] Aucun fichier spécifié."$_RESET >&2
        usage
        exit 1
    fi
    checkLogFile "$file"

    # Affichage paginé via less
    # -R : interprète les codes couleur ANSI
    # -S : désactive le retour à la ligne automatique
    # -N : affiche les numéros de ligne
    # -M : affiche le pourcentage de progression en bas
    if [[ "$mode" == "data" ]]
    then
        parseDataFile "$file" | less -R -S -N -M --prompt=" Navigation : [Flèches/j/k] Défiler  [Space/b] Page  [g/G] Début/Fin  [q] Quitter  --"
    else
        parseLogFile "$file" | less -R -S -N -M --prompt=" Navigation : [Flèches/j/k] Défiler  [Space/b] Page  [g/G] Début/Fin  [q] Quitter  --"
    fi
}

# Lancement du script avec tous les arguments
main "$@"
