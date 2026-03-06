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
//  Variable static
// ============================================================================

Logger * BluetoothLowEnergyManager::logger = nullptr;

// ============================================================================
//  Constructeur
// ============================================================================

BluetoothLowEnergyManager::BluetoothLowEnergyManager(const std::string & macAddress):
macAddress(macAddress),
deviceFound(false),
scan(nullptr),
client(nullptr),
device(nullptr),
scanCallbacks(nullptr),
clientCallbacks(nullptr)
{
    BluetoothLowEnergyManager::logger = new Logger("BluetoothLowEnergyManager", true);
}

// ============================================================================
//  Destructeur
// ============================================================================

BluetoothLowEnergyManager::~BluetoothLowEnergyManager()
{
    this->end();
    delete BluetoothLowEnergyManager::logger;
}

// ============================================================================
//  Méthode static
// ============================================================================

void BluetoothLowEnergyManager::notifyCallback(NimBLERemoteCharacteristic * pRemoteCharacteristic, uint8_t * pData, size_t length, bool isNotify)
{
    if (DEBUG)
    {
        char str[LOGGER_MAX_MESSAGE_SIZE];
        snprintf(str, sizeof(str), "[BLE] notifyCallback - Caractéristique: %s, %s, %u octet(s)\n", pRemoteCharacteristic->getUUID().toString().c_str(), isNotify ? "NOTIFY" : "INDICATE", length);
        BluetoothLowEnergyManager::logger->info(str);

        // Affichage hexadécimal des données brutes reçues
        snprintf(str, sizeof(str), "[BLE] Données brutes: ");
        for (size_t i = 0; i < length; i++)
        {
            char val[5];
            snprintf(val, sizeof(val), "%02X ", pData[i]);
            strcat(str, val);
        }
        BluetoothLowEnergyManager::logger->info(str);
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
    BluetoothLowEnergyManager::logger->info("[BLE] begin - Initialisation de la pile NimBLE");

    // Initialisation du stack Bluetooth Low Energy (NimBLE)
    if (not NimBLEDevice::init(""))
    {
        char str[LOGGER_MAX_MESSAGE_SIZE] = "[BLE] begin - Échec de l'initialisation de la pile NimBLE";
        BluetoothLowEnergyManager::logger->error(str);
        throw std::runtime_error(str);
    }

    // Création du client GATT
    this->client = NimBLEDevice::createClient();

    if (not this->client)
    {
        char str[LOGGER_MAX_MESSAGE_SIZE] = "[BLE] begin - Échec de la création du client GATT";
        BluetoothLowEnergyManager::logger->error(str);
        throw std::runtime_error(str);
    }

    // Enregistrement des callbacks de connexion/déconnexion
    this->clientCallbacks = new ClientCallbacks(this);
    this->client->setClientCallbacks(this->clientCallbacks);

    BluetoothLowEnergyManager::logger->info("[BLE] begin - Client GATT créé, démarrage du scan");

    // Démarrage du scan pour trouver le périphérique cible
    this->startScan();
    
    return ;
}



void BluetoothLowEnergyManager::end()
{
    BluetoothLowEnergyManager::logger->info("[BLE] end - Arrêt du gestionnaire Bluetooth Low Energy");

    // Libération des callbacks avant la destruction de NimBLE
    if (this->scanCallbacks != nullptr)
        delete this->scanCallbacks;
    if (this->clientCallbacks != nullptr)
        delete this->clientCallbacks;

    // Destruction complète de la pile NimBLE
    if (NimBLEDevice::isInitialized())
        NimBLEDevice::deinit(true);

    BluetoothLowEnergyManager::logger->info("[BLE] end - Gestionnaire Bluetooth Low Energy arrêté");

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
            char str[LOGGER_MAX_MESSAGE_SIZE];
            snprintf(str, sizeof(str), "[BLE] update - Périphérique cible (%s) non trouvé, relance du scan\n", this->macAddress.c_str());
            BluetoothLowEnergyManager::logger->info(str);

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
        char str[LOGGER_MAX_MESSAGE_SIZE];
        snprintf(str, sizeof(str), "[BLE] update - Périphérique trouvé, tentative de connexion à %s\n", this->macAddress.c_str());
        BluetoothLowEnergyManager::logger->info(str);

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
    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[BLE] getValue - Lecture de la caractéristique %s (service: %s)\n", uuidCharacteristic.c_str(), uuidService.c_str());
    BluetoothLowEnergyManager::logger->info(str);

    // Vérification de la connection du client
    if (not this->isConnected())
    {
        char str[LOGGER_MAX_MESSAGE_SIZE] = "[BLE] getValue - Client non connecté, lecture impossible";
        BluetoothLowEnergyManager::logger->error(str);
        throw std::runtime_error(str);
    }

    // Récupération du service
    NimBLERemoteService * service = this->getService(uuidService);

    // Récupération de la caractéristique
    NimBLERemoteCharacteristic * characteristic = this->getCharacteristic(uuidCharacteristic, service);

    NimBLEUUID uuid = NimBLEUUID(uuidCharacteristic);

    if (not characteristic->canRead())
    {
        std::string str = "[BLE] getValue - La caractéristique " + uuidCharacteristic + " ne supporte pas la lecture";
        BluetoothLowEnergyManager::logger->error(str.c_str());
        throw std::invalid_argument(str.c_str());
    }

    // Récupération de la valeur de la caractéristique
    NimBLEAttValue value = service->getValue(uuid);

    snprintf(str, sizeof(str), "[BLE] getValue() - Valeur lue (%u octet(s))\n", value.size());
    BluetoothLowEnergyManager::logger->info(str);

    return value;
}



void BluetoothLowEnergyManager::subscribe(const std::string & uuidService, const std::string & uuidCharacteristic)
{
    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[BLE] subscribe - Souscription à la caractéristique %s (service: %s)\n", uuidCharacteristic.c_str(), uuidService.c_str());
    BluetoothLowEnergyManager::logger->info(str);

    // Vérification de la connection du client
    if (not this->isConnected())
    {
        char str[LOGGER_MAX_MESSAGE_SIZE] = "[BLE] subscribe - Client non connecté, souscription impossible";
        BluetoothLowEnergyManager::logger->error(str);
        throw std::runtime_error(str);
    }

    // Récupération du service
    NimBLERemoteService * service = this->getService(uuidService);

    // Récupération de la caractéristique
    NimBLERemoteCharacteristic * characteristic = this->getCharacteristic(uuidCharacteristic, service);

    if (not characteristic->canNotify())
    {
        std::string str = "[BLE] subscribe - La caractéristique " + uuidCharacteristic + " ne supporte pas les notifications";
        BluetoothLowEnergyManager::logger->error(str.c_str());
        throw std::invalid_argument(str.c_str());
    }

    // Souscription à la caractéristique
    if (not characteristic->subscribe(true, BluetoothLowEnergyManager::notifyCallback))
    {
        std::string str = "[BLE] subscribe - Échec de la souscription à la caractéristique " + uuidCharacteristic;
        BluetoothLowEnergyManager::logger->error(str.c_str());
        throw std::runtime_error(str.c_str());
    }

    snprintf(str, sizeof(str), "[BLE] subscribe - Souscription établie sur %s\n", uuidCharacteristic.c_str());
    BluetoothLowEnergyManager::logger->info(str);

    return ;
}



void BluetoothLowEnergyManager::startScan()
{
    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[BLE] startScan - Démarrage du scan, cible: %s\n", this->macAddress.c_str());
    BluetoothLowEnergyManager::logger->info(str);

    // Récupération et configuration de l'objet scan NimBLE
    this->scan = NimBLEDevice::getScan();
    this->scanCallbacks = new ScanCallbacks(this);
    this->scan->setScanCallbacks(this->scanCallbacks);
    // Scan actif: envoie des requêtes SCAN_REQ pour obtenir plus d'informations
    this->scan->setActiveScan(true);
    
    // Durée 0 = scan continu jusqu'à l'appel explicite de stop()
    if (not this->scan->start(0, false))
    {
        char str[LOGGER_MAX_MESSAGE_SIZE] = "[BLE] startScan - Impossible de démarrer le scan BLE";
        BluetoothLowEnergyManager::logger->error(str);
        throw std::runtime_error(str);
    }

    return ;
}



void BluetoothLowEnergyManager::connection(const NimBLEAdvertisedDevice * device)
{
    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[BLE] connection - Connexion à %s en cours\n", device->getAddress().toString().c_str());
    BluetoothLowEnergyManager::logger->info(str);

    // Tentative de connexion au périphérique
    if (not this->client->connect(device))
    {
        char str[LOGGER_MAX_MESSAGE_SIZE];
        snprintf(str, sizeof(str), "[BLE] connection - Échec de la connexion à %s\n", device->getAddress().toString().c_str());
        BluetoothLowEnergyManager::logger->warning(str);

        return ;
    }

    snprintf(str, sizeof(str), "[BLE] connection - Connecté à %s\n", device->getAddress().toString().c_str());
    BluetoothLowEnergyManager::logger->info(str);

    return ;
}



NimBLERemoteService * BluetoothLowEnergyManager::getService(const std::string & uuidService)
{
    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[BLE] getService - Recherche du service %s\n", uuidService.c_str());
    BluetoothLowEnergyManager::logger->info(str);

    // Recherche du service GATT sur le périphérique connecté
    NimBLERemoteService * service = this->client->getService(uuidService);

    if (service == nullptr)
    {
        std::string str = "[BLE] getService - Service introuvable: " + uuidService;
        BluetoothLowEnergyManager::logger->error(str.c_str());
        throw std::invalid_argument(str.c_str());
    }
    
    return service;
}



NimBLERemoteCharacteristic * BluetoothLowEnergyManager::getCharacteristic(const std::string & uuidCharacteristic, NimBLERemoteService * service)
{
    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[BLE] getCharacteristic - Recherche de la caractéristique %s\n", uuidCharacteristic.c_str());
    BluetoothLowEnergyManager::logger->info(str);

    // Recherche de la caractéristique dans le service fourni
    NimBLERemoteCharacteristic * characteristic = service->getCharacteristic(uuidCharacteristic);

    if (characteristic == nullptr)
    {
        std::string str = "[BLE] getCharacteristic - Caractéristique introuvable: " + uuidCharacteristic;
        BluetoothLowEnergyManager::logger->error(str.c_str());
        throw std::invalid_argument(str.c_str());
    }

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

    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[BLE][SCAN] onResult - Périphérique détecté: %s\n", deviceMACAddress.toString().c_str());
    BluetoothLowEnergyManager::logger->info(str);

    // Comparaison de l'adresse MAC détectée avec la cible configurée
    if (deviceMACAddress.equals(macAddress))
    {
        char str[LOGGER_MAX_MESSAGE_SIZE];
        snprintf(str, sizeof(str), "[BLE][SCAN] onResult - Périphérique cible trouvé: %s — arrêt du scan\n", deviceMACAddress.toString().c_str());
        BluetoothLowEnergyManager::logger->info(str);

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
    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[BLE][CLIENT] onConnect - Connexion établie avec %s\n", pClient->getPeerAddress().toString().c_str());
    BluetoothLowEnergyManager::logger->info(str);

    return ;
}



void BluetoothLowEnergyManager::ClientCallbacks::onDisconnect(NimBLEClient * pClient, int reason)
{
    char str[LOGGER_MAX_MESSAGE_SIZE];
    snprintf(str, sizeof(str), "[BLE][CLIENT] onDisconnect - Déconnexion de %s (code: %d) — relance du scan au prochain update()\n", pClient->getPeerAddress().toString().c_str(), reason);
    BluetoothLowEnergyManager::logger->info(str);

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
