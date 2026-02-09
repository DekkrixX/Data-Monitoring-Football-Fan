#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 Dashboard Web Local 
═══════════════════════════════════════════════════════════════
 
 Serveur Flask + WebSocket pour affichage temps réel
 Compatible avec format buffer : {"id": "supporter1", "hr": [70, 72, 74], "n": 42}
 Détection automatique du nombre de supporters
 
═══════════════════════════════════════════════════════════════
"""

from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json
import threading
from datetime import datetime, timedelta
from collections import deque

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPICS = ["polar/+/heartrate"]
WEB_PORT = 5001
MAX_POINTS = 100

# ═══════════════════════════════════════════════════════════
# APPLICATION FLASK
# ═══════════════════════════════════════════════════════════

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stade-secret-123'
socketio = SocketIO(app, cors_allowed_origins="*")

# ═══════════════════════════════════════════════════════════
# STOCKAGE DES DONNÉES
# ═══════════════════════════════════════════════════════════

class SupporterData:
    """Gère les données d'un supporter"""
    def __init__(self, supporter_id):
        self.id = supporter_id
        self.times = deque(maxlen=MAX_POINTS)
        self.values = deque(maxlen=MAX_POINTS)
        self.stats = {
            'min': 999,
            'max': 0,
            'avg': 0,
            'count': 0,
            'sum': 0,
            'last': 0
        }
    
    def add_value(self, hr_value, timestamp):
        """Ajoute une valeur avec timestamp"""
        self.times.append(timestamp)
        self.values.append(hr_value)
        
        # Mise à jour stats
        self.stats['count'] += 1
        self.stats['sum'] += hr_value
        self.stats['min'] = min(self.stats['min'], hr_value)
        self.stats['max'] = max(self.stats['max'], hr_value)
        self.stats['avg'] = self.stats['sum'] / self.stats['count']
        self.stats['last'] = hr_value
    
    def get_dict(self):
        """Retourne les données sous forme de dictionnaire"""
        return {
            'times': list(self.times),
            'values': list(self.values),
            'stats': self.stats
        }

data_store = {}  # Dictionnaire dynamique de supporters
mqtt_client = None

