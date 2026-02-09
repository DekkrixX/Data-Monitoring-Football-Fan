#!/bin/bash
#
# Script de Configuration Meshtastic 
# Gère automatiquement les déconnexions et redémarrages
#

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
MAX_RETRIES=5
RECONNECT_DELAY=15

print_step() {
    echo -e "${BLUE}[ÉTAPE]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Fonction pour trouver le port
find_port() {
    local max_wait=30
    local waited=0
    
    while [ $waited -lt $max_wait ]; do
        if [[ "$OSTYPE" == "darwin"* ]]; then
            PORTS=$(ls /dev/cu.usbmodem* 2>/dev/null || true)
        else
            PORTS=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true)
        fi
        
        if [ -n "$PORTS" ]; then
            PORT=$(echo "$PORTS" | head -n 1)
            echo "$PORT"
            return 0
        fi
        
        sleep 1
        waited=$((waited + 1))
    done
    
    return 1
}

# Fonction pour attendre que le device soit prêt
wait_device_ready() {
    local port="$1"
    local max_wait=30
    local waited=0
    
    while [ $waited -lt $max_wait ]; do
        if meshtastic --port "$port" --info >/dev/null 2>&1; then
            return 0
        fi
        
        sleep 1
        waited=$((waited + 1))
    done
    
    return 1
}

