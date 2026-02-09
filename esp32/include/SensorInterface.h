#ifndef SENSOR_INTERFACE_H
#define SENSOR_INTERFACE_H

#include <Arduino.h>
#include <functional>

/**
 * @brief Structure pour les données de capteur
 */
struct SensorData {
    uint16_t value;              // Valeur principale (ex: BPM pour capteur cardiaque)
    uint16_t min;                // Valeur minimale enregistrée
    uint16_t max;                // Valeur maximale enregistrée
    float average;               // Valeur moyenne
    uint32_t sampleCount;        // Nombre d'échantillons
    unsigned long timestamp;     // Timestamp de la mesure
    bool valid;                  // Indique si les données sont valides
    
    SensorData() : value(0), min(0xFFFF), max(0), average(0), 
                   sampleCount(0), timestamp(0), valid(false) {}
};

/**
 * @brief Énumération des types de capteurs supportés
 */
enum class SensorType {
    HEART_RATE,      // Capteur de fréquence cardiaque
    TEMPERATURE,     // Capteur de température
    ACCELEROMETER,   // Accéléromètre
    GPS,             // GPS
    PRESSURE,        // Capteur de pression
    UNKNOWN
};

/**
 * @brief Interface abstraite pour tous les capteurs
 * 
 * Cette classe définit l'interface commune pour tous les types de capteurs.
 * Chaque capteur spécifique doit hériter de cette classe et implémenter
 * les méthodes virtuelles pures.
 */
class ISensor {
public:
    virtual ~ISensor() {}
    
    /**
     * @brief Initialise le capteur
     * @return true si l'initialisation réussit, false sinon
     */
    virtual bool begin() = 0;
    
    /**
     * @brief Arrête et nettoie les ressources du capteur
     */
    virtual void end() = 0;
    
    /**
     * @brief Met à jour l'état du capteur (à appeler dans loop())
     */
    virtual void update() = 0;
    
    /**
     * @brief Vérifie si le capteur est connecté
     * @return true si connecté, false sinon
     */
    virtual bool isConnected() const = 0;
    
    /**
     * @brief Obtient les données actuelles du capteur
     * @return Structure SensorData avec les données
     */
    virtual SensorData getData() const = 0;
    
    /**
     * @brief Obtient le type de capteur
     * @return Type du capteur
     */
    virtual SensorType getType() const = 0;
    
    /**
     * @brief Obtient le nom du capteur
     * @return Nom du capteur
     */
    virtual const char* getName() const = 0;
    
    /**
     * @brief Enregistre un callback appelé lors de nouvelles données
     * @param callback Fonction callback
     */
    virtual void onDataReceived(std::function<void(const SensorData&)> callback) = 0;
    
    /**
     * @brief Enregistre un callback appelé lors de changement de statut
     * @param callback Fonction callback (bool connected)
     */
    virtual void onStatusChanged(std::function<void(bool)> callback) = 0;
    
    /**
     * @brief Réinitialise les statistiques du capteur
     */
    virtual void resetStats() = 0;
    
protected:
    std::function<void(const SensorData&)> dataCallback;
    std::function<void(bool)> statusCallback;
};

#endif // SENSOR_INTERFACE_H
