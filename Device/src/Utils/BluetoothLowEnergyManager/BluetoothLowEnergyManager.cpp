/**
 * @file BluetoothLowEnergyManager.cpp
 * 
 * @brief Implémentation de la classe BluetoothLowEnergyManager.
 *
 * Fournit une abstraction haut niveau de la pile NimBLE pour scanner les périphériques Bluetooth Low Energy, établir et maintenir une connexion client, lire des caractéristiques GATT et s'abonner aux notifications.
 */

#ifndef _BLUETOOTHLOWENERGYMANAGER_CPP_
#define _BLUETOOTHLOWENERGYMANAGER_CPP_

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./BluetoothLowEnergyManager.hpp"

// ============================================================================
//  Constructeur
// ============================================================================

BluetoothLowEnergyManager::BluetoothLowEnergyManager(const std::string & macAddress):
macAddress(macAddress),
scan(nullptr),
client(nullptr),
device(nullptr),
deviceFound(false),
scanCallbacks(nullptr),
clientCallbacks(nullptr)
{}

// ============================================================================
//  Destructeur
// ============================================================================

BluetoothLowEnergyManager::~BluetoothLowEnergyManager()
{
    this->end();
}

// ============================================================================
//  Méthode static
// ============================================================================

void BluetoothLowEnergyManager::notifyCallback(NimBLERemoteCharacteristic * pRemoteCharacteristic, uint8_t * pData, size_t length, bool isNotify)
{
    if (DEBUG)
    {
        Serial.printf("[BLE] notifyCallback - Caractéristique: %s, %s, %u octet(s)\n", pRemoteCharacteristic->getUUID().toString().c_str(), isNotify ? "NOTIFY" : "INDICATE", length);
        Serial.flush();

        // Affichage hexadécimal des données brutes reçues
        Serial.print("[BLE] Données brutes: ");
        for (size_t i = 0; i < length; i++)
            Serial.printf("%02X ", pData[i]);
        Serial.println();
        Serial.flush();
    }

    // Délégation du traitement au capteur actif
    sensor->notify(pRemoteCharacteristic, pData, length);

    return ;
}

// ============================================================================
//  Méthode
// ============================================================================

void BluetoothLowEnergyManager::begin()
{
    if (DEBUG)
    {
        Serial.println("[BLE] begin - Initialisation de la pile NimBLE");
        Serial.flush();
    }

    // Initialisation du stack Bluetooth Low Energy (NimBLE)
    if (not NimBLEDevice::init(""))
        throw std::runtime_error("[BLE] begin - Échec de l'initialisation de la pile NimBLE");

    // Création du client GATT
    this->client = NimBLEDevice::createClient();

    if (not this->client)
        throw std::runtime_error("[BLE] begin - Échec de la création du client GATT");

    // Enregistrement des callbacks de connexion/déconnexion
    this->clientCallbacks = new ClientCallbacks(this);
    this->client->setClientCallbacks(this->clientCallbacks);

    if (DEBUG)
    {
        Serial.println("[BLE] begin - Client GATT créé, démarrage du scan");
        Serial.flush();
    }

    // Démarrage du scan pour trouver le périphérique cible
    this->startScan();
    
    return ;
}



void BluetoothLowEnergyManager::end()
{
    if (DEBUG)
    {
        Serial.println("[BLE] end - Arrêt du gestionnaire Bluetooth Low Energy");
        Serial.flush();
    }

    // Libération des callbacks avant la destruction de NimBLE
    if (this->scanCallbacks != nullptr)
        delete this->scanCallbacks;
    if (this->clientCallbacks != nullptr)
        delete this->clientCallbacks;

    // Destruction complète de la pile NimBLE
    if (NimBLEDevice::isInitialized())
        NimBLEDevice::deinit(true);

    if (DEBUG)
    {
        Serial.println("[BLE] end - Gestionnaire Bluetooth Low Energy arrêté");
        Serial.flush();
    }

    return ;
}



void BluetoothLowEnergyManager::update()
{
    // Si le périphérique n'est pas encore trouvé, vérifie l'état du scan
    if (not this->deviceFound)
    {
        // Si le scan s'est arrêté sans trouver la cible, on le relance
        if (not this->scan->isScanning())
        {
            if (DEBUG)
            {
                Serial.printf("[BLE] update - Périphérique cible (%s) non trouvé, relance du scan\n", this->macAddress.c_str());
                Serial.flush();
            }

            if (this->device)
                delete this->device;

            this->scan->clearResults();
            this->startScan();
        }
        
        return ;
    }

    // Périphérique trouvé mais pas encore connecté: tentative de connexion
    if (not this->isConnected())
    {
        if (DEBUG)
        {
            Serial.printf("[BLE] update - Périphérique trouvé, tentative de connexion à %s\n", this->macAddress.c_str());
            Serial.flush();
        }

        this->connection(this->device);
    }

    return ;
}



