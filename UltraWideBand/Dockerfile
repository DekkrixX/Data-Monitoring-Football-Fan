FROM python:3.10
WORKDIR /UltraWideBand
COPY . .

RUN pip install --no-cache-dir \
    ./UltraWideBand/uwb-qorvo-tools \
    paho-mqtt \
    numpy \
    python-dotenv
