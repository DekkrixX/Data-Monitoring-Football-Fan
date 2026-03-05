# =============================================================================
# envcrypt.sh — Chiffrement/déchiffrement de fichiers d'environnement via SOPS
#
# Dépendances : sops (https://github.com/getsops/sops)
# Usage       : voir la fonction usage() ci-dessous ou lancer avec --help
# =============================================================================

# =============================================================================
#  Codes de couleur ANSI
# =============================================================================

_RESET="\033[1;0m"
_BLACK="\033[1;30m"
_RED="\033[1;31m"
_GREEN="\033[1;32m"
_YELLOW="\033[1;33m"
_BLUE="\033[1;34m"
_MAGENTA="\033[1;35m"
_CYAN="\033[1;36m"
_GRAY="\033[1;37m"
_WHITE="\033[1m"

# =============================================================================
#  Codes de sortie
# =============================================================================

argumentErrorCode=1         # Arguments manquants ou invalides
installationErrorCode=2     # Dépendance manquante (sops non installé)
fileNotFoundErrorCode=3     # Fichier source introuvable
exportPublicKeyErrorCode=4  # Échec de l'export de la clé publique
exportPrivateKeyErrorCode=5 # Échec de l'export de la clé privée
importKeyErrorCode=6        # Échec de l'import d'une clé
encryptFileErrorCode=7      # Échec du chiffrement
decryptFileErrorCode=8      # Échec du déchiffrement
addErrorCode=9              # Échec de l'ajout d'une clé publique
removeErrorCode=10          # Échec de la suppression d'une clé publique
readKeyErrorCode=11         # Échec de la lecture d'un fingerprint depuis un fichier .asc

# =============================================================================
#  Flags
# =============================================================================

VERBOSE=0 # Mode verbeux — désactivé par défaut, activé par -v / --verbose

# =============================================================================
#  Variables globales
# =============================================================================

publicKeyDirectory=".PublicKeys" # Dossier contenant les clés publiques utilisées pour le chiffrement

# =============================================================================
#  Fonctions utilitaires
# =============================================================================

function usage()
{
    local name=$(basename "$0")

    echo -e $_WHITE"COMMANDE"$_RESET
    echo -e $_MAGENTA"\t$name [OPTIONS] <opération>"$_RESET
    echo ""
    echo -e $_WHITE"DESCRIPTION"$_RESET
    echo -e "\tCe script Bash permettant de chiffrer et déchiffrer des fichiers d'environnement (.env et autres) via SOPS et GPG. Il permet l'export d'une paire de clés GPG, l'import d'une clé, le chiffrement d'un fichier, et le déchiffrement d'un fichier."
    echo ""
    echo -e $_WHITE"OPTIONS"$_RESET
    echo -e "\t-h | --help"
    echo -e "\t\tAffiche cette aide."
    echo -e "\t\tDoit être placé avant l'opération."
    echo -e "\t\tExemple: $name --help"
    echo -e "\t-v | --verbose"
    echo -e "\t\tActive les messages de debug détaillés."
    echo -e "\t\tDoit être placé avant l'opération."
    echo -e "\t\tExemple: $name --verbose --encrypt AB12CD34EF56GH78 .env"
    echo ""
    echo -e $_WHITE"ARGUMENTS"$_RESET
    echo -e "\topération:"
    echo -e "\t\t--export <fingerprint_gpg> <fichier>"
    echo -e "\t\t\tExporte la clé publique correspondant au fingerprint GPG fourni."
    echo -e "\t\t\tProduit deux fichiers: publicKey.asc"
    echo -e "\t\t\tExemple: $name --export AB12CD34EF56GH78"
    echo -e "\t\t--import <fichier_cle.asc>"
    echo -e "\t\t\tImporte une clé GPG publique depuis un fichier .asc."
    echo -e "\t\t\tExemple: $name --import publicKey.asc"
    echo -e "\t\t--encrypt <fichier>"
    echo -e "\t\t\tChiffre le fichier spécifié avec les clés publiques GPG du dossier $publicKeyDirectory."
    echo -e "\t\t\tProduit un fichier <fichier.encrypted>"
    echo -e "\t\t\tExemple: $name --encrypt .env"
    echo -e "\t\t--decrypt <fichier.encrypted>"
    echo -e "\t\t\tDéchiffre le fichier spécifié (requiert la clé privée correspondante importée)."
    echo -e "\t\t\tProduit un fichier dont l'extension .encrypted est retirée."
    echo -e "\t\t\tExemple: $name --decrypt .env.encrypted"
    echo -e "\t\t--add <fichier_cle.asc> <fichier>" 
    echo -e "\t\t\tAjoute un utilisateur capable de déchiffrer le fichier spécifié."
    echo -e "\t\t\tExemple: $name --add $publicKeyDirectory/User.asc .env.encrypted"
    echo -e "\t\t--remove <fichier_cle.asc> <fichier>"
    echo -e "\t\t\tSupprime un utilisateur capable de déchiffrer le fichier spécifié."
    echo -e "\t\t\tExemple: $name --remove $publicKeyDirectory/User.asc .env.encrypted"
    echo ""
    echo -e $_WHITE"AUTEUR"$_RESET
    echo -e "\tÉcrit par DekkrixX."

    return
}

