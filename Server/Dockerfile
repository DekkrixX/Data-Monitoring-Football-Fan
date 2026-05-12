FROM python:3.11

WORKDIR /Server

COPY . .

RUN pip install --no-cache-dir \
    pyserial \
    paho-mqtt \
    influxdb-client \
    meshtastic \
    pypubsub \
    flask \
    flask-socketio \
    python-dotenv \
    psycopg \
    meshcore-cli
