#!/bin/bash
#
# Script Installation Complete - Monitoring Football
# Nettoie anciennes installations et reinstalle proprement
#

set -e

echo ""
echo "================================================================"
echo "  Installation Complete - Systeme Monitoring Football"
echo "  (Nettoyage + Reinstallation)"
echo "================================================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detection OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "${GREEN}OS detecte : macOS${NC}"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "${GREEN}OS detecte : Linux${NC}"
else
    echo "${RED}OS non supporte : $OSTYPE${NC}"
    exit 1
fi

echo ""
echo "----------------------------------------------------------------"
echo ""

# ================================================================
# ETAPE 0: NETTOYAGE
# ================================================================

echo "${YELLOW}[0/6] Nettoyage des anciennes installations...${NC}"
echo ""

# Arreter et supprimer anciens containers Docker
echo "→ Nettoyage containers Docker..."
docker stop influxdb 2>/dev/null || true
docker rm influxdb 2>/dev/null || true
docker stop grafana 2>/dev/null || true
docker rm grafana 2>/dev/null || true

# Supprimer volumes Docker (ATTENTION: supprime donnees!)
read -p "Supprimer les donnees InfluxDB/Grafana existantes? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "→ Suppression volumes Docker..."
    docker volume rm influxdb-data 2>/dev/null || true
    docker volume rm grafana-storage 2>/dev/null || true
    echo "${GREEN}Volumes supprimes${NC}"
else
    echo "${YELLOW}Volumes conserves (donnees preservees)${NC}"
fi

# Nettoyer anciens environnements virtuels Python
if [ -d "venv" ]; then
    echo "→ Suppression ancien environnement virtuel..."
    rm -rf venv
fi

if [ -d "stade_env" ]; then
    echo "→ Suppression ancien environnement virtuel stade_env..."
    rm -rf stade_env
fi

echo "${GREEN}Nettoyage termine${NC}"
echo ""

# ================================================================
# ETAPE 1: MOSQUITTO
# ================================================================

echo "${YELLOW}[1/6] Installation Mosquitto (Broker MQTT)...${NC}"
echo ""

if [[ "$OS" == "macos" ]]; then
    if ! command -v brew &> /dev/null; then
        echo "${RED}Homebrew requis mais non installe${NC}"
        echo "Installer depuis : https://brew.sh"
        exit 1
    fi
    
    # Verifier si deja installe
    if brew list mosquitto &>/dev/null; then
        echo "→ Mosquitto deja installe"
        brew services restart mosquitto
    else
        echo "→ Installation via Homebrew..."
        brew install mosquitto
        brew services start mosquitto
    fi
    
elif [[ "$OS" == "linux" ]]; then
    echo "→ Mise a jour des paquets..."
    sudo apt update -qq
    
    echo "→ Installation de Mosquitto..."
    sudo apt install -y mosquitto mosquitto-clients
    
    echo "→ Demarrage de Mosquitto..."
    sudo systemctl restart mosquitto
    sudo systemctl enable mosquitto
fi

echo ""
echo "${GREEN}Mosquitto installe et actif${NC}"
echo "   Port      : localhost:1883"
echo ""

# ================================================================
# ETAPE 2: DOCKER
# ================================================================

echo "${YELLOW}[2/6] Verification Docker...${NC}"
echo ""

if ! command -v docker &> /dev/null; then
    echo "${RED}Docker requis mais non installe${NC}"
    echo ""
    echo "Installation Docker :"
    echo "  macOS   : brew install --cask docker"
    echo "  Linux   : https://docs.docker.com/engine/install/"
    echo ""
    exit 1
fi

echo "${GREEN}Docker disponible${NC}"
docker --version
echo ""

# ================================================================
# ETAPE 3: INFLUXDB
# ================================================================

echo "${YELLOW}[3/6] Installation InfluxDB...${NC}"
echo ""

echo "→ Creation du container InfluxDB..."
docker run -d \
  --name influxdb \
  --restart unless-stopped \
  -p 8086:8086 \
  -v influxdb-data:/var/lib/influxdb2 \
  -e DOCKER_INFLUXDB_INIT_MODE=setup \
  -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
  -e DOCKER_INFLUXDB_INIT_PASSWORD=adminadmin \
  -e DOCKER_INFLUXDB_INIT_ORG=football \
  -e DOCKER_INFLUXDB_INIT_BUCKET=heartrate \
  -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=stade-token-123456789 \
  influxdb:2.7

