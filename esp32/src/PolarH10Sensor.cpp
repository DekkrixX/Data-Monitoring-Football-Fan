#include "PolarH10Sensor.h"
#include "Config.h"

// Initialisation des variables statiques
BLEUUID PolarH10Sensor::serviceUUID(Config::BLE::HR_SERVICE_UUID);
BLEUUID PolarH10Sensor::charUUID(Config::BLE::HR_CHAR_UUID);
PolarH10Sensor* PolarH10Sensor::instance = nullptr;

// =====================================================
// =========== CLASSES INTERNES (CALLBACKS) =============
// =====================================================

class PolarH10Sensor::AdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
public:
    AdvertisedDeviceCallbacks(PolarH10Sensor* sensor) : sensor(sensor) {}
    
    void onResult(BLEAdvertisedDevice advertisedDevice) override {
        String addr = advertisedDevice.getAddress().toString().c_str();
        
        if (addr.equalsIgnoreCase(sensor->macAddress)) {
            Serial.print("Detecte: ");
            Serial.print(sensor->deviceName);
            Serial.println(" trouve!");
            
            if (advertisedDevice.haveName()) {
                Serial.print("   Nom: ");
                Serial.println(advertisedDevice.getName().c_str());
            }
            Serial.print("   RSSI: ");
            Serial.print(advertisedDevice.getRSSI());
            Serial.println(" dBm");
            
            BLEDevice::getScan()->stop();
            sensor->targetDevice = new BLEAdvertisedDevice(advertisedDevice);
            sensor->doConnect = true;
        }
    }
    
private:
    PolarH10Sensor* sensor;
};

class PolarH10Sensor::ClientCallbacks : public BLEClientCallbacks {
public:
    ClientCallbacks(PolarH10Sensor* sensor) : sensor(sensor) {}
    
    void onConnect(BLEClient* pclient) override {
        Serial.println("Connecte au Polar H10!");
        sensor->connected = true;
        sensor->resetStats();
        
        if (sensor->statusCallback) {
            sensor->statusCallback(true);
        }
    }
    
    void onDisconnect(BLEClient* pclient) override {
        Serial.println("Deconnecte du Polar H10");
        sensor->connected = false;
        
        if (sensor->statusCallback) {
            sensor->statusCallback(false);
        }
    }
    
private:
    PolarH10Sensor* sensor;
};

// =====================================================
// ============== MÉTHODES PUBLIQUES ====================
// =====================================================

PolarH10Sensor::PolarH10Sensor(const String& macAddress, const String& deviceName)
    : macAddress(macAddress),
      deviceName(deviceName),
      pBLEScan(nullptr),
      pClient(nullptr),
      targetDevice(nullptr),
      connected(false),
      bleInitialized(false),
      doConnect(false),
      hrSum(0),
      scanTime(Config::BLE::SCAN_TIME),
      lastScanTime(0) {
    
    instance = this;
    sensorData.valid = false;
}

PolarH10Sensor::~PolarH10Sensor() {
    end();
    instance = nullptr;
}

bool PolarH10Sensor::begin() {
    Serial.println("[PolarH10] Initialisation BLE...");
    
    try {
        BLEDevice::init("");
        
        pBLEScan = BLEDevice::getScan();
        pBLEScan->setAdvertisedDeviceCallbacks(new AdvertisedDeviceCallbacks(this));
        pBLEScan->setActiveScan(true);
        pBLEScan->setInterval(Config::BLE::SCAN_INTERVAL);
        pBLEScan->setWindow(Config::BLE::SCAN_WINDOW);
        
        bleInitialized = true;
        Serial.println("[PolarH10] BLE initialise");
        Serial.println("[PolarH10] Recherche du Polar H10 (" + macAddress + ")...");
        
        return true;
    }
    catch (const std::exception& e) {
        Serial.print("[PolarH10] ERREUR initialisation: ");
        Serial.println(e.what());
        return false;
    }
}

void PolarH10Sensor::end() {
    if (connected && pClient) {
        pClient->disconnect();
    }
    
    if (pClient) {
        delete pClient;
        pClient = nullptr;
    }
    
    if (targetDevice) {
        delete targetDevice;
        targetDevice = nullptr;
    }
    
    BLEDevice::deinit(true);
    bleInitialized = false;
    connected = false;
}

