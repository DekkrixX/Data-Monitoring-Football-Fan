################################################################################
#	Makefile écrit par Quentin GUILLEMOD                                       #
################################################################################

# Nom de la documentation
DOCNAME = DOCUMENTATION

# Chemin de la documentation
DOCPATH = Documentation/

# Fichiers de documentation
DOCFILES = $(DOCPATH)/main.md $(DOCPATH)/architecture.md $(DOCPATH)/equipment.md $(DOCPATH)/test.md $(DOCPATH)/debug.md $(DOCPATH)/development.md

# Dossier des scripts de flash
DFLASH = .Flash
# Script flash à exécuter
FLASH_SCRIPT = $(DFLASH)/$(TARGET).sh

# Définition des variables d'environnement
include .env
export
export APP_DEVICE = $(APP) - Device
export APP_SERVER = $(APP) - Server

# Définition des couleurs
_NO_COLOR = \033[m
_BLACK = \033[1;30m
_RED = \033[1;31m
_GREEN = \033[1;32m
_YELLOW = \033[1;33m
_BLUE = \033[1;34m
_MAGENTA = \033[1;35m
_CYAN = \033[1;36m
_WHITE = \033[1;37m

# Fichiers générés
GEN_FILES = $(DOCNAME).md Device/.pio Device/doc Server/**/__pycache__ Server/doc


.PHONY: server doc load run stop install remove clean help
.DEFAULT_GOAL = help

################################################################################
#	Mise en route des serveurs												   #
################################################################################
server:
	@gnome-terminal -- bash -c ".venv/server-env/bin/python3 -m Server.Bridge.bridge_Meshtastic_MQTT"
	@gnome-terminal -- bash -c ".venv/server-env/bin/python3 -m Server.Bridge.bridge_MQTT_InfluxDB"
	@gnome-terminal -- bash -c ".venv/server-env/bin/python3 -m Server.Dashboard.app"
	@echo "Liste des interfaces de visualisation des données :"
	@echo "   - Dashboard : http://localhost:$(DASHBOARD_PORT)"
	@echo "   - Grafana   : http://localhost:$(GRAFANA_PORT)"
	@echo "   - InfluxDB  : http://localhost:$(INFLUXDB_PORT)"

################################################################################
#	Création de la documentation                                               #
################################################################################
doc: doc-markdown doc-device doc-server
	@echo "$(_YELLOW)La documentation à été créée$(_NO_COLOR)"
doc-markdown:
	@pandoc $(DOCFILES) --from markdown --to markdown -o $(DOCNAME).md
doc-device:
	@doxygen Device/Doxyfile
doc-server:
	@doxygen Server/Doxyfile

################################################################################
#	Flash le code sur la carte                                                 #
################################################################################
flash:
	@if [ -z "$(TARGET)" ]; then \
		echo "$(_WHITE)Usage du flash:$(_NO_COLOR)"; \
		echo "   $(_MAGENTA)make flash TARGET=<cible>$(_NO_COLOR)"; \
		echo ""; \
		echo "$(_WHITE)Cibles:$(_NO_COLOR)"; \
		echo "   - device : Flash le programme du device"; \
		echo "   - meshtastic : Flash la configuration Meshtastic"; \
	else \
		bash $(FLASH_SCRIPT); \
	fi

################################################################################
#	Lance les serveurs locaux                                                  #
################################################################################
run:
	@echo "Lancement du broker MQTT"
	@systemctl start mosquitto
	@echo "Lancement de Docker"
	@systemctl start docker
	@echo "Lancement de InfluxDB"
	@docker run -d \
	--name influxdb \
	--restart unless-stopped \
	-p $(INFLUXDB_PORT):$(INFLUXDB_PORT) \
	-v influxdb-data:/var/lib/influxdb2 \
	-e DOCKER_INFLUXDB_INIT_MODE=setup \
	-e DOCKER_INFLUXDB_INIT_USERNAME=$(INFLUXDB_USERNAME) \
	-e DOCKER_INFLUXDB_INIT_PASSWORD=$(INFLUXDB_PASSWORD) \
	-e DOCKER_INFLUXDB_INIT_ORG=$(INFLUXDB_ORG) \
	-e DOCKER_INFLUXDB_INIT_BUCKET=$(INFLUXDB_BUCKET) \
	-e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=$(INFLUXDB_TOKEN) \
	influxdb:2.7
	@echo "Lancement de Grafana"
	@docker run -d \
	--name grafana \
	--restart unless-stopped \
	-p $(GRAFANA_PORT):$(GRAFANA_PORT) \
	-v grafana-storage:/var/lib/grafana \
	-e GF_SECURITY_ADMIN_USER=$(GRAFANA_USERNAME) \
	-e GF_SECURITY_ADMIN_PASSWORD=$(GRAFANA_PASSWORD) \
	grafana/grafana:latest

################################################################################
#	Arrête les serveurs locaux                                                 #
################################################################################
stop:
	@echo "Arrêt du broker MQTT"
	@systemctl stop mosquitto
	@echo "Arrêt de InfluxDB"
	@docker stop influxdb
	@docker rm influxdb
	@docker volume rm influxdb-data
	@echo "Arrêt de Grafana"
	@docker stop grafana
	@docker rm grafana
	@docker volume rm influxdb-storage
	@echo "Arrêt de Docker"
	@systemctl stop docker

################################################################################
#	Installe toutes les dépendances                                            #
################################################################################
install:
	@echo "Package: TeXLive"
	@sudo apt install -y texlive
	@echo "Package: Doxygen"
	@sudo apt install doxygen graphviz
	@echo "Package: Mosquitto"
	@sudo apt install -y mosquitto mosquitto-clients
	@echo "Package: Docker"
	@curl -fsSL https://get.docker.com -o get-docker.sh
	@sudo sh ./get-docker.sh
	@echo "Package: Python3"
	@sudo apt install -y python3
	@echo "Création des environnements virtuels python"
	@mkdir -p .venv
	@echo "Environnement virtuel: PlatformIO"
	@python3 -m venv .venv/platformio-env
	@echo "Package: PlatformIO"
	@.venv/platformio-env/bin/pip install platformio
	@echo "Environement virtuel: Serveur"
	@python3 -m venv .venv/server-env
	@echo "Package: PySerial"
	@.venv/server-env/bin/pip install pyserial
	@echo "Package: MQTT"
	@.venv/server-env/bin/pip install paho-mqtt
	@echo "Package: InfluxDB"
	@.venv/server-env/bin/pip install influxdb-client
	@echo "Package: Meshtastic"
	@.venv/server-env/bin/pip install meshtastic
	@echo "Package: Pypubsub"
	@.venv/server-env/bin/pip install pypubsub
	@echo "Package: Flask"
	@.venv/server-env/bin/pip install flask flask-socketio
	@echo "Package: Matplotlib"
	@.venv/server-env/bin/pip install matplotlib
	@echo "Package: Numpy"
	@.venv/server-env/bin/pip install numpy
	@echo "Package: dotenv"
	@.venv/server-env/bin/pip install python-dotenv
	@echo "Environement virtuel: Meshtastic"
	@python3 -m venv .venv/meshtastic-env
	@echo "Package: Meshtastic"
	@.venv/meshtastic-env/bin/pip install meshtastic
	@echo "Package: ESPtool"
	@.venv/meshtastic-env/bin/pip install esptool
	@echo "$(_YELLOW)Toutes les dépendances ont été installées$(_NO_COLOR)"

################################################################################
#	Supprime toutes les dépendances                                            #
################################################################################
remove:
	@echo "Package: TeXLive"
	@sudo apt remove -y texlive
	@echo "Package: Doxygen"
	@sudo apt remove doxygen graphviz
	@echo "Package: mosquitto"
	@sudo apt remove -y mosquitto mosquitto-clients
	@echo "Package: docker"
	@sudo apt purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras
	@sudo rm -rf /var/lib/docker
	@sudo rm -rf /var/lib/containerd
	@sudo rm /etc/apt/sources.list.d/docker.sources
	@sudo rm /etc/apt/keyrings/docker.asc
	@echo "Package: python3"
	@sudo apt remove -y python3
	@echo "Suppression des environnements virtuels python"
	@rm -rf .venv
	@echo "$(_YELLOW)Toutes les dépendances ont été supprimées$(_NO_COLOR)"

################################################################################
#	Nettoie l'environnement de dévelopement                                     #
################################################################################
clean:
	@bash -c "shopt -s globstar && rm -rf $(GEN_FILES) Logs/*"
	@echo "$(_YELLOW)L'environnement de dévelopement a été nettoyé$(_NO_COLOR)"

################################################################################
#	Affiche l'usage du Makefile                                                #
################################################################################
help:
	@echo "$(_WHITE)Usage du Makefile:$(_NO_COLOR)"
	@echo "   $(_MAGENTA)make <cible>$(_NO_COLOR)"
	@echo ""
	@echo "$(_WHITE)Cibles:$(_NO_COLOR)"
	@echo "   - server : Lance la communication serveur."
	@echo "   - doc : Créer la documentation."
	@echo "   - flash : Flash la carte."
	@echo "   - run : Lance les serveurs locaux."
	@echo "   - stop : Arrête les serveurs locaux."
	@echo "   - install : Installe les dépendances."
	@echo "   - remove : Supprime les dépendances."
	@echo "   - clean : Nettoie l'environnement de dévelopement."
	@echo "   - help : Affiche le menu d'aide."
