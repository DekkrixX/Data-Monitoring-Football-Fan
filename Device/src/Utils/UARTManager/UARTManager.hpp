/**
 * @file UARTManager.hpp
 * 
 * @brief Déclaration de la classe UARTManager.
 *
 * Fournit une abstraction haut niveau du port série UART matériel (Serial1) pour l'émission et la réception de données brutes entre une carte électronique et un périphérique externe.
 */

#ifndef _UARTMANAGER_HPP_
#define _UARTMANAGER_HPP_

// ============================================================================
//  Import des headers externes
// ============================================================================

#include <stdexcept>
#include <Arduino.h>
#include <HardwareSerial.h>



/**
 * @class UARTManager
 * 
 * @brief Gestionnaire de communication UART sur le port série externe (Serial1).
 */
class UARTManager
{

// ============================================================================
//  Attribut
// ============================================================================

    private:
        const int rxPin;                           ///< Numéro de broche RX.
        const int txPin;                           ///< Numéro de broche TX.
        const uint32_t baudRate;                   ///< Vitesse de communication en bauds.

        HardwareSerial & externalSerial = Serial1; ///< @brief Référence vers le port série physique externe (Serial1).

// ============================================================================
//  Constructeur
// ============================================================================

    public:
        /**
         * @brief Construit un UARTManager avec les paramètres matériels donnés.
         *
         * @param rxPin    Broche RX de l'UART externe.
         * @param txPin    Broche TX de l'UART externe.
         * @param baudRate Vitesse de communication.
         */
        UARTManager(int rxPin, int txPin, uint32_t baudRate);

// ============================================================================
//  Destructeur
// ============================================================================

    public:
        /**
         * @brief Ferme le port série externe avant destruction de l'objet.
         */
        virtual ~UARTManager();

// ============================================================================
//  Méthode
// ============================================================================

    public:
        /**
         * @brief Initialise et ouvre le port série UART externe.
         */
        void begin();
        /**
         * @brief Ferme le port série UART externe.
         */
        void end();
        /**
         * @brief Envoie un seul octet sur l'UART externe.
         *
         * @param data Octet à envoyer.
         * 
         * @return size_t Nombre d'octets réellement écrits, ou 0 si le tampon d'émission est insuffisant.
         */
        size_t writeByte(uint8_t data);
        /**
         * @brief Lit un seul octet depuis l'UART externe.
         *
         * @return int Valeur de l'octet lu ou -1 si aucun octet n'est disponible.
         */
        int readByte();
        /**
         * @brief Envoie un buffer d'octets sur l'UART externe.
         *
         * @param buffer Pointeur vers les données à envoyer.
         * @param size   Nombre d'octets à envoyer.
         * 
         * @return size_t Nombre d'octets réellement écrits, ou 0 si le tampon d'émission est insuffisant.
         * 
         * @throws std::invalid_argument Si size <= 0.
         */
        size_t writeBuffer(const uint8_t * buffer, size_t size);
        /**
         * @brief Lit plusieurs octets depuis l'UART externe dans un buffer.
         *
         * @param buffer Pointeur vers le tampon de réception.
         * @param size   Nombre d'octets à lire.
         * 
         * @return size_t Nombre d'octets lus, ou -1 si pas assez de données disponibles.
         * 
         * @throws std::invalid_argument Si size <= 0.
         */
        size_t readBuffer(uint8_t * buffer, size_t size);

    private:
        /**
         * @brief Retourne le nombre d'octets disponibles en réception.
         *
         * @return int Nombre d'octets disponible dans le tampon de réception.
         */
        int availableForRead();
        /**
         * @brief Retourne le nombre d'octets disponibles en émission.
         *
         * @return int Nombre d'octets disponible dans le tampon de émission.
         */
        int availableForWrite();

};



#endif // _UARTMANAGER_HPP_
