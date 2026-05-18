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
    if (BluetoothLowEnergyManager::logger == nullptr)
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
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] notifyCallback - Caractéristique: %s, %s, %u octet(s)\n", pRemoteCharacteristic->getUUID().toString().c_str(), isNotify ? "NOTIFY" : "INDICATE", length));

    // Affichage hexadécimal des données brutes reçues
    char str[LOGGER_MAX_MESSAGE_SIZE];
    for (size_t i = 0; i < length; i++)
    {
        char val[5];
        snprintf(val, sizeof(val), "%02X ", pData[i]);
        strcat(str, val);
    }
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] Données brutes: %s\n", str));
#endif

    // Délégation du traitement au capteur actif
    sensor->notify(pRemoteCharacteristic, pData, length);

    return ;
}

// ============================================================================
//  Méthode
// ============================================================================

void BluetoothLowEnergyManager::begin()
{
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] begin - Initialisation de la pile NimBLE\n"));
#endif

    // Initialisation du stack Bluetooth Low Energy (NimBLE)
    if (not NimBLEDevice::init(""))
    {
        std::string str = Logger::logString("[BLE] begin - Échec de l'initialisation de la pile NimBLE\n");
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->error(str);
#endif
        throw std::runtime_error(str);
    }

    // Création du client GATT
    this->client = NimBLEDevice::createClient();

    if (not this->client)
    {
        std::string str = Logger::logString("[BLE] begin - Échec de la création du client GATT\n");
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->error(str);
#endif
        throw std::runtime_error(str);
    }

    // Enregistrement des callbacks de connexion/déconnexion
    this->clientCallbacks = new ClientCallbacks(this);
    this->client->setClientCallbacks(this->clientCallbacks);

#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] begin - Client GATT créé, démarrage du scan\n"));
#endif

    // Démarrage du scan pour trouver le périphérique cible
    this->startScan();
    
    return ;
}



void BluetoothLowEnergyManager::end()
{
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] end - Arrêt du gestionnaire Bluetooth Low Energy\n"));
#endif

    // Libération des callbacks avant la destruction de NimBLE
    if (this->scanCallbacks != nullptr)
        delete this->scanCallbacks;
    if (this->clientCallbacks != nullptr)
        delete this->clientCallbacks;

    // Destruction complète de la pile NimBLE
    if (NimBLEDevice::isInitialized())
        NimBLEDevice::deinit(true);

#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] end - Gestionnaire Bluetooth Low Energy arrêté\n"));
#endif

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
#if DEBUG == 1
            BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] update - Périphérique cible (%s) non trouvé, relance du scan\n", this->macAddress.c_str()));
#endif

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
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] update - Périphérique trouvé, tentative de connexion à %s\n", this->macAddress.c_str()));
#endif

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
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] getValue - Lecture de la caractéristique %s (service: %s)\n", uuidCharacteristic.c_str(), uuidService.c_str()));
#endif

    // Vérification de la connection du client
    if (not this->isConnected())
    {
        std::string str = Logger::logString("[BLE] getValue - Client non connecté, lecture impossible\n");
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->error(str);
#endif
        throw std::runtime_error(str);
    }

    // Récupération du service
    NimBLERemoteService * service = this->getService(uuidService);

    // Récupération de la caractéristique
    NimBLERemoteCharacteristic * characteristic = this->getCharacteristic(uuidCharacteristic, service);

    NimBLEUUID uuid = NimBLEUUID(uuidCharacteristic);

    if (not characteristic->canRead())
    {
        std::string str = Logger::logString("[BLE] getValue - La caractéristique %s ne supporte pas la lecture\n", uuidCharacteristic.c_str());
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->error(str);
#endif
        throw std::invalid_argument(str);
    }

    // Récupération de la valeur de la caractéristique
    NimBLEAttValue value = service->getValue(uuid);

#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] getValue() - Valeur lue (%u octet(s))\n", value.size()));
#endif

    return value;
}



