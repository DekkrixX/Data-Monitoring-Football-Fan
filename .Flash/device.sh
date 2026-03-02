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
    echo "Voulez vous flasher la carte sur le port série USB '$port' ? [O/N]";
    read answer;

    if [ "$answer" = "O" ] || [ "$answer" = "o" ];
    then
        # Si l'utilisateur réponds 'OUI'
        echo "";
        # Flash de la carte
        .venv/platformio-env/bin/pio run -t upload --upload-port $port --project-dir Device;
    else
        # Sinon l'utilisateur réponds 'NON'
        echo "Flash de la carte sur le port série USB '$port' annulé.";
    fi;
else
    # Sinon le port série sélectionné est fermé
    echo "Le port série USB sélectionné n'est plus ouvert.";
fi;