# Fonction pour exécuter une commande avec retry
execute_with_retry() {
    local retry=0
    
    while [ $retry -lt $MAX_RETRIES ]; do
        # Essayer la commande
        if meshtastic "$@" >/dev/null 2>&1; then
            return 0
        fi
        
        # Échec
        retry=$((retry + 1))
        
        if [ $retry -lt $MAX_RETRIES ]; then
            print_warning "Échec (tentative $retry/$MAX_RETRIES) - Reconnexion..."
            sleep $RECONNECT_DELAY
            
            # Chercher le nouveau port
            NEW_PORT=$(find_port)
            if [ -n "$NEW_PORT" ]; then
                SERIAL_PORT="$NEW_PORT"
                print_success "Port détecté : $SERIAL_PORT"
                
                # Attendre device prêt
                if wait_device_ready "$SERIAL_PORT"; then
                    print_success "Device prêt - Nouvelle tentative"
                    
                    # Reconstruire les arguments avec le nouveau port
                    local new_args=()
                    for arg in "$@"; do
                        if [[ $arg == /dev/* ]]; then
                            new_args+=("$SERIAL_PORT")
                        else
                            new_args+=("$arg")
                        fi
                    done
                    
                    # Essayer avec les nouveaux arguments
                    if meshtastic "${new_args[@]}" >/dev/null 2>&1; then
                        return 0
                    fi
                fi
            fi
        fi
    done
    
    print_error "Échec après $MAX_RETRIES tentatives"
    return 1
}

configure_serial() {
    print_step "Configuration Serial/UART..."
    
    execute_with_retry --port "$SERIAL_PORT" --set serial.enabled true
    print_success "Serial activé"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set serial.rxd 44
    print_success "RXD : GPIO 44"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set serial.txd 43
    print_success "TXD : GPIO 43"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set serial.baud BAUD_115200
    print_success "Baud : 115200"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set serial.mode TEXTMSG
    print_success "Mode : TEXTMSG"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set serial.echo false
    print_success "Echo désactivé"
    sleep 5
    
    echo ""
}

configure_device() {
    print_step "Configuration Device..."
    
    execute_with_retry --port "$SERIAL_PORT" --set device.role CLIENT
    print_success "Role : CLIENT"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set device.node_info_broadcast_secs 10800
    print_success "Node info : 3 heures"
    sleep 3
    
    echo ""
}

configure_position() {
    print_step "Configuration Position..."
    
    execute_with_retry --port "$SERIAL_PORT" --set position.gps_enabled false
    print_success "GPS désactivé"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set position.position_broadcast_secs 0
    print_success "Position broadcast désactivé"
    sleep 3
    
    echo ""
}

configure_power() {
    print_step "Configuration Power..."
    
    execute_with_retry --port "$SERIAL_PORT" --set power.is_power_saving false
    print_success "Power saving désactivé"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set power.wait_bluetooth_secs 60
    print_success "Wait Bluetooth : 60s"
    sleep 3
    
    echo ""
}

configure_bluetooth() {
    print_step "Configuration Bluetooth..."
    
    execute_with_retry --port "$SERIAL_PORT" --set bluetooth.enabled true
    print_success "Bluetooth activé"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set bluetooth.mode FIXED_PIN
    print_success "Mode : FIXED_PIN"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set bluetooth.fixed_pin 123456
    print_success "PIN : 123456"
    sleep 3
    
    echo ""
}

configure_modules() {
    print_step "Configuration Modules..."
    
    execute_with_retry --port "$SERIAL_PORT" --set mqtt.enabled false
    print_success "MQTT désactivé"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set telemetry.device_update_interval 0
    print_success "Telemetry désactivée"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set neighborinfo.enabled false
    print_success "Neighbor info désactivé"
    sleep 3
    
    echo ""
}

configure_lora() {
    print_step "Configuration LoRa"
    
    execute_with_retry --port "$SERIAL_PORT" --set lora.region EU_868
    print_success "Région : EU_868"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set lora.modem_preset LONG_FAST
    print_success "Preset : LONG_FAST"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set lora.hop_limit 3
    print_success "Hop limit : 3"
    sleep 3
    
    execute_with_retry --port "$SERIAL_PORT" --set lora.tx_power 27
    print_success "TX Power : 27 dBm"
    sleep 3
    
    echo ""
}

set_name() {
    if [ -n "$NODE_NAME" ]; then
        print_step "Configuration du nom..."
        
        execute_with_retry --port "$SERIAL_PORT" --set-owner "$NODE_NAME"
        print_success "Nom : $NODE_NAME"
        sleep 3
        
        echo ""
    fi
}

main() {
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  Configuration Meshtastic"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    # Vérifier meshtastic installé
    if ! command -v meshtastic &> /dev/null; then
        print_error "meshtastic CLI non installé"
        echo "Installation : pip install meshtastic"
        exit 1
    fi
    
    # Port
    if [ -n "$1" ]; then
        SERIAL_PORT="$1"
    else
        print_step "Détection automatique du port..."
        SERIAL_PORT=$(find_port)
        if [ -z "$SERIAL_PORT" ]; then
            print_error "Aucun port détecté"
            exit 1
        fi
        print_success "Port détecté : $SERIAL_PORT"
    fi
    
    # Type de noeud
    if [ -n "$2" ]; then
        NODE_TYPE="$2"
    else
        echo ""
        echo "Type de noeud :"
        echo "  1) Gateway"
        echo "  2) Sensor"
        echo ""
        read -p "Choix [1-2] : " choice
        case $choice in
            1) NODE_TYPE="gateway" ;;
            2) NODE_TYPE="sensor" ;;
            *) NODE_TYPE="sensor" ;;
        esac
    fi
    
    # Nom
    echo ""
    read -p "Nom personnalisé (optionnel) : " NODE_NAME
    
    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo "Configuration : $NODE_TYPE"
    [ -n "$NODE_NAME" ] && echo "Nom         : $NODE_NAME"
    echo "Port        : $SERIAL_PORT"
    echo "────────────────────────────────────────────────────────────────"
    echo ""
    
    read -p "Confirmer? (y/N) : " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Annulé"
        exit 0
    fi
    
    # Vérifier connexion
    print_step "Vérification connexion..."
    if ! wait_device_ready "$SERIAL_PORT"; then
        print_error "Device non accessible"
        exit 1
    fi
    print_success "Device prêt"
    echo ""
    
    # Configuration complète
    configure_serial
    configure_device
    configure_position
    configure_power
    configure_bluetooth
    configure_modules
    set_name
    configure_lora
    
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${GREEN}  ✓ Configuration terminée avec succès!${NC}"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    # Redémarrage final
    read -p "Redémarrer le device? (y/N) : " reboot_choice
    if [[ $reboot_choice =~ ^[Yy]$ ]]; then
        execute_with_retry --port "$SERIAL_PORT" --reboot
        print_success "Device redémarré"
        echo ""
    fi
    
    echo "Vérification : meshtastic --port $SERIAL_PORT --info"
    echo ""
}

main "$@"
