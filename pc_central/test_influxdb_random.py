#!/usr/bin/env python3
"""
Script de test pour InfluxDB
Génère des données aléatoires de fréquence cardiaque et les envoie à InfluxDB
"""

import random
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration InfluxDB
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "stade-token-123456789"
INFLUX_ORG = "football"
INFLUX_BUCKET = "heartrate"

# Paramètres de génération
SUPPORTER_ID = "supporter1"
HR_MIN = 60
HR_MAX = 180
INTERVAL = 1  # secondes entre chaque envoi
NB_MESSAGES = 50  # nombre de messages à envoyer

print("=" * 60)
print("  TEST INFLUXDB - Générateur de données aléatoires")
print("=" * 60)
print(f"\nConfiguration :")
print(f"  URL      : {INFLUX_URL}")
print(f"  Org      : {INFLUX_ORG}")
print(f"  Bucket   : {INFLUX_BUCKET}")
print(f"  Supporter: {SUPPORTER_ID}")
print(f"  Messages : {NB_MESSAGES}")
print(f"  Intervalle: {INTERVAL}s")
print(f"  HR range : {HR_MIN}-{HR_MAX} BPM")
print("\n" + "-" * 60)

try:
    # Connexion à InfluxDB
    print("\nConnexion à InfluxDB...")
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    # Vérifier la connexion
    health = client.health()
    if health.status != "pass":
        print(f"✗ Erreur : InfluxDB status = {health.status}")
        exit(1)
    
    print("✓ Connecté à InfluxDB")
    print("\n" + "=" * 60)
    print("  Envoi des données...")
    print("=" * 60 + "\n")
    
    # Générer et envoyer les données
    for i in range(1, NB_MESSAGES + 1):
        # Générer HR aléatoire
        hr = random.randint(HR_MIN, HR_MAX)
        
        # Créer le point InfluxDB
        point = Point("heartrate") \
            .tag("supporter", SUPPORTER_ID) \
            .field("hr", hr) \
            .field("msg_number", i) \
            .field("test_mode", True)
        
        # Écrire dans InfluxDB
        write_api.write(bucket=INFLUX_BUCKET, record=point)
        
        # Afficher
        now = datetime.now().strftime('%H:%M:%S')
        print(f"[{now}] Message #{i:03d} | {SUPPORTER_ID} : {hr:3d} BPM → InfluxDB ✓")
        
        # Attendre avant le prochain envoi
        if i < NB_MESSAGES:
            time.sleep(INTERVAL)
    
    # Résumé
    print("\n" + "=" * 60)
    print("  ✓ TEST TERMINÉ")
    print("=" * 60)
    print(f"\nTotal envoyé : {NB_MESSAGES} messages")
    print(f"Durée        : {NB_MESSAGES * INTERVAL} secondes")
    print(f"\nVérification :")
    print(f"  docker exec influxdb influx query \\")
    print(f"    --token {INFLUX_TOKEN} \\")
    print(f"    --org {INFLUX_ORG} \\")
    print(f"    'from(bucket:\"{INFLUX_BUCKET}\") |> range(start:-5m) |> filter(fn: (r) => r.supporter == \"{SUPPORTER_ID}\")' ")
    print()
    
    # Fermer la connexion
    client.close()

except KeyboardInterrupt:
    print("\n\n✗ Arrêté par l'utilisateur (Ctrl+C)")
    client.close()

except Exception as e:
    print(f"\n✗ Erreur : {e}")
    exit(1)
