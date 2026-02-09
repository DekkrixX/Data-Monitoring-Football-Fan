#!/bin/bash
#
# Script Desinstallation Complete - Monitoring Football
#

set -e

echo ""
echo "================================================================"
echo "  Desinstallation Complete - Systeme Monitoring Football"
echo "================================================================"
echo ""

# Couleurs
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "${RED}ATTENTION: Cette operation va :${NC}"
echo "  - Arreter et supprimer les containers Docker"
echo "  - Supprimer les volumes Docker (donnees perdues)"
echo "  - Arreter Mosquitto"
echo "  - Supprimer l'environnement virtuel Python"
echo ""

read -p "Continuer? (yes/NO) " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Annule."
    exit 0
fi

echo ""
echo "${YELLOW}Desinstallation en cours...${NC}"
echo ""

# Docker
echo "→ Arret containers Docker..."
docker stop influxdb 2>/dev/null || true
docker stop grafana 2>/dev/null || true

echo "→ Suppression containers..."
docker rm influxdb 2>/dev/null || true
docker rm grafana 2>/dev/null || true

echo "→ Suppression volumes..."
docker volume rm influxdb-data 2>/dev/null || true
docker volume rm grafana-storage 2>/dev/null || true

# Mosquitto
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "→ Arret Mosquitto..."
    brew services stop mosquitto 2>/dev/null || true
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "→ Arret Mosquitto..."
    sudo systemctl stop mosquitto 2>/dev/null || true
fi

# Environnement virtuel
echo "→ Suppression environnement virtuel..."
rm -rf stade_env 2>/dev/null || true
rm -rf venv 2>/dev/null || true

# Fichiers temporaires
echo "→ Nettoyage fichiers temporaires..."
rm -f MEMO_UTILISATION.txt 2>/dev/null || true

echo ""
echo "${GREEN}Desinstallation terminee${NC}"
echo ""
echo "Pour reinstaller, lancez:"
echo "  ./install_complete.sh"
echo ""
