#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 BRIDGE : MQTT Local → InfluxDB Local (BUFFER VERSION)
═══════════════════════════════════════════════════════════════
 
 Ce script écoute les messages MQTT LOCAL avec buffers de HR
 et stocke CHAQUE VALEUR séparément dans InfluxDB avec des
 timestamps rétro-actifs.
 
 Format attendu : {"id": "supporter1", "hr": [82, 82, 82, 82], "n": 924}
 
 Pour chaque buffer de N valeurs, on envoie N points dans InfluxDB
 avec des timestamps décrémentés (la dernière valeur = timestamp actuel,
 les précédentes = timestamps rétro-actifs).
 
═══════════════════════════════════════════════════════════════
"""

import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta
import time
import sys

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Broker MQTT LOCAL (sur ce PC, pas sur Internet !)
MQTT_BROKER = "localhost"  # ← localhost = 127.0.0.1 
MQTT_PORT = 1883
MQTT_TOPICS = ["polar/+/heartrate"]  # + est un wildcard (tous les supporters)
MQTT_CLIENT_ID = "mqtt_to_influxdb_buffer"
MQTT_KEEPALIVE = 60

# Base de données InfluxDB LOCAL (sur ce PC, pas sur Internet !)
INFLUX_URL = "http://localhost:8086"  # ← localhost 
INFLUX_TOKEN = "stade-token-123456789"
INFLUX_ORG = "football"
INFLUX_BUCKET = "heartrate"

# Intervalle entre les mesures (en secondes)
HEART_RATE_INTERVAL = 1  # Intervalle supposé entre 2 mesures HR

# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════

class Colors:
    """Codes ANSI pour couleurs terminal"""
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'

# Statistiques globales
stats = {
    'total_messages': 0,
    'total_points': 0,
    'by_supporter': {},
    'errors': 0,
    'start_time': time.time(),
    'last_buffer_sizes': []
}

def print_banner():
    """Affiche la bannière de démarrage"""
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}╔═══════════════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}║        BRIDGE : MQTT → InfluxDB                                           ║{Colors.ENDC}")
    print(f"{Colors.BOLD}╚═══════════════════════════════════════════════════════════════════════════╝{Colors.ENDC}")
    print("=" * 80)
    print(f"\n{Colors.CYAN}Configuration :{Colors.ENDC}")
    print(f"  MQTT Broker  : {MQTT_BROKER}:{MQTT_PORT} {Colors.GREEN}(LOCAL){Colors.ENDC}")
    print(f"  InfluxDB URL : {INFLUX_URL} {Colors.GREEN}(LOCAL){Colors.ENDC}")
    print(f"  Organization : {INFLUX_ORG}")
    print(f"  Bucket       : {INFLUX_BUCKET}")
    print(f"  Topics MQTT  : {', '.join(MQTT_TOPICS)}")
    print(f"\n{Colors.MAGENTA}{Colors.ENDC}")
    print(f"  - Intervalle entre mesures : {HEART_RATE_INTERVAL}s")
    print(f"  - Dernière valeur = timestamp actuel")
    print(f"  - Valeurs précédentes = timestamps rétro-actifs")
    print("\n" + "-" * 80 + "\n")

def test_influxdb():
    """Teste la connexion à InfluxDB et retourne le client"""
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        health = client.health()
        
        if health.status == "pass":
            print(f"{Colors.GREEN}✓{Colors.ENDC} InfluxDB accessible : {INFLUX_URL}")
            return client
        else:
            print(f"{Colors.RED}✗ InfluxDB non accessible (status: {health.status}){Colors.ENDC}")
            sys.exit(1)
            
    except Exception as e:
        print(f"{Colors.RED}✗ Erreur connexion InfluxDB :{Colors.ENDC} {e}")
        sys.exit(1)

def on_connect(client, userdata, flags, rc):
    """Callback appelé lors de la connexion au broker MQTT"""
    if rc == 0:
        print(f"{Colors.GREEN}✓{Colors.ENDC} Connecté au broker MQTT : {MQTT_BROKER}:{MQTT_PORT}")
        
        # S'abonner aux topics
        print(f"\n{Colors.CYAN}Abonnement aux topics :{Colors.ENDC}")
        for topic in MQTT_TOPICS:
            client.subscribe(topic)
            print(f"  ✓ {topic}")
        
        print(f"\n{Colors.GREEN}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}  ✓ SYSTÈME OPÉRATIONNEL  - En attente des données...{Colors.ENDC}")
        print(f"{Colors.GREEN}{'=' * 80}{Colors.ENDC}\n")
    else:
        error_messages = {
            1: "Protocole incorrect",
            2: "Client ID rejeté",
            3: "Serveur indisponible",
            4: "Mauvais username/password",
            5: "Non autorisé"
        }
        error_msg = error_messages.get(rc, f"Erreur inconnue (code {rc})")
        print(f"{Colors.RED}✗ Erreur connexion MQTT : {error_msg}{Colors.ENDC}")
        sys.exit(1)

def process_buffer(supporter_id, hr_buffer, msg_number, base_timestamp, write_api):
    """Traite un buffer et envoie chaque valeur séparément à InfluxDB"""
    global stats
    
    nb_values = len(hr_buffer)
    points_written = 0
    
    # Calculer la moyenne pour affichage
    avg_hr = sum(hr_buffer) / nb_values if nb_values > 0 else 0
    
    # Pour chaque valeur dans le buffer (du plus ancien au plus récent)
    for i, hr_value in enumerate(hr_buffer):
        # Calculer le timestamp rétro-actif
        # Dernière valeur (i = nb_values-1) = timestamp actuel
        # Avant-dernière valeur = timestamp actuel - intervalle
        # etc.
        time_offset = (nb_values - 1 - i) * HEART_RATE_INTERVAL
        point_timestamp = base_timestamp - timedelta(seconds=time_offset)
        
        # Formater le timestamp pour InfluxDB (RFC3339)
        timestamp_str = point_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Créer un point InfluxDB
        point = Point("heartrate") \
            .tag("supporter", supporter_id) \
            .tag("source", "buffer") \
            .field("hr", hr_value) \
            .field("msg_number", msg_number) \
            .field("buffer_index", i) \
            .field("buffer_size", nb_values) \
            .time(timestamp_str)  # Timestamp explicite
        
        # Écrire dans InfluxDB
        write_api.write(bucket=INFLUX_BUCKET, record=point)
        points_written += 1
    
    # Mettre à jour les statistiques
    stats['total_messages'] += 1
    stats['total_points'] += points_written
    stats['by_supporter'][supporter_id] = stats['by_supporter'].get(supporter_id, 0) + points_written
    stats['last_buffer_sizes'].append(nb_values)
    
    # Garder seulement les 10 derniers buffers pour les stats
    if len(stats['last_buffer_sizes']) > 10:
        stats['last_buffer_sizes'].pop(0)
    
    return nb_values, avg_hr, points_written

def on_message(client, userdata, message):
    """Callback appelé lors de la réception d'un message MQTT"""
    global stats
    
    try:
        # Timestamp actuel (pour la dernière valeur du buffer)
        base_timestamp = datetime.utcnow()
        
        # Parser le JSON
        data = json.loads(message.payload.decode())
        
        # Extraire les informations
        supporter_id = data.get("id", "unknown")
        msg_number = data.get("n", 0)
        
        # Vérifier le format du HR (valeur unique ou buffer)
        hr_data = data.get("hr", 0)
        write_api = userdata['write_api']
        
        # Affichage du message reçu
        now = datetime.now().strftime('%H:%M:%S')
        
        if isinstance(hr_data, list):
            # NOUVEAU FORMAT : Buffer de valeurs
            hr_buffer = hr_data
            nb_values, avg_hr, points_written = process_buffer(
                supporter_id, hr_buffer, msg_number, base_timestamp, write_api
            )
            
            print(f"{Colors.CYAN}[{now}]{Colors.ENDC} "
                  f"#{stats['total_messages']:04d} | "
                  f"{Colors.BOLD}{supporter_id:12s}{Colors.ENDC} : "
                  f"{Colors.MAGENTA}{nb_values:2d} valeurs{Colors.ENDC} "
                  f"(moy: {Colors.GREEN}{avg_hr:.0f} BPM{Colors.ENDC}) → "
                  f"{points_written} points → InfluxDB ✓")
        
        elif isinstance(hr_data, (int, float)):
            # ANCIEN FORMAT : Valeur unique (compatibilité)
            hr_value = int(hr_data)
            timestamp_str = base_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Créer un point InfluxDB
            point = Point("heartrate") \
                .tag("supporter", supporter_id) \
                .tag("source", "single") \
                .field("hr", hr_value) \
                .field("msg_number", msg_number) \
                .field("buffer_size", 1) \
                .time(timestamp_str)
            
            # Écrire dans InfluxDB
            write_api.write(bucket=INFLUX_BUCKET, record=point)
            
            # Mettre à jour les statistiques
            stats['total_messages'] += 1
            stats['total_points'] += 1
            stats['by_supporter'][supporter_id] = stats['by_supporter'].get(supporter_id, 0) + 1
            
            print(f"{Colors.CYAN}[{now}]{Colors.ENDC} "
                  f"#{stats['total_messages']:04d} | "
                  f"{Colors.BOLD}{supporter_id:12s}{Colors.ENDC} : "
                  f"{Colors.GREEN}{hr_value:3d} BPM{Colors.ENDC} → "
                  f"InfluxDB ✓")
        
        else:
            raise ValueError(f"Format HR non supporté: {type(hr_data)}")
            
    except json.JSONDecodeError as e:
        stats['errors'] += 1
        print(f"{Colors.YELLOW}  Erreur JSON : {e}{Colors.ENDC}")
    except ValueError as e:
        stats['errors'] += 1
        print(f"{Colors.YELLOW}  Valeur invalide : {e}{Colors.ENDC}")
    except Exception as e:
        stats['errors'] += 1
        print(f"{Colors.RED}✗ Erreur : {e}{Colors.ENDC}")

