##
# @file run.sh
#
# @brief Lance le test de distance.
#
# @see out.sh
# @see Fonction usage() ou lancer le script avec --help
##

# =============================================================================
#  Import
# =============================================================================

source "$(dirname "${BASH_SOURCE[0]}")/../../Script/out.sh"

# =============================================================================
#  Code de sortie
# =============================================================================

argumentErrorCode=1             ##< @brief Arguments manquants ou invalides.
portNotFoundErrorCode=2         ##< @brief Port série introuvable.
targetNotSupportErrorCode=3     ##< @brief Cible non supporté.
choiceNotSupportErrorCode=4     ##< @brief Choix non supporté.
nodeTypeNotSupportErrorCode=5   ##< @brief Type de noeud non supporté.
sensorTypeNotSupportErrorCode=6 ##< @brief Type de capteur non supporté.

# =============================================================================
#  Flag
# =============================================================================

VERBOSE=0 ##< @brief Mode verbeux (désactivé par défaut, activé par -v / --verbose).

# =============================================================================
#  Variable globale
# =============================================================================

path="$(dirname "${BASH_SOURCE[0]}")/../.." ##< @brief Chemin du projet.
port=""                                     ##< @brief Port série à utilisé.
step="R"                                    ##< @brief Code de retour de l'étape.

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
    echo -e "\t\tExemple: ${name} --verbose file.log"
    echo ""
    echo -e "${_WHITE}ARGUMENTS${_RESET}"
    echo -e "\t<cible>"
    echo -e "\t\tNom de la cible à flahser."
    echo -e "\t\tExemple: ${name} device"

    return
}

# =============================================================================
#  Configuration Meshtastic
# =============================================================================

##
# @brief Raccourci de la commande pour la configuration de Meshtastic.
##
function mesh()
{
    # Execute le commande meshtastic
    until "${path}/.venv/meshtastic-env/bin/meshtastic" --port "${port}" "$@"
    do
        debug "Échec de la commande."
        debug "Nouvelle tentative."
        sleep 2
    done

    sleep 2

    return
}



##
# @brief Flash la configuration Meshtastic.
#
# @param nodeType   Type de noeud à configurer.
# @param sensorType Type de capteur à configurer.
##
function flashConfiguration()
{
    local nodeType="${1}"
    local preset="${2}"

    debug "Configuration Bluetooth."
    mesh --set bluetooth.enabled false # Bluetooth
    mesh --reboot
    sleep 11
    debug "Configuration série"
    mesh --set serial.rxd 44 # Pin RX
    mesh --set serial.txd 43 # Pin TX
    mesh --set serial.baud BAUD_115200 # Baudrate
    mesh --set serial.mode TEXTMSG # Transmission de text par UART
    mesh --set serial.enabled true # Communication série
    mesh --reboot
    sleep 11
    debug "Configuration LoRa."
    mesh --set lora.region EU_868 # Bande de fréquence
    mesh --set lora.modem_preset "${preset}" # Porté et débit
    mesh --set lora.tx_power 14 # Puissance de transmission en dBm
    mesh --set lora.hop_limit 3 # Limite du nombre de retransmission d'un message par les autres noeuds
    mesh --reboot
    sleep 11
    debug "Configuration des channels."
    mesh --ch-index 0 --ch-set psk "base64:5BqoFn2cuaQFHcqnRSKANEvnt2naVyf5G51tfFkXIYA="
    mesh --ch-index 0 --ch-set name "monitoring"
    mesh --reboot
    sleep 11
    debug "Configuration du device"
    if [ "${nodeType}" = "gateway" ]
    then
        mesh --set device.role CLIENT_MUTE # Rôle du noeud
    fi
    if [ "${nodeType}" = "sensor" ]
    then
        mesh --set device.role CLIENT # Rôle du noeud
    fi
    mesh --reboot
    sleep 11
    debug "Configuration de l'économie d'énergie."
    mesh --set power.is_power_saving true # Économie d'énergie
    mesh --reboot
    sleep 11

    return
}

# =============================================================================
#  Fonctions métier
# =============================================================================

##
# @brief Affiche la boîte de dialogue pour la sélection du port série.
##
function selectPort()
{
    local foundACM=0
    local foundUSB=0

    # Vérifie si au moins un port série ACM est ouvert
    for port in /dev/ttyACM*
    do
        [ -e "${port}" ] && { foundACM=1; break; }
    done

    # Vérifie si au moins un port série USB est ouvert
    for port in /dev/ttyUSB*
    do
        [ -e "${port}" ] && { foundUSB=1; break; }
    done

    if [ "${foundACM}" -eq 0 ] && [ "${foundUSB}" -eq 0 ]
    then
        # Si aucun port série est ouvert
        echo "Aucun port série USB n'est ouvert." >&2
    else
        # Sinon au moins un port série est ouvert
        echo "Liste des ports série USB :" >&2
        [ "${foundACM}" -gt 0 ] && ls /dev/ttyACM*
        [ "${foundUSB}" -gt 0 ] && ls /dev/ttyUSB*
    fi

    echo "Sélectionner le port série USB correspondant à la carte à flasher" >&2
    echo -n "> " >&2
    read port

    return
}