echo "→ Attente demarrage InfluxDB..."
for i in {1..30}; do
    if curl -s http://localhost:8086/health > /dev/null 2>&1; then
        echo ""
        echo "${GREEN}InfluxDB operationnel${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "   URL       : http://localhost:8086"
echo "   Login     : admin / adminadmin"
echo "   Token     : stade-token-123456789"
echo "   Org       : football"
echo "   Bucket    : heartrate"
echo ""

# ================================================================
# ETAPE 4: GRAFANA
# ================================================================

echo "${YELLOW}[4/6] Installation Grafana...${NC}"
echo ""

echo "→ Creation du container Grafana..."
docker run -d \
  --name grafana \
  --restart unless-stopped \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana:latest

echo "→ Attente demarrage Grafana..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo ""
        echo "${GREEN}Grafana operationnel${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "   URL       : http://localhost:3000"
echo "   Login     : admin / admin"
echo ""

# ================================================================
# ETAPE 5: ENVIRONNEMENT VIRTUEL PYTHON
# ================================================================

echo "${YELLOW}[5/6] Creation environnement virtuel Python...${NC}"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "${RED}Python 3 requis mais non installe${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "→ Python trouve : $PYTHON_VERSION"

# Creer environnement virtuel
echo "→ Creation environnement virtuel 'stade_env'..."
python3 -m venv stade_env

# Activer environnement
echo "→ Activation environnement virtuel..."
source stade_env/bin/activate

# Mettre a jour pip
echo "→ Mise a jour pip..."
pip install --upgrade pip --quiet

echo "${GREEN}Environnement virtuel cree et active${NC}"
echo ""

# ================================================================
# ETAPE 6: DEPENDANCES PYTHON
# ================================================================

echo "${YELLOW}[6/6] Installation dependances Python...${NC}"
echo ""

echo "→ Installation des packages Python..."
if [[ "$OS" == "macos" ]]; then
    # macOS necessite parfois --break-system-packages
    # Mais dans venv, pas necessaire
    pip install pyserial paho-mqtt influxdb-client meshtastic pypubsub flask flask-socketio matplotlib numpy
else
    pip install pyserial paho-mqtt influxdb-client meshtastic pypubsub flask flask-socketio matplotlib numpy
fi

echo ""
echo "${GREEN}Dependances Python installees${NC}"
echo "   Packages :"
echo "   - pyserial        (communication serie USB)"
echo "   - paho-mqtt       (client MQTT)"
echo "   - influxdb-client (client InfluxDB)"
echo "   - meshtastic      (API Meshtastic)"
echo "   - pypubsub        (systeme messages)"
echo "   - flask           (serveur web)"
echo "   - flask-socketio  (WebSocket)"
echo "   - matplotlib      (graphiques)"
echo "   - numpy           (calculs)"
echo ""

# ================================================================
# VERIFICATION FINALE
# ================================================================