void PolarH10Sensor::update() {
    if (!bleInitialized) {
        return;
    }
    
    // Gérer la connexion en attente
    if (doConnect) {
        if (connectToDevice()) {
            Serial.println("[PolarH10] Reception des donnees en temps reel...");
        } else {
            Serial.println("[PolarH10] Echec connexion, nouvelle tentative...");
        }
        doConnect = false;
    }
    
    // Scanner si non connecté
    if (!connected) {
        unsigned long now = millis();
        if (now - lastScanTime > 3000) {  // Scan toutes les 3 secondes
            lastScanTime = now;
            
            Serial.print("[PolarH10] Scan BLE");
            BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
            
            if (!doConnect) {
                Serial.println("\n[PolarH10] " + deviceName + " non trouve, nouvelle tentative...");
            }
            
            pBLEScan->clearResults();
        }
    }
}

bool PolarH10Sensor::isConnected() const {
    return connected;
}

SensorData PolarH10Sensor::getData() const {
    return sensorData;
}

void PolarH10Sensor::onDataReceived(std::function<void(const SensorData&)> callback) {
    dataCallback = callback;
}

void PolarH10Sensor::onStatusChanged(std::function<void(bool)> callback) {
    statusCallback = callback;
}

void PolarH10Sensor::resetStats() {
    sensorData.min = 0xFFFF;
    sensorData.max = 0;
    hrSum = 0;
    sensorData.sampleCount = 0;
    sensorData.average = 0;
}

int PolarH10Sensor::getRSSI() const {
    if (connected && pClient) {
        return pClient->getRssi();
    }
    return 0;
}

// =====================================================
// ============== MÉTHODES PRIVÉES ======================
// =====================================================

bool PolarH10Sensor::connectToDevice() {
    Serial.println("[PolarH10] Connexion BLE en cours...");
    
    pClient = BLEDevice::createClient();
    pClient->setClientCallbacks(new ClientCallbacks(this));
    
    if (!pClient->connect(targetDevice)) {
        Serial.println("[PolarH10] Echec connexion BLE");
        return false;
    }
    
    BLERemoteService* pRemoteService = pClient->getService(serviceUUID);
    if (!pRemoteService) {
        Serial.println("[PolarH10] Service Heart Rate non trouve");
        pClient->disconnect();
        return false;
    }
    Serial.println("[PolarH10] Service Heart Rate trouve");
    
    BLERemoteCharacteristic* pRemoteCharacteristic = pRemoteService->getCharacteristic(charUUID);
    if (!pRemoteCharacteristic) {
        Serial.println("[PolarH10] Caracteristique non trouvee");
        pClient->disconnect();
        return false;
    }
    Serial.println("[PolarH10] Caracteristique trouvee");
    
    if (pRemoteCharacteristic->canNotify()) {
        pRemoteCharacteristic->registerForNotify(notifyCallback);
        Serial.println("[PolarH10] Abonne aux notifications");
    }
    
    return true;
}

void PolarH10Sensor::processHeartRate(uint16_t bpm) {
    // Validation des données
    if (bpm < Config::System::VALID_HR_MIN || bpm > Config::System::VALID_HR_MAX) {
        return;
    }
    
    // Mise à jour des données
    sensorData.value = bpm;
    sensorData.timestamp = millis();
    sensorData.valid = true;
    
    // Statistiques
    if (bpm > sensorData.max) {
        sensorData.max = bpm;
    }
    if (bpm < sensorData.min) {
        sensorData.min = bpm;
    }
    
    hrSum += bpm;
    sensorData.sampleCount++;
    sensorData.average = (float)hrSum / sensorData.sampleCount;
    
    // Affichage
    Serial.print("FC: ");
    Serial.print(bpm);
    Serial.print(" BPM | Moy: ");
    Serial.print(sensorData.average, 1);
    Serial.print(" | Min: ");
    Serial.print(sensorData.min);
    Serial.print(" | Max: ");
    Serial.println(sensorData.max);
    
    // Callback si défini
    if (dataCallback) {
        dataCallback(sensorData);
    }
}

void PolarH10Sensor::notifyCallback(BLERemoteCharacteristic* pBLERemoteCharacteristic,
                                    uint8_t* pData, size_t length, bool isNotify) {
    if (instance && length > 1) {
        uint16_t bpm = pData[1];
        instance->processHeartRate(bpm);
    }
}
