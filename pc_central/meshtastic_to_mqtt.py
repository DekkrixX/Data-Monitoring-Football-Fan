#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 BRIDGE : Meshtastic Gateway → MQTT Local
═══════════════════════════════════════════════════════════════
 
 Ce script lit les messages du Meshtastic Gateway via USB
 et les publie sur un broker Mosquitto LOCAL (localhost).
 
  Mosquitto tourne en LOCAL sur ce PC
  localhost = 127.0.0.1 = communication interne au PC
  Pas de connexion Internet requise
 
 
═══════════════════════════════════════════════════════════════
"""

import json
import paho.mqtt.client as mqtt
import time
import sys
from datetime import datetime
import meshtastic
import meshtastic.serial_interface
from pubsub import pub


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Port série du Meshtastic Gateway
SERIAL_PORT = '/dev/cu.usbmodem983DAE614B981'  # macOS avec cu

# Broker MQTT LOCAL 
MQTT_BROKER = 'localhost'  # ← localhost = 127.0.0.1 = CE PC
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'meshtastic_bridge'
MQTT_KEEPALIVE = 60

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
    'total': 0,
    'by_supporter': {},
    'errors': 0,
    'start_time': time.time()
}

# Client MQTT global
mqtt_client = None

def print_banner():
    """Affiche la bannière de démarrage"""
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}╔═══════════════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}║       BRIDGE : Meshtastic Gateway → MQTT Local                            ║{Colors.ENDC}")
    print(f"{Colors.BOLD}╚═══════════════════════════════════════════════════════════════════════════╝{Colors.ENDC}")
    print("=" * 80)
    print(f"\n{Colors.CYAN}Configuration :{Colors.ENDC}")
    print(f"  Port série  : {SERIAL_PORT}")
    print(f"  MQTT Broker : {MQTT_BROKER}:{MQTT_PORT} {Colors.GREEN}(LOCAL){Colors.ENDC}")
    print(f"  Client ID   : {MQTT_CLIENT_ID}")
    print(f"\n{Colors.MAGENTA}{Colors.ENDC}")
    print(f"  - Compatible ancien format (valeur unique)")
    print(f"  - Compatible nouveau format (tableau de valeurs)")
    print("\n" + "-" * 80 + "\n")

def connect_mqtt():
    """Établit la connexion au broker MQTT local"""
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID)
        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        client.loop_start()
        print(f"{Colors.GREEN}✓{Colors.ENDC} Connecté au broker MQTT : {MQTT_BROKER}:{MQTT_PORT}")
        print(f"  {Colors.GREEN}→ Tout fonctionne en LOCAL sur ce PC{Colors.ENDC}")
        return client
    except Exception as e:
        print(f"{Colors.RED}✗ Erreur connexion MQTT :{Colors.ENDC} {e}\n")
        sys.exit(1)

def onReceive(packet, interface):
    """Callback appelé quand un message Meshtastic est reçu"""
    global mqtt_client, stats
    
    try:
        # Vérifier si c'est un message texte
        if 'decoded' in packet and 'text' in packet['decoded']:
            text = packet['decoded']['text']
            
            # Parser le JSON
            try:
                data = json.loads(text)
                
                # Extraire les informations
                supporter_id = data.get('id', 'unknown')
                hr = data.get('hr', 0)
                msg_number = data.get('n', 0)
                
                # Topic MQTT
                topic = f"polar/{supporter_id}/heartrate"
                
                # Publier sur MQTT LOCAL
                result = mqtt_client.publish(topic, json.dumps(data))
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    # Statistiques
                    stats['total'] += 1
                    stats['by_supporter'][supporter_id] = stats['by_supporter'].get(supporter_id, 0) + 1
                    
                    # Détecter le format (ancien ou nouveau)
                    now = datetime.now().strftime('%H:%M:%S')
                    
                    if isinstance(hr, list):
                        # Nouveau format : tableau de valeurs
                        nb_values = len(hr)
                        avg_hr = sum(hr) / nb_values if nb_values > 0 else 0
                        
                        print(f"{Colors.CYAN}[{now}]{Colors.ENDC} "
                              f"#{stats['total']:04d} | "
                              f"{Colors.BOLD}{supporter_id:12s}{Colors.ENDC} : "
                              f"{Colors.MAGENTA}{nb_values:2d} valeurs{Colors.ENDC} "
                              f"(moy: {Colors.GREEN}{avg_hr:.0f} BPM{Colors.ENDC}) → "
                              f"{topic}")
                    else:
                        # Ancien format : valeur unique
                        print(f"{Colors.CYAN}[{now}]{Colors.ENDC} "
                              f"#{stats['total']:04d} | "
                              f"{Colors.BOLD}{supporter_id:12s}{Colors.ENDC} : "
                              f"{Colors.GREEN}{hr:3d} BPM{Colors.ENDC} → "
                              f"{topic}")
                
            except json.JSONDecodeError:
                # Message texte non-JSON, ignorer
                pass
                
    except Exception as e:
        stats['errors'] += 1
        print(f"{Colors.YELLOW}  Erreur : {e}{Colors.ENDC}")

# ═══════════════════════════════════════════════════════════
# PROGRAMME PRINCIPAL
# ═══════════════════════════════════════════════════════════

def main():
    global mqtt_client
    
    print_banner()
    
    # Connexion MQTT
    mqtt_client = connect_mqtt()
    
    # Connexion Meshtastic
    try:
        print(f"\n{Colors.CYAN}Connexion au Meshtastic Gateway...{Colors.ENDC}")
        interface = meshtastic.serial_interface.SerialInterface(SERIAL_PORT)
        print(f"{Colors.GREEN}✓{Colors.ENDC} Connecté au Meshtastic : {SERIAL_PORT}")
        
        # S'abonner aux messages texte
        pub.subscribe(onReceive, "meshtastic.receive.text")
        
        print(f"\n{Colors.GREEN}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}  ✓ SYSTÈME OPÉRATIONNEL - En attente des messages...{Colors.ENDC}")
        print(f"{Colors.GREEN}{'=' * 80}{Colors.ENDC}\n")
        
        # Boucle infinie
        try:
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            # Arrêt propre
            duration = time.time() - stats['start_time']
            
            print(f"\n\n{Colors.BLUE}{'=' * 80}{Colors.ENDC}")
            print(f"{Colors.BOLD}  ARRÊT DU BRIDGE{Colors.ENDC}")
            print(f"{Colors.BLUE}{'=' * 80}{Colors.ENDC}\n")
            
            # Statistiques
            print(f"{Colors.CYAN}Statistiques de la session :{Colors.ENDC}")
            print(f"  Durée          : {int(duration)} secondes ({duration/60:.1f} minutes)")
            print(f"  Messages traités : {stats['total']}")
            print(f"  Erreurs        : {stats['errors']}")
            if stats['total'] > 0:
                print(f"  Débit moyen    : {stats['total'] / (duration / 60):.1f} messages/minute")
            
            if stats['by_supporter']:
                print(f"\n{Colors.CYAN}Répartition par supporter :{Colors.ENDC}")
                for supporter, count in sorted(stats['by_supporter'].items()):
                    percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
                    print(f"  {supporter:15s} : {count:4d} messages ({percentage:.1f}%)")
            
            # Déconnexion
            print(f"\n{Colors.CYAN}Fermeture des connexions...{Colors.ENDC}")
            interface.close()
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            print(f"{Colors.GREEN}✓ Déconnexion propre{Colors.ENDC}\n")
    
    except Exception as e:
        print(f"\n{Colors.RED}✗ Erreur fatale : {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()