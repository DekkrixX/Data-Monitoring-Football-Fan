chip=esp32s3; # Chip de la carte à flasher

function waitForPort()
{
    # Attend l'ouverture du port
    while [ ! -e "$port" ];
    do
        sleep 1;
    done;
    sleep 2;

    return ;
}

function mesh()
{
    # Execute le commande meshtastic
    .venv/meshtastic-env/bin/meshtastic --port $port $@ || true;
    waitForPort;

    return ;
}

function flashFirmware()
{
    # Flash le firmware Meshtastic
    .venv/meshtastic-env/bin/esptool --chip $chip --port $port --baud 921600 write-flash -z 0x0 .Flash/firmware-seeed-xiao-s3-2.7.15.567b8ea.bin;

    return ;
}

function flashConfiguration()
{
    # Configure Meshtastic
    mesh --set bluetooth.enabled true # Bluetooth
    mesh --set network.wifi_enabled false # WiFi
    mesh --set range_test.enabled false # Test de porté
    #mesh --set range_test.save true # Sauvegarde des tests de porté
    #mesh --set range_test.sender 60 # Interval de test en seconde
    mesh --set position.gps_enabled false # GPS
    mesh --set position.gps_mode DISABLED # Mode du GPS
    mesh --set serial.enabled true # Communication série
    mesh --set serial.baud BAUD_115200 # Baudrate
    mesh --set serial.rxd 44 # Pin RX
    mesh --set serial.txd 43 # Pin TX
    mesh --set serial.echo false # Renvoi des packets reçu
    mesh --set serial.mode TEXTMSG # Transmission de text par UART
    mesh --set lora.region EU_868 # Bande de fréquence
    mesh --set lora.modem_preset LONG_FAST # Porté et débit
    mesh --set lora.use_preset true # Utilisation du preset
    mesh --set lora.tx_power 14 # Puissance de transmission en dBm
    mesh --set lora.hop_limit 3 # Limite du nombre de retransmission d'un message par les autres noeuds
    mesh --set lora.override_duty_cycle false # Dépassement du duty cycle
    # Cannal de communication
    mesh --ch-index 1 --ch-set name "monitoring"
    mesh --ch-index 1 --ch-set psk default
    if [ "$node_type" = "gateway" ];
    then
        # Cannal de communication
        mesh --ch-index 1 --ch-set uplink_enabled false
        mesh --ch-index 1 --ch-set downlink_enabled true
        mesh --set device.role CLIENT_MUTE # Rôle du noeud
    fi
    if [ "$node_type" = "sensor" ];
    then
        # Cannal de communication
        mesh --ch-index 1 --ch-set uplink_enabled true
        mesh --ch-index 1 --ch-set downlink_enabled false
        mesh --set device.role CLIENT # Rôle du noeud
    fi
    mesh --set power.is_power_saving true # Économie d'énergie

    return ;
}

function displayNodeTypeSupported()
{
    echo "Type de noeud supporté :";
    echo "   - gateway";
    echo "   - sensor";
    echo "";

    return ;
}

function isNodeTypeSupported()
{
    case "$node_type" in
        gateway|sensor)
            valide=0;;
        *)
            valide=1;;
    esac

    return $valide;
}

foundACM=0;
foundUSB=0;

# Vérifie si au moins un port série ACM est ouvert
for port in /dev/ttyACM*;
do
    [ -e "$port" ] && { foundACM=1; break; };
done;

# Vérifie si au moins un port série USB est ouvert
for port in /dev/ttyUSB*;
do
    [ -e "$port" ] && { foundUSB=1; break; };
done;

if [ $foundACM -eq 0 ] && [ $foundUSB -eq 0 ];
then
    # Si aucun port série est ouvert
    echo "Aucun port série USB n'est ouvert.";
else
    # Sinon au moins un port série est ouvert
    echo "Liste des ports série USB";
    [ $foundACM -gt 0 ] && ls /dev/ttyACM* 2>/dev/null;
    [ $foundUSB -gt 0 ] && ls /dev/ttyUSB* 2>/dev/null;
fi;

echo "Sélectionner le port série USB correspondant à la carte à flasher";
echo -n "> "
read port;

# Vérifie que le port série sélectionné est ouvert
if [ -e $port ];
then
    # Si le port série sélectionné est ouvert
    echo "";
    echo "Voulez vous flasher la carte sur le port série USB '$port' ? [O/N]";
    read answer;

    if [ $answer = 'O' ] || [ $answer = 'o' ];
    then
        # Si l'utilisateur réponds 'OUI'
        echo "";

        echo "Que voulez vous flash (firmware/configuration) ?";
        echo -n "> ";
        read choice;

        case "$choice" in
        firmware)
            # Si l'utilisateur réponds 'firmware'
            echo "";

            # Flash du firmware
            flashFirmware;;

        configuration)
            # Si l'utilisateur réponds 'configuration'
            echo "";

            displayNodeTypeSupported;
            echo "Sélectionner le type de noeud à configurer :";
            echo -n "> ";
            read node_type;

            # Vérifie que le type de noeud est supporté
            if isNodeTypeSupported;
            then
                # Flash de la carte
                flashConfiguration;
                # Redémarrage
                mesh --reboot
            else
                echo "Type de noeud non supporté.";
            fi;;

            *)
                # Si l'utilisateur réponds autre chose
                echo "";
                echo "Flash invalide. Commande annulé.";;
        esac

    else
        # Sinon l'utilisateur réponds 'NON'
        echo "Flash de la carte sur le port série USB '$port' annulé.";
    fi;
else
    # Sinon le port série sélectionné est fermé
    echo "Le port série USB sélectionné n'est plus ouvert.";
fi;