echo "================================================================"
echo ""
echo "${GREEN}INSTALLATION TERMINEE AVEC SUCCES${NC}"
echo ""
echo "================================================================"
echo ""
echo "Services installes et actifs :"
echo "  ${GREEN}✓${NC} Mosquitto (MQTT)     → localhost:1883"
echo "  ${GREEN}✓${NC} InfluxDB             → localhost:8086"
echo "  ${GREEN}✓${NC} Grafana              → localhost:3000"
echo "  ${GREEN}✓${NC} Python venv          → stade_env/"
echo ""
echo "----------------------------------------------------------------"
echo ""
echo "${YELLOW}IMPORTANT - Environnement Virtuel${NC}"
echo ""
echo "Pour utiliser les scripts Python, TOUJOURS activer l'environnement :"
echo ""
echo "  ${GREEN}source stade_env/bin/activate${NC}"
echo ""
echo "Vous verrez (stade_env) avant le prompt:"
echo "  (stade_env) user@mac project %"
echo ""
echo "Pour desactiver:"
echo "  ${YELLOW}deactivate${NC}"
echo ""
echo "----------------------------------------------------------------"
echo ""
echo "${YELLOW}Prochaines etapes :${NC}"
echo ""
echo "1. Recuperer le token InfluxDB :"
echo "   ${GREEN}http://localhost:8086${NC}"
echo "   → Login: admin / adminadmin"
echo "   → Load Data > API Tokens > Copier le token"
echo ""
echo "2. Editer mqtt_to_influxdb.py :"
echo "   ${GREEN}nano mqtt_to_influxdb.py${NC}"
echo "   → Ligne ~30: INFLUX_TOKEN = 'votre-token-copie'"
echo ""
echo "3. Trouver le port USB du Gateway Meshtastic :"
echo "   ${GREEN}ls /dev/cu.usbmodem*${NC}  (macOS)"
echo "   ${GREEN}ls /dev/ttyUSB*${NC}       (Linux)"
echo ""
echo "4. Editer meshtastic_to_mqtt.py :"
echo "   ${GREEN}nano meshtastic_to_mqtt.py${NC}"
echo "   → Ligne ~25: SERIAL_PORT = '/dev/cu.usbmodem...'"
echo ""
echo "5. Lancer les scripts (dans 3 terminaux) :"
echo ""
echo "   Terminal 1:"
echo "   ${GREEN}source stade_env/bin/activate${NC}"
echo "   ${GREEN}python3 meshtastic_to_mqtt.py${NC}"
echo ""
echo "   Terminal 2:"
echo "   ${GREEN}source stade_env/bin/activate${NC}"
echo "   ${GREEN}python3 mqtt_to_influxdb.py${NC}"
echo ""
echo "   Terminal 3:"
echo "   ${GREEN}source stade_env/bin/activate${NC}"
echo "   ${GREEN}python3 web_dashboard.py${NC}"
echo ""
echo "6. Ouvrir le dashboard :"
echo "   ${GREEN}http://localhost:5001${NC}"
echo ""
echo "================================================================"
echo ""
echo "${GREEN}Bon match !${NC}"
echo ""

# Creer fichier memo
cat > MEMO_UTILISATION.txt << 'ENDMEMO'
================================================================
MEMO UTILISATION - Systeme Monitoring Football
================================================================

ACTIVER ENVIRONNEMENT VIRTUEL (A FAIRE A CHAQUE FOIS)
------------------------------------------------------
source stade_env/bin/activate

Vous verrez: (stade_env) avant le prompt


LANCER LE SYSTEME (3 terminaux)
--------------------------------
Terminal 1:
  source stade_env/bin/activate
  python3 meshtastic_to_mqtt.py

Terminal 2:
  source stade_env/bin/activate
  python3 mqtt_to_influxdb.py

Terminal 3:
  source stade_env/bin/activate
  python3 web_dashboard.py


ACCES INTERFACES
----------------
Dashboard   : http://localhost:5001
Grafana     : http://localhost:3000 (admin/admin)
InfluxDB    : http://localhost:8086 (admin/adminadmin)


VERIFICATIONS
-------------
# Mosquitto actif?
brew services list | grep mosquitto  (macOS)
systemctl status mosquitto           (Linux)

# Docker containers actifs?
docker ps

# Port USB Gateway?
ls /dev/cu.usbmodem*  (macOS)
ls /dev/ttyUSB*       (Linux)

# Test MQTT?
mosquitto_sub -h localhost -t "#" -v


ARRETER LE SYSTEME
------------------
Ctrl+C dans chaque terminal
deactivate  (pour sortir du venv)


REDEMARRER SERVICES
-------------------
# Mosquitto
brew services restart mosquitto  (macOS)
sudo systemctl restart mosquitto (Linux)

# Docker
docker restart influxdb grafana


DESINSTALLATION COMPLETE
-------------------------
./uninstall.sh  (si cree)

Ou manuellement:
  docker stop influxdb grafana
  docker rm influxdb grafana
  docker volume rm influxdb-data grafana-storage
  brew services stop mosquitto  (macOS)
  rm -rf stade_env/

================================================================
ENDMEMO

echo "${GREEN}Fichier memo cree : MEMO_UTILISATION.txt${NC}"
echo ""