function debug()
{
    local message=$1

    if [ "$VERBOSE" -eq 1 ]
    then
        echo -e $_WHITE"[DEBUG] $message"$_RESET >&2
    fi

    return
}

function info()
{
    local message=$1

    echo -e $_CYAN"[INFO] $message"$_RESET >&2

    return
}

function warning()
{
    local message=$1

    echo -e $_YELLOW"[AVERTISSEMENT] $message"$_RESET >&2

    return
}

function error()
{
    local code=$1
    local message=$2

    echo -e $_RED"[ERREUR:$code] $message"$_RESET >&2

    # En cas d'erreur d'argument, on affiche l'usage pour guider l'utilisateur
    if [ "$code" -eq "$argumentErrorCode" ]
    then
        usage
    fi

    exit "$code"
}

# =============================================================================
#  Fonctions métier
# =============================================================================

function exportKey()
{
    local key=$1
    local file=$2".asc"

    debug "Début de l'exportation de la clé GPG: '$key'."

    # Export de la clé publique
    debug "Export de la clé publique vers '$file'."
    if gpg --armor --export "$key" > "$file"
    then
        info "Clé publique exportée avec succès: '$file'."
    else
        error $exportPublicKeyErrorCode "Impossible d'exporter la clé publique pour le fingerprint '$key'. Vérifiez que ce fingerprint existe dans votre trousseau GPG (gpg --list-keys)."
    fi

    debug "Fin de l'exportation de la clé GPG: '$key'."
# Dossier contenant les clés publiques utilisées pour le chiffrement

    return
}

function importKey()
{
    local fileKey=$1

    debug "Début de l'importation de la clé depuis le fichier '$fileKey'."

    # Import de la clé publique
    debug "Import de la clé publique dans le fichier '$fileKey'."
    if gpg --import "$fileKey"
    then
        info "Clé importée avec succès depuis '$fileKey'."
        info "Vous pouvez vérifier l'import avec: gpg --list-keys"
    else
        error $importKeyErrorCode "Impossible d'importer la clé depuis '$fileKey'. Vérifiez que le fichier est un fichier de clé GPG valide au format ASCII armor (.asc)."
    fi

    debug "Fin de l'importation de la clé depuis le fichier '$fileKey'."

    return
}

function encryptFile()
{
    local file=$1
    local encryptedFile="$file.encrypted"

    debug "Lecture des clés publiques depuis le dossier '$publicKeyDirectory'."

    # Récupération des fingerprints de toutes les clés publiques disponibles
    local keys
    keys=$(readKeys | cut -d':' -f2 | xargs | tr ' ' ',')

    if [ -z "$keys" ]
    then
        error $encryptFileErrorCode "Aucune clé publique trouvée dans '$publicKeyDirectory'. Ajoutez au moins un fichier .asc avant de chiffrer."
    fi

    debug "Clés GPG utilisées pour le chiffrement : '$keys'."
    debug "Début du chiffrement de '$file' -> '$encryptedFile' avec les clés GPG '$keys'."

    # Chiffrement du fichier
    debug "Chiffrement du fichier '$file'."
    if sops --encrypt $(echo "$keys" | sed 's/,/ --pgp /g' | sed 's/^/--pgp /') "$file" > "$encryptedFile"
    then
        info "Fichier chiffré avec succès : '$encryptedFile'."
    else
        # Nettoyer le fichier de sortie potentiellement vide ou corrompu
        rm -f "$encryptedFile"
        error $encryptFileErrorCode "Impossible de chiffrer '$file' avec la clé '$keys'. Causes possibles: fingerprint GPG invalide, clé publique absente du trousseau, ou fichier déjà chiffré par sops. Vérifiez avec: gpg --list-keys"
    fi

    debug "Fin du chiffrement de '$file' -> '$encryptedFile' avec les clés GPG '$keys'."

    return
}

