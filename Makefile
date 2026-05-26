# =============================================================================
#  Makefile écrit par Quentin GUILLEMOD
# =============================================================================

# Définition des variables d'environnement
include .env
export
export APP_DEVICE = $(APP) - Device
export APP_SERVER = $(APP) - Server

# Fichiers générés
GEN_FILES = Device/doc Server/doc Device/.pio Device/data Tests/Distance/.pio Tests/Distance/data .venv Resources/Data/gatewayContact.txt

# Définition des couleurs
_RESET = \033[m
_BLACK = \033[1;30m
_RED = \033[1;31m
_GREEN = \033[1;32m
_YELLOW = \033[1;33m
_BLUE = \033[1;34m
_MAGENTA = \033[1;35m
_CYAN = \033[1;36m
_WHITE = \033[1;37m

.PHONY: build run stop logs test clear doc clean script install remove help
.DEFAULT_GOAL := help

# =============================================================================
#  Construction des conteneurs Docker
# =============================================================================
build:
	@echo "$(_YELLOW)Construction des conteneurs Docker$(_RESET)"
	@docker compose build

# =============================================================================
#  Lancement des conteneurs Docker
# =============================================================================
run:
	@echo "$(_YELLOW)Lancement des conteneurs Docker$(_RESET)"
	@docker compose up -d

# =============================================================================
#  Arrêt des conteneurs Docker
# =============================================================================
stop:
	@echo "$(_YELLOW)Arrêt des conteneurs Docker$(_RESET)"
	@docker compose down
	@docker volume prune -f
	@if docker ps -a --format "{{.Names}}" | grep -w data > /dev/null; \
	then \
		docker rm -f test-data; \
	fi
	@if docker ps -a --format "{{.Names}}" | grep -w tracking > /dev/null; \
	then \
		docker rm -f test-tracking; \
	fi
	@if docker ps -a --format "{{.Names}}" | grep -w distance > /dev/null; \
	then \
		docker rm -f test-distance || true; \
	fi

# =============================================================================
#  Affichage des logs des conteneurs Docker
# =============================================================================
log:
	@if [ -z "$(TARGET)" ]; \
	then \
		echo "$(_YELLOW)Logs de tous les conteneurs Docker$(_RESET)"; \
	else \
		echo "$(_YELLOW)Logs du conteneurs Docker: $(TARGET)$(_RESET)"; \
	fi
	@docker compose logs -f $(TARGET)

# =============================================================================
#  Lancement des conteneurs Docker de test
# =============================================================================
test:
	@if [ -z "$(TARGET)" ]; \
	then \
		echo "$(_RED)Aucun cible spécifiée.$(_RESET)"; \
	else \
		echo "$(_YELLOW)Lancement des conteneurs Docker de test$(_RESET)"; \
		docker compose --profile $(TARGET) up -d; \
	fi

# =============================================================================
#  Suppression des volumes Docker
# =============================================================================
clear:
	@echo "$(_YELLOW)Suppression des volumes Docker$(_RESET)"
	@docker compose down -v
	@docker rmi data-monitoring-football-fan-bridge-meshcore-mqtt
	@docker rmi data-monitoring-football-fan-bridge-meshtastic-mqtt
	@docker rmi data-monitoring-football-fan-bridge-mqtt-influxdb
	@docker rmi data-monitoring-football-fan-server
	@docker rmi data-monitoring-football-fan-test-data || true
	@docker rmi data-monitoring-football-fan-test-tracking || true
	@docker rmi data-monitoring-football-fan-test-distance || true
	@docker rmi eclipse-mosquitto
	@docker rmi grafana/grafana:12.4.2
	@docker rmi influxdb:2.7
	@docker rmi postgres:16

# =============================================================================
#  Création de la documentation
# =============================================================================
doc:
	@echo "$(_YELLOW)Création de la documentation du Device$(_RESET)"
	@doxygen Device/Doxyfile
	@echo "$(_YELLOW)Création de la documentation du Server$(_RESET)"
	@doxygen Server/Doxyfile

# =============================================================================
#  Nettoyage l'environnement
# =============================================================================
clean:
	@echo "$(_YELLOW)Nettoyage de l'environnement$(_RESET)"
	@rm -rf $(GEN_FILES)

# =============================================================================
#  Affichage de l'usage des scripts
# =============================================================================
script:
	@if [ -z "$(TARGET)" ]; \
	then \
		echo "Liste des scripts"; \
		echo " - envcrypt"; \
		echo " - flash"; \
		echo " - logviewer"; \
		echo " - readSerialLog"; \
	else \
		if [ "$(TARGET)" = "envcrypt" ]; \
		then \
			echo "$(_YELLOW)Menu d'aide du script envcrypt$(_RESET)"; \
			bash "$(SCRIPT_PATH)envcrypt.sh" "--help"; \
		elif [ "$(TARGET)" = "flash" ]; \
		then \
			echo "$(_YELLOW)Menu d'aide du script flash$(_RESET)"; \
			bash "$(SCRIPT_PATH)flash.sh" "--help"; \
		elif [ "$(TARGET)" = "logviewer" ]; \
		then \
			echo "$(_YELLOW)Menu d'aide du script logviewer$(_RESET)"; \
			bash "$(SCRIPT_PATH)logviewer.sh" "--help"; \
		elif [ "$(TARGET)" = "readSerialLog" ]; \
		then \
			echo "$(TARGET)Menu d'aide du script readSerialLog$(_RESET)"; \
			bash "$(SCRIPT_PATH)readSerialLog.sh" "--help"; \
		else \
			echo "$(_RED)Aucun menu d'aide n'est disponible pour le script $(TARGET)$(_RESET)"; \
		fi; \
	fi

# =============================================================================
#  Installation des dépendances
# =============================================================================
install:
	@echo "$(_YELLOW)Installation des dépendances$(_RESET)"
	@echo "Package: Curl"
	@sudo apt install -y curl
	@echo "Package: Doxygen"
	@sudo apt install -y doxygen graphviz
	@echo "Package: Docker"
	@curl -fsSL https://get.docker.com -o get-docker.sh
	@sudo sh ./get-docker.sh
	@rm get-docker.sh
	@echo "Package: Python3.10"
	@sudo apt install -y python3.10
	@echo "Package: Pip"
	@sudo apt install -y python3-pip
	@python3.10 -m pip install --upgrade pip
	@echo "Package: venv"
	@sudo apt install -y python3-venv
	@echo "Création de l'environnement virtuel"
	@python3.10 -m venv Ultra-Wide-Band/uwb-qorvo-tools/.venv
	@Ultra-Wide-Band/uwb-qorvo-tools/.venv/bin/pip install Ultra-Wide-Band/uwb-qorvo-tools
	@echo "$(_YELLOW)Les dépendances ont été installées$(_NO_COLOR)"

# =============================================================================
#  Suppression des dépendances
# =============================================================================
remove:
	@echo "$(_YELLOW)Suppression des dépendances$(_RESET)"
	@echo "Package: Curl"
	@sudo apt remove -y curl
	@echo "Package: Doxygen"
	@sudo apt remove -y doxygen graphviz
	@echo "Package: Docker"
	@sudo apt purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras
	@sudo rm -rf /var/lib/docker
	@sudo rm -rf /var/lib/containerd
	@sudo rm /etc/apt/sources.list.d/docker.sources
	@sudo rm /etc/apt/keyrings/docker.asc
	@echo "Package: Python3-venv"
	@sudo apt remove -y python3-venv
	@echo "Package: Pip"
	@sudo apt remove -y python3-pip
	@echo "Package: Python3.10"
	@sudo apt remove -y python3.10
	@echo "Package: Python3"
	@sudo apt remove -y python3
	@echo "Suppression des environnements virtuels python"
	@rm -rf .venv Ultra-Wide-Band/uwb-qorvo-tools/.venv
	@sudo apt autoremove -y
	@echo "$(_YELLOW)Les dépendances ont été supprimées$(_NO_COLOR)"

# =============================================================================
#  Affichage de l'usage du Makefile
# =============================================================================
help:
	@echo "$(_WHITE)Usage du Makefile:$(_NO_COLOR)"
	@echo "   $(_MAGENTA)make <cible>$(_NO_COLOR)"
	@echo ""
	@echo "$(_WHITE)Cibles:$(_NO_COLOR)"
	@echo "   - build   : Construit les conteneurs Docker."
	@echo "   - run     : Lance les conteneurs Docker."
	@echo "   - stop    : Arrête les conteneurs Docker."
	@echo "   - log     : Affiche les logs des conteneurs Docker. (TARGET=<conteneur>)"
	@echo "   - test    : Lance les conteneurs Docker de test. (TARGET=<conteneur>)"
	@echo "   - clear   : Supprime les volumes Docker."
	@echo "   - doc     : Créer la documentation."
	@echo "   - clean   : Nettoie l'environnement."
	@echo "   - script  : Affiche le menu d'aide des scripts. (TARGET=<script>)"
	@echo "   - install : Installe les dépendances."
	@echo "   - remove  : Supprime les dépendances."
	@echo "   - help    : Affiche le menu d'aide."