# ═══════════════════════════════════════════════════════════
# PROGRAMME PRINCIPAL
# ═══════════════════════════════════════════════════════════

def main():
    print_banner()
    
    # Tester et initialiser InfluxDB
    influx_client = test_influxdb()
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    
    print()
    
    # Créer et configurer le client MQTT
    mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    mqtt_client.user_data_set({'write_api': write_api})
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        # Se connecter au broker MQTT et démarrer la boucle
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        mqtt_client.loop_forever()
    
    except KeyboardInterrupt:
        # Arrêt propre (Ctrl+C)
        duration = time.time() - stats['start_time']
        
        print(f"\n\n{Colors.BLUE}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}  ARRÊT DU BRIDGE (BUFFER){Colors.ENDC}")
        print(f"{Colors.BLUE}{'=' * 80}{Colors.ENDC}\n")
        
        # Statistiques finales
        print(f"{Colors.CYAN}Statistiques de la session :{Colors.ENDC}")
        print(f"  Durée totale    : {int(duration)} secondes ({duration/60:.1f} minutes)")
        print(f"  Messages reçus  : {stats['total_messages']}")
        print(f"  Points écrits   : {stats['total_points']}")
        print(f"  Erreurs         : {stats['errors']}")
        
        if stats['total_points'] > 0:
            print(f"  Débit moyen     : {stats['total_points'] / (duration / 60):.1f} points/minute")
            print(f"  Taux d'erreur   : {stats['errors'] / stats['total_messages'] * 100:.1f}%")
            
            if stats['last_buffer_sizes']:
                avg_buffer = sum(stats['last_buffer_sizes']) / len(stats['last_buffer_sizes'])
                print(f"  Taille buffer   : {avg_buffer:.1f} valeurs/message")
        
        if stats['by_supporter']:
            print(f"\n{Colors.CYAN}Répartition par supporter :{Colors.ENDC}")
            for supporter, count in sorted(stats['by_supporter'].items()):
                percentage = (count / stats['total_points'] * 100) if stats['total_points'] > 0 else 0
                print(f"  {supporter:15s} : {count:4d} points ({percentage:.1f}%)")
        
        # Déconnexions propres
        print(f"\n{Colors.CYAN}Fermeture des connexions...{Colors.ENDC}")
        mqtt_client.disconnect()
        influx_client.close()
        print(f"{Colors.GREEN}✓ Déconnexion propre{Colors.ENDC}\n")
    
    except Exception as e:
        print(f"\n{Colors.RED}✗ Erreur fatale : {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()