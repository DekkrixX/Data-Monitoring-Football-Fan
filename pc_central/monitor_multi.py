#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 Moniteur Multi-Graphiques - Compatible Buffer V2
═══════════════════════════════════════════════════════════════
 
 Affiche dans UNE SEULE FENÊTRE :
 - N graphiques individuels (un par supporter)
 - 1 graphique de comparaison
 
 Compatible avec le format buffer : {"id": "supporter1", "hr": [70, 72, 74], "n": 42}
 
═══════════════════════════════════════════════════════════════
"""

import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime, timedelta
from collections import deque
import sys

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "polar/+/heartrate"
MAX_POINTS = 100
UPDATE_INTERVAL = 1000  # ms - Intervalle de mise à jour du graphique

# Couleurs pour chaque supporter
COLORS = [
    '#3498db',  # Bleu
    '#e74c3c',  # Rouge
    '#2ecc71',  # Vert
    '#f39c12',  # Orange
    '#9b59b6',  # Violet
    '#1abc9c',  # Turquoise
]

# ═══════════════════════════════════════════════════════════
# STRUCTURE DE DONNÉES
# ═══════════════════════════════════════════════════════════

class SupporterData:
    """Classe pour gérer les données d'un supporter"""
    def __init__(self, supporter_id, color):
        self.id = supporter_id
        self.color = color
        self.times = deque(maxlen=MAX_POINTS)
        self.values = deque(maxlen=MAX_POINTS)
        self.stats = {
            'min': 999,
            'max': 0,
            'avg': 0,
            'count': 0,
            'sum': 0
        }
    
    def add_value(self, hr_value, timestamp=None):
        """Ajoute une valeur HR"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.times.append(timestamp)
        self.values.append(hr_value)
        
        # Statistiques
        self.stats['count'] += 1
        self.stats['sum'] += hr_value
        self.stats['min'] = min(self.stats['min'], hr_value)
        self.stats['max'] = max(self.stats['max'], hr_value)
        self.stats['avg'] = self.stats['sum'] / self.stats['count']

# ═══════════════════════════════════════════════════════════
# GESTIONNAIRE DE DONNÉES
# ═══════════════════════════════════════════════════════════

class DataManager:
    """Gère les données de tous les supporters"""
    def __init__(self):
        self.supporters = {}
        self.color_index = 0
    
    def get_or_create_supporter(self, supporter_id):
        """Obtient ou crée un supporter"""
        if supporter_id not in self.supporters:
            color = COLORS[self.color_index % len(COLORS)]
            self.supporters[supporter_id] = SupporterData(supporter_id, color)
            self.color_index += 1
            print(f"✓ Supporter détecté : {supporter_id}")
        return self.supporters[supporter_id]
    
    def get_supporter(self, supporter_id):
        """Retourne un supporter s'il existe"""
        return self.supporters.get(supporter_id, None)
    
    def get_all_supporters(self):
        """Retourne tous les supporters"""
        return list(self.supporters.values())
    
    def get_supporter_count(self):
        """Retourne le nombre de supporters"""
        return len(self.supporters)

data_manager = DataManager()
mqtt_client = None

