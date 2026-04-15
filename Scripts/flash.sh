#!/bin/bash

# Couleurs
_NO_COLOR="\033[0m"
_WHITE="\033[1;37m"
_MAGENTA="\033[1;35m"
_RED="\033[1;31m"

# Dossiers
DFLASH=".Flash"
DFLASH_TEST="Tests/Distance/Flash"

# Chargement du .env si présent
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Vérification TARGET
if [ -z "$1" ]; then
    echo -e "${_WHITE}Usage du flash:${_NO_COLOR}"
    echo -e "   ${_MAGENTA}.${0} <cible>${_NO_COLOR}"
    echo ""
    echo -e "${_WHITE}Cibles:${_NO_COLOR}"
    echo "   - device : Flash le programme du device"
    echo "   - meshtastic : Flash la configuration Meshtastic"
    exit 1
fi

# Choix du script
if [ "$TEST" = "1" ]; then
    FLASH_SCRIPT="${DFLASH_TEST}/${TARGET}.sh"
else
    FLASH_SCRIPT="${DFLASH}/${TARGET}.sh"
fi

# Vérification existence script
if [ ! -f "$FLASH_SCRIPT" ]; then
    echo -e "${_RED}Erreur : script introuvable -> $FLASH_SCRIPT${_NO_COLOR}"
    exit 1
fi

# Exécution
echo -e "${_WHITE}Exécution du script:${_NO_COLOR} $FLASH_SCRIPT"
bash "$FLASH_SCRIPT"
