/**
 * @file BluetoothLowEnergyManager.hpp
 * 
 * @brief Déclaration de la classe BluetoothLowEnergyManager.
 *
 * Fournit une abstraction haut niveau de la pile NimBLE pour scanner les périphériques Bluetooth Low Energy, établir et maintenir une connexion client, lire des caractéristiques GATT et s'abonner aux notifications.
 */

#ifndef _BLUETOOTHLOWENERGYMANAGER_HPP_
#define _BLUETOOTHLOWENERGYMANAGER_HPP_

// ============================================================================
//  Import des headers externes
// ============================================================================

#include <string>
#include <stdexcept>
#include <NimBLEDevice.h>
#include <NimBLEScan.h>
#include <NimBLEClient.h>
#include <NimBLERemoteService.h>
#include <NimBLERemoteCharacteristic.h>

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "../../Config/setting.hpp"

// ============================================================================
//  Variable externe
// ============================================================================

#include "../../Sensor/Sensor.hpp"
extern Sensor * sensor; ///< @brief Pointeur global vers le capteur actif, utilisé dans le callback de notification.



/**
 * @class BluetoothLowEnergyManager
 * 
 * @brief Gestionnaire de connexion Bluetooth Low Energy.
 */
class BluetoothLowEnergyManager
{

    class ScanCallbacks;
    class ClientCallbacks;

// ============================================================================
//  Attribut
// ============================================================================

    protected:
        const std::string macAddress;       ///< Adresse MAC cible du périphérique Bluetooth Low Energy.

        volatile bool deviceFound;          ///< Indique si le périphérique cible a été détecté.
        
        NimBLEScan * scan;                  ///< Pointeur vers l'objet de scan NimBLE.
        NimBLEClient * client;              ///< Pointeur vers le client GATT NimBLE.
        NimBLEAdvertisedDevice * device;    ///< Périphérique trouvé lors du scan.
        ScanCallbacks * scanCallbacks;      ///< Callbacks du scan Bluetooth Low Energy.
        ClientCallbacks * clientCallbacks;  ///< Callbacks de connexion/déconnexion.

// ============================================================================
//  Constructeur
// ============================================================================

    public:
        /**
         * @brief Construit un gestionnaire Bluetooth Low Energy ciblant une adresse MAC donnée.
         *
         * @param macAddress Adresse MAC du périphérique Bluetooth Low Energy cible (format "xx:xx:xx:xx:xx:xx").
         */
        BluetoothLowEnergyManager(const std::string & macAddress);

// ============================================================================
//  Destructeur
// ============================================================================

    public:
        /**
         * @brief Libère les ressources Bluetooth Low Energy.
         */
        ~BluetoothLowEnergyManager();

// ============================================================================
//  Méthode static
// ============================================================================

    private:
        /**
         * @brief Callback statique appelé lors de la réception d'une notification GATT.
         *
         * @param pRemoteCharacteristic Caractéristique ayant émis la notification.
         * @param pData                 Données brutes reçues.
         * @param length                Taille des données en octets.
         * @param isNotify              true = notification, false = indication.
         */
        static void notifyCallback(NimBLERemoteCharacteristic * pRemoteCharacteristic, uint8_t * pData, size_t length, bool isNotify);

// ============================================================================
//  Méthode
// ============================================================================

    public:
        /**
         * @brief Initialise la pile NimBLE, crée le client et démarre le scan.
         *
         * @throws std::runtime_error Si l'initialisation NimBLE ou la création
         *         du client échoue.
         */
        void begin();
        /**
         * @brief Arrête la pile NimBLE et libère les callbacks.
         */
        void end();
        /**
         * @brief Met à jour l'état de la connexion Bluetooth Low Energy.
         */
        void update();

        /**
         * @brief Indique si le client est actuellement connecté au périphérique.
         *
         * @return true  Connecté.
         * @return false Déconnecté.
         */
        bool isConnected();
        /**
         * @brief Lit la valeur d'une caractéristique GATT.
         *
         * @param uuidService        UUID du service GATT cible.
         * @param uuidCharacteristic UUID de la caractéristique à lire.
         * 
         * @return NimBLEAttValue    Valeur brute retournée par le périphérique.
         * 
         * @throws std::runtime_error    Si le client n'est pas connecté.
         * @throws std::invalid_argument Si le service ou la caractéristique est
         *         introuvable, ou si elle n'est pas lisible.
         */
        NimBLEAttValue getValue(const std::string & uuidService, const std::string & uuidCharacteristic);
        /**
         * @brief Souscrit aux notifications d'une caractéristique GATT, délègue le traitement au capteur global via sensor->notify().
         *
         * @param uuidService        UUID du service GATT cible.
         * @param uuidCharacteristic UUID de la caractéristique à surveiller.
         * 
         * @throws std::runtime_error    Si le client n'est pas connecté ou si la
         *         souscription échoue.
         * @throws std::invalid_argument Si le service ou la caractéristique est
         *         introuvable, ou si elle ne supporte pas les notifications.
         */
        void subscribe(const std::string & uuidService, const std::string & uuidCharacteristic);