##
# @brief Affiche la boîte de dialogue pour la sélection du choix.
##
function selectChoice()
{
    echo "Que voulez vous flash (firmware/configuration) ?" >&2
    echo -n "> " >&2
    read choice

    echo "${choice}"

    return
}



##
# @brief Affiche la boîte de dialogue pour la sélection du type de noeud Meshtastic.
##
function selectNodeType()
{
    echo "Quelle est le type de noeud à configurer (gateway/sensor) ?" >&2
    echo -n "> " >&2
    read nodeType

    echo "${nodeType}"

    return
}



##
# @brief Affiche la boîte de dialogue pour la sélection de type de test.
##
function selectTestOption()
{
    echo "Quelle est le type de test à configurer (LONG_FAST/MEDIUM_FAST/SHORT_FAST/SHORT_TURBO) ?" >&2
    echo -n "> " >&2
    read testOptionType

    echo "${testOptionType}"

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

    local target="${1}"

    case "${target}" in
        # Flash du device
        device)
            selectPort

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
                "${path}"/.venv/platformio-env/bin/pio run -t erase --upload-port "${port}" --project-dir Tests/DistanceDevice
                # Flash de la carte
                "${path}"/.venv/platformio-env/bin/pio run -t upload --upload-port "${port}" --project-dir Tests/Distance/Device
            else
                error "${portNotFoundErrorCode}" "Le port série '${port}' sélectionné n'est pas ouvert."
            fi
            ;;

        # Flash de Meshtastic
        meshtastic)
            local chip="esp32s3" # Chip de la carte à flasher
            selectPort

            # Vérifie l'installation de l'environnement virtuel
            if [ ! -e "${path}/.venv/meshtastic-env" ]
            then
                info "Installation de l'environnement virtuel 'platformio-env'"
                debug "Package: Python3"
                sudo apt install -y python3
                debug "Package: Python3-venv"
                sudo apt install -y python3-venv
                debug "Création des environnements virtuels python"
                mkdir -p "${path}/.venv"
                debug "Environement virtuel: Meshtastic"
                python3 -m venv "${path}/.venv/meshtastic-env"
                debug "Package: Meshtastic"
                "${path}"/.venv/meshtastic-env/bin/pip install meshtastic
                debug "Package: ESPtool"
                "${path}"/.venv/meshtastic-env/bin/pip install esptool
            fi

            # Vérifie que le port série sélectionné est ouvert
            if [ -e "${port}" ]
            then
                debug "Flash de Meshtastic."

                local choice=$(selectChoice)
                case "${choice}" in
                    # Flash le firmware Meshtastic
                    firmware)
                        info "Flash du firmware"
                        "${path}"/.venv/meshtastic-env/bin/esptool --chip "${chip}" --port "${port}" --baud 921600 erase-flash
                        "${path}"/.venv/meshtastic-env/bin/esptool --chip "${chip}" --port "${port}" --baud 921600 write-flash -z 0x0 "${path}/.Flash/firmware-seeed-xiao-s3-2.7.15.567b8ea.bin"
                        ;;

                    # Flash de la configuration Meshtastic
                    configuration)
                        debug "Flash de la configuration de Meshtastic."

                        local testOptionType=$(selectTestOption)
                        case "${testOptionType}" in
                        	LONG_FAST | MEDIUM_FAST | SHORT_FAST | SHORT_TURBO)
                        		debug "Option de test sélectionné ${testOptionType}"
                        		;;

                        	*)
                        		testOptionType="LONG_FAST"
                        		;;
                        esac

                        local nodeType=$(selectNodeType)
                        case "${nodeType}" in
                            # Flash de la configuration de la gateway Meshtastic
                            gateway)
                                info "Flash de la configuration de la gateway."
                                flashConfiguration "gateway" "${testOptionType}"
                                ;;

                            # Flash de la configuration d'un capteur Meshtastic
                            sensor)
                                info "Flash de la configuration d'un capteur."
                                flashConfiguration "sensor" "${testOptionType}"
                                ;;

                            *)
                                error "${nodeTypeNotSupportErrorCode}" "Le type de noeud '${nodeType}' sélectionné n'est pas supporté."
                                ;;
                        esac
                        ;;

                    *)
                        error "${choiceNotSupportErrorCode}" "Le choix '${choice}' sélectionné n'est pas supporté."
                        ;;
                    esac
            fi
            ;;

        *)
            error "${targetNotSupportErrorCode}" "La cible '${target}' sélectionné n'est pas supporté."
            ;;
    esac

    return
}

# Lancement du script avec tous les arguments
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
    main "${@}"
fi
