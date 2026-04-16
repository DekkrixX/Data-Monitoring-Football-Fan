##
# @file envcrypt.sh
# 
# @brief Chiffrement/déchiffrement de fichiers d'environnement via SOPS.
# @details Le script permet de chiffrer ou déchiffrer un fichier mais aussi d'aujouter ou retirer des clés publiques au fichier chiffrer.
#
# @see out.sh
# @see sops (https://github.com/getsops/sops)
# @see Fonction usage() ou lancer le script avec --help
##

# =============================================================================
#  Import
# =============================================================================

source "$(dirname "${BASH_SOURCE[0]}")/out.sh"

# =============================================================================
#  Code de sortie
# =============================================================================

argumentErrorCode=1         ##< @brief Arguments manquants ou invalides.
installationErrorCode=2     ##< @brief Dépendance manquante.
fileNotFoundErrorCode=3     ##< @brief Fichier source introuvable.
exportPublicKeyErrorCode=4  ##< @brief Échec de l'export de la clé publique.
exportPrivateKeyErrorCode=5 ##< @brief Échec de l'export de la clé privée.
importKeyErrorCode=6        ##< @brief Échec de l'import d'une clé.
encryptFileErrorCode=7      ##< @brief Échec du chiffrement.
decryptFileErrorCode=8      ##< @brief Échec du déchiffrement.
addErrorCode=9              ##< @brief Échec de l'ajout d'une clé publique.
removeErrorCode=10          ##< @brief Échec de la suppression d'une clé publique.
readKeyErrorCode=11         ##< @brief Échec de la lecture d'un fingerprint depuis un fichier .asc.

# =============================================================================
#  Flag
# =============================================================================

VERBOSE=0 ##< @brief Mode verbeux (désactivé par défaut, activé par -v / --verbose)

# =============================================================================
#  Variable globale
# =============================================================================

publicKeyDirectory=".PublicKeys" ##< @brief Dossier contenant les clés publiques utilisées pour le chiffrement

# =============================================================================
#  Fonction utilitaire
# =============================================================================

##
# @brief Affiche le manuel d'usage du script.
#
# @param name Nom du script.
#
# @since 1.0.0
# @date 11 avril 2026
# @author DekkrixX
##
function usage()
{
    local name=$(basename "$0")

    echo -e $_WHITE"COMMANDE"$_RESET
    echo -e $_MAGENTA"\t$name [OPTIONS] <opération>"$_RESET
    echo ""
    echo -e $_WHITE"DESCRIPTION"$_RESET
    echo -e "\tCe script Bash permet de chiffrer et déchiffrer des fichiers d'environnement (.env et autres) via SOPS et GPG. Il permet l'export d'une paire de clés GPG, l'import d'une clé, le chiffrement d'un fichier, et le déchiffrement d'un fichier."
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

# =============================================================================
#  Fonction métier
# =============================================================================

##
# @brief Export une clé publique sous forme de fichier clé .asc.
#
# @param key  Clé publique.
# @param file Nom du fichier clé .asc créé.
#
# @since 1.0.0
# @date 11 avril 2026
# @author DekkrixX
##
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


##
# @brief Import une clé publique à partir d'un fichier clé .asc.
#
# @param fileKey Nom du fichier clé .asc.
#
# @pre fileKey Doit pouvoir être ouvert en lecture.
#
# @since 1.0.0
# @date 11 avril 2026
# @author DekkrixX
##
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


##
# @brief Chiffre un fichier avec les clés publiques associées.
#
# @param file Nom du fichier.
#
# @pre file Doit pouvoir être ouvert en lecture.
#
# @remark Le fichier de base n'est pas écrasé.
#
# @since 1.0.0
# @date 11 avril 2026
# @author DekkrixX
##
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

    debug "Clés GPG utilisées pour le chiffrement: '$keys'."
    debug "Début du chiffrement de '$file' -> '$encryptedFile' avec les clés GPG '$keys'."

    # Chiffrement du fichier
    debug "Chiffrement du fichier '$file'."
    if sops --encrypt --input-type dotenv --output-type dotenv $(echo "$keys" | sed 's/,/ --pgp /g' | sed 's/^/--pgp /') "$file" > "$encryptedFile"
    then
        info "Fichier chiffré avec succès: '$encryptedFile'."
    else
        # Nettoyer le fichier de sortie potentiellement vide ou corrompu
        rm -f "$encryptedFile"
        error $encryptFileErrorCode "Impossible de chiffrer '$file' avec la clé '$keys'. Causes possibles: fingerprint GPG invalide, clé publique absente du trousseau, ou fichier déjà chiffré par sops. Vérifiez avec: gpg --list-keys"
    fi

    debug "Fin du chiffrement de '$file' -> '$encryptedFile' avec les clés GPG '$keys'."

    return
}


##
# @brief Déchiffre un fichier chiffré.
#
# @param file Nom du fichier chiffré.
#
# @remark Le fichier chiffré n'est pas écrasé.
#
# @pre file Doit pouvoir être ouvert en lecture.
#
# @since 1.0.0
# @date 11 avril 2026
# @author DekkrixX
##
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
    if sops --decrypt --input-type dotenv --output-type dotenv "$file" > "$decryptedFile"
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


##
# @brief Ajoute une clé publique à associer au fichier chiffré.
#
# @param key  Clé publique.
# @param file Nom du fichier chiffré.
#
# @pre file Doit pouvoir être ouvert en lecture.
#
# @since 1.0.0
# @date 11 avril 2026
# @author DekkrixX
##
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


##
# @brief Supprime une clé publique associée au fichier chiffré.
#
# @param key  Clé publique.
# @param file Nom du fichier chiffré.
#
# @pre file Doit pouvoir être ouvert en lecture.
#
# @since 1.0.0
# @date 11 avril 2026
# @author DekkrixX
##
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


##
# @brief Lit tous les fichiers de clé .asc et afficher la clé publique de chaque fichier.
#
# @since 1.0.0
# @date 11 avril 2026
# @author DekkrixX
##
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

        debug "Clé trouvée: '$(basename "$key")' -> '$fpr'."
        local file=$(basename $key)
        keys="$keys ${file%.asc}: $fpr\n"
    done

    echo -e "$keys"

    return
}


##
# @brief Affichage de la clé publique d'un fichier .asc.
#
# @param file Nom du fichier de clé .asc.
#
# @pre file Doit pouvoir être ouvert en lecture.
#
# @since 1.0.0
# @date 11 avril 2026
# @author DekkrixX
##
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

##
# @brief Parsing des arguments et exécution de la bonne commande.
#
# @param $@ Tous les arguments du script.
#
# @since 1.0.0
# @date 11 avril 2026
# @author DekkrixX
##
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
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
    main "${@}"
fi