function decryptFile()
{
    local file=$1
    # Retire l'extension .encrypted pour obtenir le nom du fichier déchiffré
    local decryptedFile="${file%.encrypted}"

    # Si le fichier n'a pas l'extension .encrypted, avertir et adapter le nom de sortie
    if [ "$decryptedFile" = "$file" ]
    then
        warning "Le fichier '$file' ne possède pas l'extension '.encrypted'." >&2
        warning "Le fichier déchiffré sera produit sous le nom '$decryptedFile.decrypted'." >&2
        decryptedFile="$file.decrypted"
    fi

    debug "Début du déchiffrement de '$file' -> '$decryptedFile'."

    # Chiffrement du fichier
    debug "Déchiffrement du fichier '$file'."
    if sops --decrypt "$file" > "$decryptedFile"
    then
        info "Fichier déchiffré avec succès: '$decryptedFile'."
    else
        # Nettoyer le fichier de sortie potentiellement vide ou corrompu
        rm -f "$decryptedFile"
        error $decryptFileErrorCode "Impossible de déchiffrer '$file'. Causes possibles: la clé privée n'est pas importée dans le trousseau GPG local, le fichier n'a pas été chiffré avec sops, ou le fichier est corrompu. Vérifiez avec: gpg --list-secret-keys"
    fi

    debug "Fin du déchiffrement de '$file' -> '$decryptedFile'."

    return
}

function add()
{
    local key=$1
    local file=$2

    # Ajout d'une clé publique au fichier
    debug "Ajout d'une clé '$key' au fichier '$file'."
    if sops --add-pgp "$key" "$file"
    then
        info "Destinataire '$key' ajouté avec succès au fichier '$file'."
    else
        error $addErrorCode "Impossible d'ajouter le destinataire '$key' au fichier '$file'. Vérifiez que le fingerprint est valide et que la clé publique est présente dans le trousseau GPG."
    fi

    return
}

function remove()
{
    local key=$1
    local file=$2

    # Suppression d'une clé publique du fichier
    debug "Suppression d'une clé '$key' du fichier '$file'."
    if sops --rm-pgp "$key" "$file"
    then
        info "Destinataire '$key' supprimé avec succès du fichier '$file'."
    else
        error $removeErrorCode "Impossible de supprimer le destinataire '$key' du fichier '$file'. Vérifiez que le fingerprint est valide et qu'il était bien destinataire du fichier."
    fi

    return
}