void BluetoothLowEnergyManager::subscribe(const std::string & uuidService, const std::string & uuidCharacteristic)
{
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] subscribe - Souscription à la caractéristique %s (service: %s)\n", uuidCharacteristic.c_str(), uuidService.c_str()));
#endif

    // Vérification de la connection du client
    if (not this->isConnected())
    {
        std::string str = Logger::logString("[BLE] subscribe - Client non connecté, souscription impossible\n");
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->error(str);
#endif
        throw std::runtime_error(str);
    }

    // Récupération du service
    NimBLERemoteService * service = this->getService(uuidService);

    // Récupération de la caractéristique
    NimBLERemoteCharacteristic * characteristic = this->getCharacteristic(uuidCharacteristic, service);

    if (not characteristic->canNotify())
    {
        std::string str = Logger::logString("[BLE] subscribe - La caractéristique %s ne supporte pas les notifications\n", uuidCharacteristic.c_str());
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->error(str);
#endif
        throw std::invalid_argument(str);
    }

    // Souscription à la caractéristique
    if (not characteristic->subscribe(true, BluetoothLowEnergyManager::notifyCallback))
    {
        std::string str = Logger::logString("[BLE] subscribe - Échec de la souscription à la caractéristique %s\n", uuidCharacteristic.c_str());
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->error(str);
#endif
        throw std::runtime_error(str);
    }

#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] subscribe - Souscription établie sur %s\n", uuidCharacteristic.c_str()));
#endif

    return ;
}



void BluetoothLowEnergyManager::startScan()
{
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] startScan - Démarrage du scan, cible: %s\n", this->macAddress.c_str()));
#endif

    // Récupération et configuration de l'objet scan NimBLE
    this->scan = NimBLEDevice::getScan();
    this->scanCallbacks = new ScanCallbacks(this);
    this->scan->setScanCallbacks(this->scanCallbacks);
    // Scan actif: envoie des requêtes SCAN_REQ pour obtenir plus d'informations
    this->scan->setActiveScan(true);
    
    // Durée 0 = scan continu jusqu'à l'appel explicite de stop()
    if (not this->scan->start(0, false))
    {
        std::string str = Logger::logString("[BLE] startScan - Impossible de démarrer le scan BLE\n");
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->error(str);
#endif
        throw std::runtime_error(str);
    }

    return ;
}



void BluetoothLowEnergyManager::connection(const NimBLEAdvertisedDevice * device)
{
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] connection - Connexion à %s en cours\n", device->getAddress().toString().c_str()));
#endif

    // Tentative de connexion au périphérique
    if (not this->client->connect(device))
    {
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->warning(Logger::logString("[BLE] connection - Échec de la connexion à %s\n", device->getAddress().toString().c_str()));
#endif

        return ;
    }

#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] connection - Connecté à %s\n", device->getAddress().toString().c_str()));
#endif

    return ;
}



NimBLERemoteService * BluetoothLowEnergyManager::getService(const std::string & uuidService)
{
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] getService - Recherche du service %s\n", uuidService.c_str()));
#endif

    // Recherche du service GATT sur le périphérique connecté
    NimBLERemoteService * service = this->client->getService(uuidService);

    if (service == nullptr)
    {
        std::string str = Logger::logString("[BLE] getService - Service introuvable: %s\n", uuidService.c_str());
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->error(str);
#endif
        throw std::invalid_argument(str);
    }
    
    return service;
}



NimBLERemoteCharacteristic * BluetoothLowEnergyManager::getCharacteristic(const std::string & uuidCharacteristic, NimBLERemoteService * service)
{
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE] getCharacteristic - Recherche de la caractéristique %s\n", uuidCharacteristic.c_str()));
#endif

    // Recherche de la caractéristique dans le service fourni
    NimBLERemoteCharacteristic * characteristic = service->getCharacteristic(uuidCharacteristic);

    if (characteristic == nullptr)
    {
        std::string str = Logger::logString("[BLE] getCharacteristic - Caractéristique introuvable: %s\n", uuidCharacteristic.c_str());
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->error(str);
#endif
        throw std::invalid_argument(str);
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

#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE][SCAN] onResult - Périphérique détecté: %s\n", deviceMACAddress.toString().c_str()));
#endif

    // Comparaison de l'adresse MAC détectée avec la cible configurée
    if (deviceMACAddress.equals(macAddress))
    {
#if DEBUG == 1
        BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE][SCAN] onResult - Périphérique cible trouvé: %s — arrêt du scan\n", deviceMACAddress.toString().c_str()));
#endif

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
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE][CLIENT] onConnect - Connexion établie avec %s\n", pClient->getPeerAddress().toString().c_str()));
#endif

    return ;
}



void BluetoothLowEnergyManager::ClientCallbacks::onDisconnect(NimBLEClient * pClient, int reason)
{
#if DEBUG == 1
    BluetoothLowEnergyManager::logger->info(Logger::logString("[BLE][CLIENT] onDisconnect - Déconnexion de %s (code: %d) — relance du scan au prochain update()\n", pClient->getPeerAddress().toString().c_str(), reason));
#endif

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