# ═══════════════════════════════════════════════════════════
# CALLBACKS MQTT
# ═══════════════════════════════════════════════════════════

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback connexion MQTT"""
    if rc == 0:
        print("✓ Connecté au broker MQTT:", MQTT_BROKER)
        for topic in MQTT_TOPICS:
            client.subscribe(topic)
            print("✓ Abonné à:", topic)
    else:
        print("✗ Erreur connexion MQTT:", rc)

def on_message(client, userdata, message):
    """Callback réception message MQTT - Compatible Buffer V2"""
    try:
        data = json.loads(message.payload.decode())
        supporter_id = data.get('id', 'unknown')
        hr_data = data.get('hr', 0)
        
        # Créer le supporter s'il n'existe pas
        if supporter_id not in data_store:
            data_store[supporter_id] = SupporterData(supporter_id)
            print(f"✓ Nouveau supporter détecté : {supporter_id}")
            socketio.emit('new_supporter', {'id': supporter_id})
        
        supporter = data_store[supporter_id]
        
        #  GESTION FORMAT BUFFER 
        if isinstance(hr_data, list):
            # Format buffer : [70, 72, 74, 73, 71]
            base_time = datetime.now()
            
            for i, hr in enumerate(hr_data):
                # Calculer timestamp rétroactif
                time_offset = len(hr_data) - i - 1
                timestamp = base_time - timedelta(seconds=time_offset)
                timestamp_str = timestamp.strftime('%H:%M:%S')
                
                supporter.add_value(hr, timestamp_str)
            
            # Envoyer mise à jour WebSocket (dernière valeur)
            socketio.emit('heartrate_update', {
                'supporter': supporter_id,
                'hr': hr_data[-1],
                'timestamp': base_time.strftime('%H:%M:%S'),
                'stats': supporter.stats,
                'buffer_size': len(hr_data)
            })
        
        elif isinstance(hr_data, (int, float)):
            # Format ancien : valeur unique
            timestamp_str = datetime.now().strftime('%H:%M:%S')
            supporter.add_value(int(hr_data), timestamp_str)
            
            socketio.emit('heartrate_update', {
                'supporter': supporter_id,
                'hr': int(hr_data),
                'timestamp': timestamp_str,
                'stats': supporter.stats,
                'buffer_size': 1
            })
    
    except Exception as e:
        print(f"✗ Erreur traitement message : {e}")

# ═══════════════════════════════════════════════════════════
# TEMPLATES HTML INTÉGRÉS
# ═══════════════════════════════════════════════════════════

INDEX_HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Dashboard Football</title>
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#1e3c72 0%,#2a5298 100%);min-height:100vh;padding:20px}.container{max-width:1200px;margin:0 auto}header{text-align:center;color:white;margin-bottom:50px}h1{font-size:3em;margin-bottom:10px;text-shadow:2px 2px 4px rgba(0,0,0,0.3)}.subtitle{font-size:1.2em;opacity:0.9}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:30px;margin-top:40px}.card{background:white;border-radius:15px;padding:30px;box-shadow:0 10px 30px rgba(0,0,0,0.2);transition:transform 0.3s ease;cursor:pointer;text-decoration:none;color:inherit;display:block}.card:hover{transform:translateY(-10px)}.card-icon{font-size:4em;margin-bottom:15px;font-weight:bold}.card-title{font-size:1.8em;font-weight:bold;margin-bottom:10px}.card-description{color:#666;line-height:1.6}.color-1{border-top:5px solid #3498db}.color-1 .card-icon{color:#3498db}.color-2{border-top:5px solid #e74c3c}.color-2 .card-icon{color:#e74c3c}.color-3{border-top:5px solid #2ecc71}.color-3 .card-icon{color:#2ecc71}.color-4{border-top:5px solid #f39c12}.color-4 .card-icon{color:#f39c12}.color-5{border-top:5px solid #9b59b6}.color-5 .card-icon{color:#9b59b6}.card-comparaison{border-top:5px solid #2ecc71}.card-comparaison .card-icon{color:#2ecc71}</style>
</head><body>
<div class="container"><header><h1> Dashboard Football</h1><p class="subtitle">Monitoring FC Temps Réel</p></header><div class="grid" id="grid"></div></div>
<script>const socket=io();let supporters=[];fetch('/api/supporters').then(r=>r.json()).then(data=>{supporters=data;renderCards()});function renderCards(){const grid=document.getElementById('grid');grid.innerHTML='';supporters.forEach((s,i)=>{const num=s.replace('supporter','');const colorClass='color-'+((i%5)+1);grid.innerHTML+=`<a href="/supporter/${s}" class="card ${colorClass}"><div class="card-icon">S${num}</div><div class="card-title">Supporter ${num}</div><div class="card-description">Visualisation temps réel</div></a>`});if(supporters.length>1){grid.innerHTML+=`<a href="/comparaison" class="card card-comparaison"><div class="card-icon">VS</div><div class="card-title">Comparaison</div><div class="card-description">Tous les supporters</div></a>`}}socket.on('new_supporter',(data)=>{if(!supporters.includes(data.id)){supporters.push(data.id);renderCards()}})</script>
</body></html>'''

SUPPORTER_HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{{ title }}</title>
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',sans-serif;background:#f5f7fa;padding:20px}.container{max-width:1400px;margin:0 auto}header{background:white;padding:20px 30px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin-bottom:20px;display:flex;justify-content:space-between;align-items:center}h1{color:{{ color }};font-size:2em}.back-btn{background:{{ color }};color:white;padding:10px 20px;border-radius:5px;text-decoration:none}.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:20px}.stat-card{background:white;padding:20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);text-align:center}.stat-value{font-size:2.5em;font-weight:bold;color:{{ color }}}.stat-label{color:#666;margin-top:5px;font-size:0.9em}.chart-container{background:white;padding:30px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);height:500px}</style>
</head><body>
<div class="container"><header><h1>{{ title }}</h1><a href="/" class="back-btn">← Retour</a></header><div class="stats-grid"><div class="stat-card"><div class="stat-value" id="current">-</div><div class="stat-label">FC Actuelle (BPM)</div></div><div class="stat-card"><div class="stat-value" id="avg">-</div><div class="stat-label">Moyenne</div></div><div class="stat-card"><div class="stat-value" id="min">-</div><div class="stat-label">Minimum</div></div><div class="stat-card"><div class="stat-value" id="max">-</div><div class="stat-label">Maximum</div></div><div class="stat-card"><div class="stat-value" id="count">-</div><div class="stat-label">Mesures</div></div></div><div class="chart-container"><canvas id="chart"></canvas></div></div>
<script>const supporter='{{ supporter }}';const color='{{ color }}';const ctx=document.getElementById('chart').getContext('2d');const chart=new Chart(ctx,{type:'line',data:{labels:[],datasets:[{label:'{{ title }}',data:[],borderColor:color,backgroundColor:color+'33',borderWidth:3,tension:0.4,fill:true,pointRadius:4}]},options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:false,min:40,max:200,ticks:{stepSize:20}},x:{ticks:{maxTicksLimit:10}}}}});const socket=io();socket.on('connect',()=>{fetch('/api/data').then(r=>r.json()).then(data=>{if(data[supporter]){chart.data.labels=data[supporter].times;chart.data.datasets[0].data=data[supporter].values;chart.update();updateStats(data[supporter].stats)}})});socket.on('heartrate_update',(data)=>{if(data.supporter===supporter){chart.data.labels.push(data.timestamp);chart.data.datasets[0].data.push(data.hr);if(chart.data.labels.length>100){chart.data.labels.shift();chart.data.datasets[0].data.shift()}chart.update('none');updateStats(data.stats)}});function updateStats(stats){document.getElementById('current').textContent=stats.last;document.getElementById('avg').textContent=stats.avg.toFixed(1);document.getElementById('min').textContent=stats.min;document.getElementById('max').textContent=stats.max;document.getElementById('count').textContent=stats.count}</script>
</body></html>'''

COMPARAISON_HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Comparaison</title>
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',sans-serif;background:#f5f7fa;padding:20px}.container{max-width:1600px;margin:0 auto}header{background:white;padding:20px 30px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin-bottom:20px;display:flex;justify-content:space-between}h1{color:#2ecc71;font-size:2em}.back-btn{background:#2ecc71;color:white;padding:10px 20px;border-radius:5px;text-decoration:none}.stats-container{display:flex;gap:20px;margin-bottom:20px;flex-wrap:wrap}.supporter-stats{flex:1;min-width:250px;background:white;padding:20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}.supporter-stats h2{margin-bottom:15px;padding-bottom:10px;border-bottom:3px solid}.stat-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee}.stat-label{color:#666}.stat-value{font-weight:bold;font-size:1.1em}.chart-container{background:white;padding:30px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);height:600px}</style>
</head><body>
<div class="container"><header><h1> Comparaison</h1><a href="/" class="back-btn">← Retour</a></header><div class="stats-container" id="stats"></div><div class="chart-container"><canvas id="chart"></canvas></div></div>
<script>const colors=['#3498db','#e74c3c','#2ecc71','#f39c12','#9b59b6','#1abc9c'];let supporters=[];const ctx=document.getElementById('chart').getContext('2d');const chart=new Chart(ctx,{type:'line',data:{labels:[],datasets:[]},options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:false,min:40,max:200,ticks:{stepSize:20}},x:{ticks:{maxTicksLimit:10}}}}});let allData={};let allTimes=[];function updateChart(){allTimes=Object.keys(allData).sort();if(allTimes.length>100){allTimes=allTimes.slice(-100);const newData={};allTimes.forEach(t=>newData[t]=allData[t]);allData=newData}chart.data.labels=allTimes;supporters.forEach((s,i)=>{if(!chart.data.datasets[i]){chart.data.datasets[i]={label:s.replace('supporter','S'),data:[],borderColor:colors[i%colors.length],backgroundColor:colors[i%colors.length]+'33',borderWidth:2.5,tension:0.4,pointRadius:3}}chart.data.datasets[i].data=allTimes.map(t=>allData[t][s]!==undefined?allData[t][s]:null)});chart.update('none')}function updateStats(supporter,stats){const el=document.getElementById('stats-'+supporter);if(!el){const idx=supporters.indexOf(supporter);const color=colors[idx%colors.length];const num=supporter.replace('supporter','');document.getElementById('stats').innerHTML+=`<div class="supporter-stats" id="stats-${supporter}"><h2 style="color:${color};border-color:${color}">Supporter ${num}</h2><div class="stat-row"><span class="stat-label">Actuel</span><span class="stat-value" style="color:${color}" id="${supporter}-current">-</span></div><div class="stat-row"><span class="stat-label">Moyenne</span><span class="stat-value" style="color:${color}" id="${supporter}-avg">-</span></div><div class="stat-row"><span class="stat-label">Min</span><span class="stat-value" style="color:${color}" id="${supporter}-min">-</span></div><div class="stat-row"><span class="stat-label">Max</span><span class="stat-value" style="color:${color}" id="${supporter}-max">-</span></div></div>`}document.getElementById(supporter+'-current').textContent=stats.last+' BPM';document.getElementById(supporter+'-avg').textContent=stats.avg.toFixed(1)+' BPM';document.getElementById(supporter+'-min').textContent=stats.min+' BPM';document.getElementById(supporter+'-max').textContent=stats.max+' BPM'}const socket=io();socket.on('connect',()=>{fetch('/api/data').then(r=>r.json()).then(data=>{Object.keys(data).forEach(s=>{if(!supporters.includes(s))supporters.push(s);data[s].times.forEach((time,i)=>{if(!allData[time])allData[time]={};allData[time][s]=data[s].values[i]});updateStats(s,data[s].stats)});updateChart()})});socket.on('heartrate_update',(data)=>{if(!supporters.includes(data.supporter)){supporters.push(data.supporter)}if(!allData[data.timestamp])allData[data.timestamp]={};allData[data.timestamp][data.supporter]=data.hr;updateChart();updateStats(data.supporter,data.stats)});socket.on('new_supporter',(data)=>{if(!supporters.includes(data.id)){supporters.push(data.id);updateChart()}})</script>
</body></html>'''

# ═══════════════════════════════════════════════════════════
# ROUTES FLASK
# ═══════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/supporter/<supporter_id>')
def supporter(supporter_id):
    colors = {
        'supporter1': '#3498db',
        'supporter2': '#e74c3c',
        'supporter3': '#2ecc71',
        'supporter4': '#f39c12',
        'supporter5': '#9b59b6',
        'supporter6': '#1abc9c'
    }
    color = colors.get(supporter_id, '#34495e')
    return render_template_string(SUPPORTER_HTML, 
                                 supporter=supporter_id, 
                                 title=supporter_id.replace('supporter', 'Supporter '),
                                 color=color)

@app.route('/comparaison')
def comparaison():
    return render_template_string(COMPARAISON_HTML)

@app.route('/api/data')
def get_data():
    result = {}
    for supporter_id, supporter in data_store.items():
        result[supporter_id] = supporter.get_dict()
    return jsonify(result)

@app.route('/api/supporters')
def get_supporters():
    return jsonify(list(data_store.keys()))

# ═══════════════════════════════════════════════════════════
# MQTT THREAD
# ═══════════════════════════════════════════════════════════

def mqtt_loop():
    global mqtt_client
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="web_dashboard")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()

# ═══════════════════════════════════════════════════════════
# DÉMARRAGE
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  Dashboard Web Local - Compatible Buffer V2")
    print("="*70)
    print()
    print("Démarrage du serveur web...")
    print(f"URL: http://localhost:{WEB_PORT}")
    print()
    print("Pages disponibles:")
    print(f"  - http://localhost:{WEB_PORT}/              (Accueil)")
    print(f"  - http://localhost:{WEB_PORT}/supporter/<id> (Individuel)")
    print(f"  - http://localhost:{WEB_PORT}/comparaison    (Comparaison)")
    print()
    print("✓ Détection automatique des supporters")
    print("✓ Compatible format buffer [70, 72, 74, ...]")
    print()
    
    # Démarrer MQTT dans un thread séparé
    mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
    mqtt_thread.start()
    
    # Démarrer serveur Flask
    socketio.run(app, host='0.0.0.0', port=WEB_PORT, debug=False)