function readKeys()
{
    local keys=""

    debug "Parcours du dossier '$publicKeyDirectory' pour lister les clés publiques."

    for key in $publicKeyDirectory/*.asc
    do
        # Extraction du fingerprint depuis le fichier .asc sans l'importer dans le trousseau
        local fpr=$(gpg --with-colons --import-options show-only --import "$key" | awk -F: '/^fpr:/ {print $10; exit}')

        if [ -z "$fpr" ]
        then
            warning "Impossible d'extraire le fingerprint depuis '$key'. Fichier ignoré."
            continue
        fi

        debug "Clé trouvée : '$(basename "$key")' -> '$fpr'."
        keys="$keys $(basename $key): $fpr\n"
    done

    echo -e "$keys"

    return
}

function getKeyFromFile()
{
    local file=$1

    debug "Extraction du fingerprint depuis le fichier '$file'."

    # Extraction du fingerprint depuis le fichier .asc sans l'importer dans le trousseau
    local fpr=$(gpg --with-colons --import-options show-only --import "$file" | awk -F: '/^fpr:/ {print $10; exit}')

    if [ -z "$fpr" ]
    then
        warning $readKeyErrorCode "Impossible d'extraire le fingerprint depuis '$file'."
    fi

    debug "Fingerprint extrait depuis '$file' -> '$fpr'."

    echo "$fpr"

    return
}

# =============================================================================
#  Point d'entrée du script
# =============================================================================

function main()
{
    # Parsing de l'option -h/--help en première position
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]
    then
        usage
        exit 0
    fi
    # Parsing de l'option -v/--verbose en première position
    if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]
    then
        VERBOSE=1
        debug "Mode verbeux activé."
        shift  # Retire -v/--verbose de la liste des arguments
    fi

    # Vérification du nombre minimal d'arguments restants
    if [ $# -lt 1 ]
    then
        error $argumentErrorCode "Nombre d'arguments insuffisant. Au moins 1 argument est requis: <opération>."
    fi

    # Vérification de la présence de sops
    if ! command -v sops >/dev/null 2>&1
    then
        error $installationErrorCode "'sops' est introuvable. Installez-le depuis: https://github.com/getsops/sops/releases"
    fi

    local operation=$1

    debug "Opération demandée: '$operation'."

    case "$operation" in
        --export)
            # --export requiert exactement 3 arguments: opération, fingerprint, fichier
            if [ $# -ne 3 ]
            then
                error $argumentErrorCode "L'opération --export requiert exactement 3 arguments: --export <fingerprint_gpg> <fichier>. Reçu: $# argument(s)."
            fi

            local key=$2
            local file=$3
            debug "Fichier cible: '$file', clé GPG: '$key'."

            exportKey "$key" "$file"
            ;;
        --import)
            # --import requiert exactement 2 arguments: opération, fingerprint
            if [ $# -ne 2 ]
            then
                error $argumentErrorCode "L'opération --import requiert exactement 2 arguments: --import <fingerprint_gpg>. Reçu: $# argument(s)."
            fi

            local key=$2
            debug "Clé GPG: '$key'."

            importKey "$key"
            ;;
        --encrypt)
            # --encrypt requiert exactement 2 arguments: opération, fichier
            if [ $# -ne 2 ]
            then
                error $argumentErrorCode "L'opération --encrypt requiert exactement 2 arguments: --encrypt <fichier>. Reçu: $# argument(s)."
            fi

            local file=$2
            debug "Fichier cible: '$file'."

            if [ ! -f "$file" ]
            then
                error $fileNotFoundErrorCode "Le fichier à chiffrer '$file' est introuvable. Vérifiez le chemin et les permissions."
            fi

            encryptFile "$file"
            ;;
        --decrypt)
            # --decrypt requiert exactement 2 arguments: opération, fichier
            if [ $# -ne 2 ]
            then
                error $argumentErrorCode "L'opération --decrypt requiert exactement 2 arguments: --decrypt <fichier>. Reçu: $# argument(s)."
            fi

            local file=$2
            debug "Fichier cible: '$file'."

            if [ ! -f "$file" ]
            then
                error $fileNotFoundErrorCode "Le fichier à déchiffrer '$file' est introuvable. Vérifiez le chemin et les permissions."
            fi

            decryptFile "$file"
            ;;
        --add)
            # --add requiert exactement 3 arguments : opération, fichier clé, fichier chiffré
            if [ $# -ne 3 ]
            then
                error $argumentErrorCode "L'opération --add requiert exactement 3 arguments : --add <fichier_cle.asc> <fichier.encrypted>. Reçu : $# argument(s)."
            fi

            local fileKey=$2
            local file=$3
            debug "Ajout du destinataire '$(basename $fileKey)' au fichier '$file'."

            if [ ! -f "$file" ]
            then
                error $fileNotFoundErrorCode "Le fichier '$file' est introuvable. Vérifiez le chemin et les permissions."
            fi
            if [ ! -f "$fileKey" ]
            then
                error $fileNotFoundErrorCode "Le fichier '$fileKey' est introuvable. Vérifiez le chemin et les permissions."
            fi

            local key
            key=$(getKeyFromFile "$fileKey")

            add "$key" "$file"
            ;;
        --remove)
            # --remove requiert exactement 3 arguments : opération, fichier clé, fichier chiffré
            if [ $# -ne 3 ]
            then
                error $argumentErrorCode "L'opération --remove requiert exactement 3 arguments : --remove <fichier_cle.asc> <fichier.encrypted>. Reçu : $# argument(s)."
            fi

            local fileKey=$2
            local file=$3
            debug "Suppression du destinataire '$(basename $fileKey)' du fichier '$file'."

            if [ ! -f "$file" ]
            then
                error $fileNotFoundErrorCode "Le fichier '$file' est introuvable. Vérifiez le chemin et les permissions."
            fi
            if [ ! -f "$fileKey" ]
            then
                error $fileNotFoundErrorCode "Le fichier '$fileKey' est introuvable. Vérifiez le chemin et les permissions."
            fi

            local key
            key=$(getKeyFromFile "$fileKey")
            
            remove "$key" "$file"
            ;;
        *)
            error $argumentErrorCode "Opération inconnue: '$operation'. Opérations valides: --export, --import, --encrypt, --decrypt."
            ;;
    esac

    return
}

# Lancement du script avec tous les arguments
main "$@"