bool BluetoothLowEnergyManager::isConnected()
{
    return this->client->isConnected();
}



NimBLEAttValue BluetoothLowEnergyManager::getValue(const std::string & uuidService, const std::string & uuidCharacteristic)
{
    if (DEBUG)
    {
        Serial.printf("[BLE] getValue - Lecture de la caractéristique %s (service: %s)\n",
            uuidCharacteristic.c_str(), uuidService.c_str());
        Serial.flush();
    }

    // Vérification de la connection du client
    if (not this->isConnected())
        throw std::runtime_error("[BLE] getValue - Client non connecté, lecture impossible");

    // Récupération du service
    NimBLERemoteService * service = this->getService(uuidService);

    // Récupération de la caractéristique
    NimBLERemoteCharacteristic * characteristic = this->getCharacteristic(uuidCharacteristic, service);

    NimBLEUUID uuid = NimBLEUUID(uuidCharacteristic);

    if (not characteristic->canRead())
        throw std::invalid_argument("[BLE] getValue - La caractéristique " + uuidCharacteristic + " ne supporte pas la lecture");

    // Récupération de la valeur de la caractéristique
    NimBLEAttValue value = service->getValue(uuid);

    if (DEBUG)
    {
        Serial.printf("[BLE] getValue() - Valeur lue (%u octet(s))\n", value.size());
        Serial.flush();
    }

    return value;
}



void BluetoothLowEnergyManager::subscribe(const std::string & uuidService, const std::string & uuidCharacteristic)
{
    if (DEBUG)
    {
        Serial.printf("[BLE] subscribe - Souscription à la caractéristique %s (service: %s)\n",
            uuidCharacteristic.c_str(), uuidService.c_str());
        Serial.flush();
    }

    // Vérification de la connection du client
    if (not this->isConnected())
        throw std::runtime_error("[BLE] subscribe - Client non connecté, souscription impossible");

    // Récupération du service
    NimBLERemoteService * service = this->getService(uuidService);

    // Récupération de la caractéristique
    NimBLERemoteCharacteristic * characteristic = this->getCharacteristic(uuidCharacteristic, service);

    if (not characteristic->canNotify())
        throw std::invalid_argument("[BLE] subscribe - La caractéristique " + uuidCharacteristic + " ne supporte pas les notifications");

    // Souscription à la caractéristique
    if (not characteristic->subscribe(true, BluetoothLowEnergyManager::notifyCallback))
        throw std::runtime_error("[BLE] subscribe - Échec de la souscription à la caractéristique " + uuidCharacteristic);

    if (DEBUG)
    {
        Serial.printf("[BLE] subscribe - Souscription établie sur %s\n", uuidCharacteristic.c_str());
        Serial.flush();
    }

    return ;
}



void BluetoothLowEnergyManager::startScan()
{
    if (DEBUG)
    {
        Serial.printf("[BLE] startScan - Démarrage du scan, cible: %s\n", this->macAddress.c_str());
        Serial.flush();
    }

    // Récupération et configuration de l'objet scan NimBLE
    this->scan = NimBLEDevice::getScan();
    this->scanCallbacks = new ScanCallbacks(this);
    this->scan->setScanCallbacks(this->scanCallbacks);
    // Scan actif: envoie des requêtes SCAN_REQ pour obtenir plus d'informations
    this->scan->setActiveScan(true);
    
    // Durée 0 = scan continu jusqu'à l'appel explicite de stop()
    if (not this->scan->start(0, false))
        throw std::runtime_error("[BLE] startScan - Impossible de démarrer le scan BLE");

    return ;
}



void BluetoothLowEnergyManager::connection(const NimBLEAdvertisedDevice * device)
{
    if (DEBUG)
    {
        Serial.printf("[BLE] connection - Connexion à %s en cours\n", device->getAddress().toString().c_str());
        Serial.flush();
    }

    // Tentative de connexion au périphérique
    if (not this->client->connect(device))
    {
        if (DEBUG)
        {
            Serial.printf("[BLE] connection - Échec de la connexion à %s\n", device->getAddress().toString().c_str());
            Serial.flush();
        }

        return ;
    }

    if (DEBUG)
    {
        Serial.printf("[BLE] connection - Connecté à %s\n", device->getAddress().toString().c_str());
        Serial.flush();
    }

    return ;
}



