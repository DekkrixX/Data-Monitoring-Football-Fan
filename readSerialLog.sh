# =============================================================================
# readSerialLog.sh - Lecture et sauvegarde de dumps de logs via port série
#
# Dépendances : stty
# Usage       : voir la fonction usage() ci-dessous ou lancer avec --help
# =============================================================================

# =============================================================================
#  Codes de couleur ANSI
# =============================================================================

_RESET="\033[1;0m"
_RED="\033[1;31m"
_GREEN="\033[1;32m"
_CYAN="\033[1;36m"
_WHITE="\033[1m"
_MAGENTA="\033[1;35m"

# =============================================================================
#  Configuration du port série
# =============================================================================

baudRate=115200
logDir="./Logs/Device"

# =============================================================================
#  Marqueurs de protocole (doivent correspondre au firmware)
# =============================================================================

dumpStart="<<<DUMP_START>>>"
fileStartPrefix="<<<FILE_START:"
fileEnd="<<<FILE_END>>>"
dumpEnd="<<<DUMP_END>>>"

# =============================================================================
#  Fonctions utilitaires
# =============================================================================

function usage()
{
    local name=$(basename "$0")

    echo -e $_WHITE"COMMANDE"$_RESET
    echo -e "\t$_MAGENTA$name <PORT>"$_RESET
    echo ""
    echo -e $_WHITE"DESCRIPTION"$_RESET
    echo -e "\tLit le port série spécifié et sauvegarde les fichiers reçus lors d'un dump ESP32."
    echo -e "\tLe script attend l'ouverture du port si celui-ci n'est pas encore disponible."
    echo -e "\tLes fichiers reçus sont sauvegardés dans le dossier '$logDir'."
    echo ""
    echo -e $_WHITE"OPTIONS"$_RESET
    echo -e "\t-h | --help"
    echo -e "\t\tAffiche cette aide."
    echo -e "\t\tExemple: $name --help"
    echo ""
    echo -e $_WHITE"ARGUMENTS"$_RESET
    echo -e "\t<PORT>"
    echo -e "\t\tChemin vers le port série à écouter."
    echo -e "\t\tExemple: $name /dev/ttyUSB0"

    return
}

# =============================================================================
#  Fonctions métier
# =============================================================================

function waitForPort()
{
    local port="$1"

    # Si le port n'est pas encore disponible, attendre qu'il apparaisse
    if [[ ! -e "$port" ]]
    then
        echo -e $_CYAN"[INFO] En attente du port '$port'."$_RESET
        while [[ ! -e "$port" ]]
        do
            sleep 1
        done
        echo -e $_GREEN"[OK]   Port '$port' détecté."$_RESET
    fi

    return
}

function configurePort()
{
    local port="$1"

    # Configuration du port série en mode raw 8N1 sans echo
    stty -F "$port" "$baudRate" raw cs8 -cstopb -parenb -echo

    return
}

function parseDump()
{
    local port="$1"

    # État du parsing
    local inDump=false
    local currentFile=""
    local fileName=""
    local filesReceived=0

    while IFS= read -r line <&3
    do
        # Nettoyage des caractères de contrôle résiduels (retour chariot Windows)
        line=$(echo "$line" | tr -d '\r')

        # -- Début du dump ----------------------------------------------------
        if [[ "$line" == "$dumpStart" ]]
        then
            inDump=true
            mkdir -p "$logDir"
            echo -e $_CYAN"[INFO] Dump démarré"$_RESET
            continue
        fi

        # Ignorer tout ce qui précède le marqueur de début de dump
        [[ "$inDump" == false ]] && continue

        # -- Début d'un fichier -----------------------------------------------
        if [[ "$line" == $fileStartPrefix* ]]
        then
            # Extraction du chemin depuis le marqueur : <<<FILE_START:/Logs/mqtt.log>>> -> /Logs/mqtt.log
            currentFile=$(echo "$line" | sed "s|$fileStartPrefix||;s|>>>.*||")
            fileName=$(basename "$currentFile")

            # Création du dossier parent si nécessaire
            mkdir -p "$(dirname "$logDir/$fileName")"

            # Création ou vidage du fichier destination
            > "$logDir/$fileName"

            echo -e $_CYAN"[INFO] Réception : $fileName"$_RESET
            continue
        fi

        # -- Fin d'un fichier -------------------------------------------------
        if [[ "$line" == "$fileEnd" ]]
        then
            if [[ -n "$currentFile" ]]
            then
                echo -e $_GREEN"[OK]   Sauvegardé : $logDir/$fileName"$_RESET
                filesReceived=$((filesReceived + 1))
                currentFile=""
            fi
            continue
        fi

        # -- Fin du dump ------------------------------------------------------
        if [[ "$line" == "$dumpEnd" ]]
        then
            echo ""
            echo -e "$_WHITE╔══════════════════════════════════════════════════╗$_RESET"
            echo -e "$_WHITE║  Résumé                                          ║$_RESET"
            echo -e "$_WHITE╠══════════════════════════════════════════════════╣$_RESET"
            echo -e "$_WHITE║ $(printf "%-76s" "Fichiers reçus : $_GREEN$filesReceived$_RESET$_WHITE")║$_RESET"
            echo -e "$_WHITE║ $(printf "%-75s" "Dossier        : $_MAGENTA$logDir$_RESET$_WHITE")║$_RESET"
            echo -e "$_WHITE╚══════════════════════════════════════════════════╝$_RESET"
            break
        fi

        # -- Erreur remontée par le firmware ----------------------------------
        if [[ "$line" == "<<<ERROR:"* ]]
        then
            echo -e $_RED"[ERROR] Firmware : $line"$_RESET
            continue
        fi

        # -- Contenu du fichier courant ---------------------------------------
        if [[ -n "$currentFile" ]]
        then
            echo "$line" >> "$logDir/$fileName"
        fi

    done 3<"$port"

    return
}

# =============================================================================
#  Point d'entrée du script
# =============================================================================

function main()
{
    # Affichage de l'aide si demandé
    if [[ "$1" == "-h" || "$1" == "--help" ]]
    then
        usage
        exit 0
    fi

    # Vérification du nombre d'arguments
    if [[ $# -ne 1 ]]
    then
        echo -e $_RED"[ERROR] Port série manquant."$_RESET >&2
        echo -e "\tUsage   : $(basename "$0") <PORT>" >&2
        echo -e "\tExemple : $(basename "$0") /dev/ttyUSB0" >&2
        exit 1
    fi

    local port="$1"

    # Attente et configuration du port série
    waitForPort "$port"
    configurePort "$port"

    echo -e $_CYAN"[INFO] Port    : $port"$_RESET
    echo -e $_CYAN"[INFO] Dossier : $logDir"$_RESET
    echo -e $_CYAN"[INFO] En attente du dump ESP32"$_RESET
    echo ""

    # Lecture et parsing du dump série
    parseDump "$port"

    return
}

# Lancement du script avec tous les arguments
main "$@"