# ═══════════════════════════════════════════════════════════
# CALLBACKS MQTT
# ═══════════════════════════════════════════════════════════

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback de connexion MQTT"""
    if rc == 0:
        print(f"\n✓ Connecté au broker MQTT : {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"✓ Abonné au topic : {MQTT_TOPIC}")
        print("\n" + "="*60)
        print("  Monitoring en cours...")
        print("="*60 + "\n")
    else:
        print(f"✗ Erreur connexion MQTT (code {rc})")
        sys.exit(1)

def on_message(client, userdata, message):
    """Callback de réception de message MQTT"""
    try:
        data = json.loads(message.payload.decode())
        supporter_id = data.get('id', 'unknown')
        hr_data = data.get('hr', 0)
        
        supporter = data_manager.get_or_create_supporter(supporter_id)
        
        # Gestion du format buffer
        if isinstance(hr_data, list):
            base_time = datetime.now()
            for i, hr in enumerate(hr_data):
                time_offset = len(hr_data) - i - 1
                timestamp = base_time - timedelta(seconds=time_offset)
                supporter.add_value(hr, timestamp)
        
        elif isinstance(hr_data, (int, float)):
            supporter.add_value(int(hr_data))
    
    except Exception as e:
        print(f"✗ Erreur : {e}")

# ═══════════════════════════════════════════════════════════
# ANIMATION
# ═══════════════════════════════════════════════════════════

def animate(frame, fig, axes):
    """Animation de tous les graphiques avec détection automatique"""
    
    # Obtenir tous les supporters actifs
    all_supporters = data_manager.get_all_supporters()
    nb_supporters = len(all_supporters)
    
    # Déterminer si on affiche la comparaison
    show_comparison = nb_supporters >= 2
    
    # Réorganiser les axes si le nombre de supporters a changé
    current_layout = getattr(fig, '_current_layout', None)
    needed_layout = (nb_supporters, show_comparison)
    
    if current_layout != needed_layout:
        # Le layout a changé, on doit recréer les subplots
        fig.clear()
        
        if nb_supporters == 0:
            # Aucun supporter, afficher message d'attente
            ax = fig.add_subplot(1, 1, 1)
            ax.text(0.5, 0.5, 'En attente de données...', 
                   transform=ax.transAxes,
                   fontsize=16, ha='center', va='center', color='gray')
            ax.axis('off')
            fig._current_layout = needed_layout
            plt.tight_layout()
            return
        
        elif nb_supporters == 1:
            # 1 supporter = 1 graphique plein écran
            nrows, ncols = 1, 1
            axes_list = [fig.add_subplot(1, 1, 1)]
        
        elif nb_supporters == 2:
            # 2 supporters = disposition 2x2
            nrows, ncols = 2, 2
            axes_list = [fig.add_subplot(2, 2, 1),
                        fig.add_subplot(2, 2, 2),
                        fig.add_subplot(2, 1, 2)]  # Comparaison sur toute la largeur
        
        elif nb_supporters == 3:
            # 3 supporters = disposition 2x2
            nrows, ncols = 2, 2
            axes_list = [fig.add_subplot(2, 2, 1),
                        fig.add_subplot(2, 2, 2),
                        fig.add_subplot(2, 2, 3),
                        fig.add_subplot(2, 2, 4)]  # Comparaison
        
        else:
            # N supporters = grille dynamique
            ncols = 2
            nrows = (nb_supporters + 1) // 2 + 1
            axes_list = []
            for i in range(nb_supporters):
                axes_list.append(fig.add_subplot(nrows, ncols, i + 1))
            # Comparaison sur toute la dernière ligne
            axes_list.append(fig.add_subplot(nrows, 1, nrows))
        
        # Sauvegarder le nouveau layout
        fig._axes_list = axes_list
        fig._current_layout = needed_layout
        
        print(f"✓ Layout mis à jour : {nb_supporters} supporter(s)" + 
              (f" + comparaison" if show_comparison else ""))
    
    # Utiliser les axes sauvegardés
    axes_list = getattr(fig, '_axes_list', [])
    
    if not axes_list:
        return
    
    # Afficher les graphiques individuels
    for i, supporter in enumerate(all_supporters):
        if i >= len(axes_list):
            break
        
        ax = axes_list[i]
        ax.clear()
        
        ax.set_title(f'{supporter.id}', fontsize=12, fontweight='bold')
        ax.set_ylabel('FC (BPM)', fontsize=10)
        ax.set_ylim(40, 200)
        ax.grid(True, alpha=0.3)
        
        if len(supporter.values) > 0:
            # Tracer la courbe
            ax.plot(supporter.times, supporter.values,
                   color=supporter.color,
                   linewidth=2.5,
                   marker='o',
                   markersize=4)
            
            # Zone remplie
            ax.fill_between(supporter.times, supporter.values, 0, 
                           alpha=0.2, color=supporter.color)
            
            # Valeur actuelle
            last_hr = supporter.values[-1]
            ax.text(0.02, 0.98, f'{last_hr} BPM', 
                   transform=ax.transAxes,
                   fontsize=16, fontweight='bold',
                   va='top', ha='left',
                   color=supporter.color,
                   bbox=dict(boxstyle='round', facecolor='white', 
                           alpha=0.9, edgecolor=supporter.color, linewidth=2))
            
            # Statistiques
            stats = supporter.stats
            stats_text = f"Min:{stats['min']} Moy:{stats['avg']:.0f} Max:{stats['max']}"
            ax.text(0.98, 0.02, stats_text, 
                   transform=ax.transAxes,
                   fontsize=8,
                   va='bottom', ha='right',
                   bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
        else:
            ax.text(0.5, 0.5, 'En attente...', 
                   transform=ax.transAxes,
                   fontsize=12, ha='center', va='center', color='gray')
    
    # Graphique de comparaison (si 2+ supporters)
    if show_comparison and len(axes_list) > nb_supporters:
        ax_comp = axes_list[nb_supporters]
        ax_comp.clear()
        
        ax_comp.set_title('Comparaison', fontsize=12, fontweight='bold')
        ax_comp.set_ylabel('FC (BPM)', fontsize=10)
        ax_comp.set_xlabel('Temps', fontsize=10)
        ax_comp.set_ylim(40, 200)
        ax_comp.grid(True, alpha=0.3)
        
        has_data = False
        for supporter in all_supporters:
            if len(supporter.values) > 0:
                has_data = True
                ax_comp.plot(supporter.times, supporter.values,
                            color=supporter.color,
                            linewidth=2,
                            marker='o',
                            markersize=3,
                            label=supporter.id,
                            alpha=0.8)
        
        if has_data:
            ax_comp.legend(loc='upper left', fontsize=9)
        
        if not has_data:
            ax_comp.text(0.5, 0.5, 'En attente...', 
                        transform=ax_comp.transAxes,
                        fontsize=12, ha='center', va='center', color='gray')
        
        # Afficher valeurs actuelles
        y_position = 0.98
        for i, supporter in enumerate(all_supporters):
            if len(supporter.values) > 0:
                last_hr = supporter.values[-1]
                display_name = f"S{i+1}"
                
                ax_comp.text(0.02, y_position, f'{display_name}: {last_hr} BPM', 
                            transform=ax_comp.transAxes,
                            fontsize=11, fontweight='bold',
                            va='top', ha='left',
                            color=supporter.color,
                            bbox=dict(boxstyle='round', facecolor='white', 
                                    alpha=0.8, edgecolor=supporter.color, linewidth=1.5))
                y_position -= 0.12
    
    plt.tight_layout()

# ═══════════════════════════════════════════════════════════
# PROGRAMME PRINCIPAL
# ═══════════════════════════════════════════════════════════

def main():
    global mqtt_client
    
    print("\n" + "="*60)
    print("  Moniteur Multi-Graphiques")
    print("  Compatible Buffer V2 - Détection Automatique")
    print("="*60)
    print("\n✓ Détection automatique des supporters")
    print("✓ Layout adaptatif selon le nombre de capteurs")
    print("✓ Comparaison à partir de 2 supporters\n")
    
    # Créer une figure initiale simple
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle('Monitoring Multi-Supporters (Auto-détection)', 
                fontsize=16, fontweight='bold')
    fig.canvas.manager.set_window_title('Heart Rate Monitor')
    
    # Initialiser le layout
    fig._current_layout = None
    fig._axes_list = []
    
    # Initialisation MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 
                             client_id="monitor_multi_auto")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        
        # Animation avec détection automatique
        ani = animation.FuncAnimation(
            fig,
            animate,
            fargs=(fig, None),
            interval=UPDATE_INTERVAL,
            cache_frame_data=False
        )
        
        print("✓ Système démarré - En attente de données...")
        print("✓ Fermez la fenêtre pour quitter\n")
        
        plt.show()
    
    except KeyboardInterrupt:
        print("\n\n✓ Arrêt du moniteur...")
    
    except Exception as e:
        print(f"\n✗ Erreur fatale : {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("✓ Déconnexion propre\n")

if __name__ == "__main__":
    main()