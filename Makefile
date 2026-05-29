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

.PHONY: build run stop logs test tracking clear doc clean script install remove help
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
	@if docker ps -a --format "{{.Names}}" | grep -w tracker > /dev/null; \
	then \
		docker ps -aq --filter "name=tracker-" | xargs -r docker rm -f; \
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
#  Lancement d'une carte avec communication UWB pour le tracking
# =============================================================================
tracker:
	@docker run -d --name "tracker-$(shell date +%s)" --env-file .env --device $(PORT):$(PORT) --network data-monitoring-football-fan_default data-monitoring-football-fan-tracker python3.10 -m UltraWideBand.tracking $(PORT) $(TYPE) $(ADDRESS) $(if $(DEST),--destAddress $(DEST),)

# =============================================================================
#  Suppression des volumes Docker
# =============================================================================
clear:
	@echo "$(_YELLOW)Suppression des volumes Docker$(_RESET)"
	@docker compose down -v
	@docker rmi data-monitoring-football-fan-bridge-meshcore-mqtt || true
	@docker rmi data-monitoring-football-fan-bridge-meshtastic-mqtt || true
	@docker rmi data-monitoring-football-fan-bridge-mqtt-influxdb || true
	@docker rmi data-monitoring-football-fan-server || true
	@docker rmi data-monitoring-football-fan-test-data || true
	@docker rmi data-monitoring-football-fan-test-tracking || true
	@docker rmi data-monitoring-football-fan-test-distance || true
	@docker rmi data-monitoring-football-fan-tracker || true
	@docker rmi eclipse-mosquitto || true
	@docker rmi grafana/grafana:12.4.2 || true
	@docker rmi influxdb:2.7 || true
	@docker rmi postgres:16 || true

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
			echo "$(_YELLOW)Menu d'aide du script envcrypt.$(_RESET)"; \
			echo "$(_YELLOW)Utilisation: bash $(SCRIPT_PATH)$(TARGET).sh$(_RESET)"; \
			bash "$(SCRIPT_PATH)envcrypt.sh" "--help"; \
		elif [ "$(TARGET)" = "flash" ]; \
		then \
			echo "$(_YELLOW)Menu d'aide du script flash$(_RESET)"; \
			echo "$(_YELLOW)Utilisation: bash $(SCRIPT_PATH)$(TARGET).sh$(_RESET)"; \
			bash "$(SCRIPT_PATH)flash.sh" "--help"; \
		elif [ "$(TARGET)" = "logviewer" ]; \
		then \
			echo "$(_YELLOW)Menu d'aide du script logviewer$(_RESET)"; \
			echo "$(_YELLOW)Utilisation: bash $(SCRIPT_PATH)$(TARGET).sh$(_RESET)"; \
			bash "$(SCRIPT_PATH)logviewer.sh" "--help"; \
		elif [ "$(TARGET)" = "readSerialLog" ]; \
		then \
			echo "$(TARGET)Menu d'aide du script readSerialLog$(_RESET)"; \
			echo "$(_YELLOW)Utilisation: bash $(SCRIPT_PATH)$(TARGET).sh$(_RESET)"; \
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
	@echo "Package: Python3"
	@sudo apt remove -y python3
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
	@echo "   - tracker : Lance de la communication UWB pour le tracker. (PORT=<port_série>, TYPE=<type_de_carte>, ADDRESS=<adresse_de_la_carte>, DEST=<liste_adresse_destinataire>)"
	@echo "   - clear   : Supprime les volumes Docker."
	@echo "   - doc     : Créer la documentation."
	@echo "   - clean   : Nettoie l'environnement."
	@echo "   - script  : Affiche le menu d'aide des scripts. (TARGET=<script>)"
	@echo "   - install : Installe les dépendances."
	@echo "   - remove  : Supprime les dépendances."
	@echo "   - help    : Affiche le menu d'aide."