NimBLERemoteService * BluetoothLowEnergyManager::getService(const std::string & uuidService)
{
    if (DEBUG)
    {
        Serial.printf("[BLE] getService - Recherche du service %s\n", uuidService.c_str());
        Serial.flush();
    }

    // Recherche du service GATT sur le périphérique connecté
    NimBLERemoteService * service = this->client->getService(uuidService);

    if (service == nullptr)
        throw std::invalid_argument("[BLE] getService - Service introuvable: " + uuidService);
    
    return service;
}



NimBLERemoteCharacteristic * BluetoothLowEnergyManager::getCharacteristic(const std::string & uuidCharacteristic, NimBLERemoteService * service)
{
    if (DEBUG)
    {
        Serial.printf("[BLE] getCharacteristic - Recherche de la caractéristique %s\n", uuidCharacteristic.c_str());
        Serial.flush();
    }

    // Recherche de la caractéristique dans le service fourni
    NimBLERemoteCharacteristic * characteristic = service->getCharacteristic(uuidCharacteristic);

    if (characteristic == nullptr)
        throw std::invalid_argument("[BLE] getCharacteristic - Caractéristique introuvable: " + uuidCharacteristic);

    return characteristic;
}

// ============================================================================
//  Callback du scan Bluetooth Low Energy
// ============================================================================

BluetoothLowEnergyManager::ScanCallbacks::ScanCallbacks(BluetoothLowEnergyManager * bleManager):
bleManager(bleManager)
{}



BluetoothLowEnergyManager::ScanCallbacks::~ScanCallbacks() = default;



void BluetoothLowEnergyManager::ScanCallbacks::onResult(const NimBLEAdvertisedDevice * advertisedDevice)
{
    // Récupération de l'adresse MAC
    const NimBLEAddress & deviceMACAddress = advertisedDevice->getAddress();
    NimBLEAddress macAddress = NimBLEAddress(this->bleManager->macAddress, 1);

    if (DEBUG)
    {
        Serial.printf("[BLE][SCAN] onResult - Périphérique détecté: %s\n", deviceMACAddress.toString().c_str());
        Serial.flush();
    }

    // Comparaison de l'adresse MAC détectée avec la cible configurée
    if (deviceMACAddress.equals(macAddress))
    {
        if (DEBUG)
        {
            Serial.printf("[BLE][SCAN] onResult - Périphérique cible trouvé: %s — arrêt du scan\n", deviceMACAddress.toString().c_str());
            Serial.flush();
        }

        // Copie du périphérique trouvé pour utilisation après l'arrêt du scan
        this->bleManager->device = new NimBLEAdvertisedDevice(*advertisedDevice);
        this->bleManager->deviceFound = true;

        // Arrêt du scan: le périphérique cible est trouvé
        NimBLEDevice::getScan()->stop();
    }

    return ;
}

// ============================================================================
//  Callback de gestion du client Bluetooth Low Energy
// ============================================================================

BluetoothLowEnergyManager::ClientCallbacks::ClientCallbacks(BluetoothLowEnergyManager * bleManager):
bleManager(bleManager)
{}



BluetoothLowEnergyManager::ClientCallbacks::~ClientCallbacks() = default;



void BluetoothLowEnergyManager::ClientCallbacks::onConnect(NimBLEClient * pClient)
{
    if (DEBUG)
    {
        Serial.printf("[BLE][CLIENT] onConnect - Connexion établie avec %s\n",
            pClient->getPeerAddress().toString().c_str());
        Serial.flush();
    }

    return ;
}



void BluetoothLowEnergyManager::ClientCallbacks::onDisconnect(NimBLEClient * pClient, int reason)
{
    if (DEBUG)
    {
        Serial.printf("[BLE][CLIENT] onDisconnect - Déconnexion de %s (code: %d) — relance du scan au prochain update()\n",
            pClient->getPeerAddress().toString().c_str(), reason);
        Serial.flush();
    }

    // Réinitialisation de l'état: un nouveau scan sera déclenché au prochain update()
    this->bleManager->deviceFound = false;

    if (this->bleManager->device != nullptr)
    {
        delete this->bleManager->device;
        this->bleManager->device = nullptr;
    }

    return ;
}



#endif // _BLUETOOTHLOWENERGYMANAGER_CPP_