    private:
        /**
         * @brief Configure et démarre un scan Bluetooth Low Energy actif continu.
         *
         * @throws std::runtime_error Si le démarrage du scan échoue.
         */
        void startScan();
        /**
         * @brief Tente de connecter le client GATT au périphérique donné.
         *
         * @param device Pointeur vers le périphérique Bluetooth Low Energy cible.
         */
        void connection(const NimBLEAdvertisedDevice * device);
        /**
         * @brief Récupère un service GATT par son UUID.
         *
         * @param uuidService UUID du service recherché.
         * 
         * @return NimBLERemoteService * Pointeur vers le service.
         * 
         * @throws std::invalid_argument Si le service est introuvable.
         */
        NimBLERemoteService * getService(const std::string & uuidService);
        /**
         * @brief Récupère une caractéristique GATT par son UUID dans un service donné.
         *
         * @param uuidCharacteristic UUID de la caractéristique recherchée.
         * @param service            Pointeur vers le service parent.
         * 
         * @return NimBLERemoteCharacteristic * Pointeur vers la caractéristique.
         * 
         * @throws std::invalid_argument Si la caractéristique est introuvable.
         */
        NimBLERemoteCharacteristic * getCharacteristic(const std::string & uuidCharacteristic, NimBLERemoteService * service);

// ============================================================================
//  Callback du scan Bluetooth Low Energy
// ============================================================================

    private:
        /**
         * @class ScanCallbacks
         * 
         * @brief Callback NimBLE déclenché pour chaque périphérique détecté lors du scan.
         */
        class ScanCallbacks: public NimBLEScanCallbacks
        {
            private:
                BluetoothLowEnergyManager * bleManager; ///< Référence vers le gestionnaire parent.
                
            public:
                /**
                 * @brief Constructeur d'un callback de scan.
                 * 
                 * @param bleManager Pointeur vers l'instance BluetoothLowEnergyManager parente.
                 */
                ScanCallbacks(BluetoothLowEnergyManager * bleManager);
                /**
                 * @brief Destructeur d'un callback de scan.
                 */
                ~ScanCallbacks();
                /**
                 * @brief Appelé par NimBLE pour chaque périphérique annoncé détecté, Compare l'adresse MAC annoncée avec la cible. Si correspondance, sauvegarde le périphérique et arrête le scan.
                 *
                 * @param advertisedDevice Périphérique Bluetooth Low Energy détecté.
                 */
                void onResult(const NimBLEAdvertisedDevice * advertisedDevice) override;
        };

// ============================================================================
//  Callback de gestion du client Bluetooth Low Energy
// ============================================================================

    private:
        /**
         * @class ClientCallbacks
         * 
         * @brief Callbacks NimBLE déclenchés lors des événements de connexion client.
         */
        class ClientCallbacks: public NimBLEClientCallbacks
        {
            private:
                BluetoothLowEnergyManager * bleManager; ///< Référence vers le gestionnaire parent.

            public:
                /**
                 * @brief Constructeur d'un callback client.
                 * 
                 * @param bleManager Pointeur vers l'instance BluetoothLowEnergyManager parente.
                 */
                ClientCallbacks(BluetoothLowEnergyManager * bleManager);
                /**
                 * @brief Destructeur d'un callback client.
                 */
                ~ClientCallbacks();
                /**
                 * @brief Appelé par NimBLE lorsque la connexion est établie.
                 * 
                 * @param pClient Pointeur vers le client GATT connecté.
                 */
                void onConnect(NimBLEClient * pClient) override;
                /**
                 * @brief Appelé par NimBLE lors d'une déconnexion, réinitialise deviceFound à false et libère le pointeur device afin de déclencher un nouveau scan au prochain update().
                 *
                 * @param pClient Pointeur vers le client GATT déconnecté.
                 * @param reason  Code de raison de la déconnexion Bluetooth Low Energy.
                 */
                void onDisconnect(NimBLEClient * pClient, int reason) override;
        };
};



#endif // _BLUETOOTHLOWENERGYMANAGER_HPP
