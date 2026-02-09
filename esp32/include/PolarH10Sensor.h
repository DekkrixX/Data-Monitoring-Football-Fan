#ifndef POLAR_H10_SENSOR_H
#define POLAR_H10_SENSOR_H

#include "SensorInterface.h"
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

/**
 * @brief Implémentation du capteur Polar H10
 * 
 * Cette classe gère la connexion BLE avec le capteur Polar H10
 * et la réception des données de fréquence cardiaque.
 */
class PolarH10Sensor : public ISensor {
public:
    /**
     * @brief Constructeur
     * @param macAddress Adresse MAC du Polar H10
     * @param deviceName Nom du périphérique (pour affichage)
     */
    PolarH10Sensor(const String& macAddress, const String& deviceName);
    
    /**
     * @brief Destructeur
     */
    ~PolarH10Sensor() override;
    
    // Implémentation de l'interface ISensor
    bool begin() override;
    void end() override;
    void update() override;
    bool isConnected() const override;
    SensorData getData() const override;
    SensorType getType() const override { return SensorType::HEART_RATE; }
    const char* getName() const override { return deviceName.c_str(); }
    void onDataReceived(std::function<void(const SensorData&)> callback) override;
    void onStatusChanged(std::function<void(bool)> callback) override;
    void resetStats() override;
    
    /**
     * @brief Obtient le RSSI de la connexion BLE
     * @return RSSI en dBm
     */
    int getRSSI() const;
    
private:
    // Configuration BLE
    String macAddress;
    String deviceName;
    static BLEUUID serviceUUID;
    static BLEUUID charUUID;
    
    // Objets BLE
    BLEScan* pBLEScan;
    BLEClient* pClient;
    BLEAdvertisedDevice* targetDevice;
    
    // État du capteur
    bool connected;
    bool bleInitialized;
    bool doConnect;
    
    // Données capteur
    SensorData sensorData;
    uint64_t hrSum;
    
    // Timing
    int scanTime;
    unsigned long lastScanTime;
    
    // Classes internes pour callbacks BLE
    class AdvertisedDeviceCallbacks;
    class ClientCallbacks;
    
    // Méthodes privées
    bool connectToDevice();
    void processHeartRate(uint16_t bpm);
    static void notifyCallback(BLERemoteCharacteristic* pBLERemoteCharacteristic,
                              uint8_t* pData, size_t length, bool isNotify);
    
    // Pointeur statique pour accès dans callback
    static PolarH10Sensor* instance;
};

#endif // POLAR_H10_SENSOR_H
