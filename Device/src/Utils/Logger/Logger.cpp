/**
 * @file Logger.cpp
 *
 * @brief Implémentation du système de journalisation pour ESP32.
 */

#ifndef _LOGGER_CPP_
#define _LOGGER_CPP_

// ============================================================================
//  Import des bibliothèques
// ============================================================================

#include "Logger.hpp"

// ============================================================================
//  Constructeur
// ============================================================================

Logger::Logger(const char * name, bool fileEnabled):
name(name),
fileEnabled(fileEnabled),
filePath(std::string("/Logs/") + name + ".log")
{
    // Création du dossier de logs via POSIX
    struct stat st;
    if (stat("/littlefs/Logs", &st) != 0)
    {
        mkdir("/littlefs/Logs", 0755);
        if (DEBUG)
        {
            Serial.println("[Logger] Dossier /Logs créé");
            Serial.flush();
        }
    }

    if (DEBUG)
    {
        Serial.printf("[Logger] Logger '%s' initialisé (fichier=%s)\n", name, fileEnabled ? filePath.c_str() : "désactivé");
        Serial.flush();
    }
}

// ============================================================================
//  Destructeur
// ============================================================================

Logger::~Logger() = default;

// ============================================================================
//  Méthodes publiques
// ============================================================================

void Logger::info(const char * message)
{
    this->write(Level::INFO, message);
    return ;
}



void Logger::warning(const char * message)
{
    this->write(Level::WARNING, message);
    return ;
}



void Logger::error(const char * message)
{
    this->write(Level::ERROR, message);
    return ;
}

// ============================================================================
//  Méthodes privées
// ============================================================================

void Logger::write(Level level, const char * message)
{
    const std::string timestamp = this->getTimestamp();
    const char * levelStr       = this->levelToString(level);

    // Formatage de l'entrée complète
    char entry[LOGGER_MAX_MESSAGE_SIZE + 64];
    snprintf(entry, sizeof(entry), "[%s] [%s] %s", timestamp.c_str(), levelStr, message);

    // Sortie série
    if (DEBUG)
    {
        Serial.println(entry);
        Serial.flush();
    }

    // Sortie fichier si activée
    if (this->fileEnabled)
        this->writeFile(entry);

    return ;
}



void Logger::writeFile(const char * entry)
{
    // Taille de la nouvelle entrée qu'on va écrire
    const size_t entrySize = strlen(entry);

    // Vérification que l'entrée seule ne dépasse pas la limite
    if (entrySize > LOGGER_MAX_FILE_SIZE)
    {
        Serial.printf("[Logger] ERREUR : entrée trop grande pour '%s' (%u > %u)\n",
            this->filePath.c_str(), (unsigned)entrySize, (unsigned)LOGGER_MAX_FILE_SIZE);
        Serial.flush();
        return ;
    }

    // Construction du chemin POSIX complet (préfixe /littlefs obligatoire)
    std::string posixPath = std::string("/littlefs") + this->filePath;

    // Vérification de la taille courante via POSIX
    struct stat st;
    if (stat(posixPath.c_str(), &st) == 0)
    {
        if ((size_t)st.st_size + entrySize > LOGGER_MAX_FILE_SIZE)
            this->trimFile(entrySize);
    }

    // Écriture via fopen POSIX crée le fichier s'il n'existe pas
    FILE * fp = fopen(posixPath.c_str(), "a");

    if (!fp)
    {
        Serial.printf("[Logger] ERREUR : fopen failed pour '%s' (errno=%d)\n",
            posixPath.c_str(), errno);
        Serial.flush();
        return ;
    }

    fprintf(fp, "%s", entry);
    fflush(fp);
    fclose(fp);

    return ;
}



void Logger::trimFile(size_t entrySize)
{
    // Construction du chemin POSIX complet
    std::string posixPath = std::string("/littlefs") + this->filePath;

    // Lecture intégrale du fichier via POSIX
    FILE * fp = fopen(posixPath.c_str(), "r");

    if (!fp)
    {
        Serial.printf("[Logger] ERREUR : impossible d'ouvrir '%s' pour trim (errno=%d)\n",
            posixPath.c_str(), errno);
        Serial.flush();
        return ;
    }

    fseek(fp, 0, SEEK_END);
    const size_t fileSize = (size_t)ftell(fp);
    fseek(fp, 0, SEEK_SET);

    // Allocation du buffer en PSRAM pour ne pas consommer le heap interne
    char * content = (char *)ps_malloc(fileSize + 1);

    if (!content)
    {
        Serial.printf("[Logger] ERREUR : ps_malloc(%u) échoué pour trim de '%s'\n",
            (unsigned)(fileSize + 1), posixPath.c_str());
        Serial.flush();
        fclose(fp);
        return ;
    }

    // Lecture intégrale du fichier dans le buffer PSRAM
    const size_t bytesRead = fread(content, 1, fileSize, fp);
    content[bytesRead] = '\0';
    fclose(fp);

    // Suppression des premières lignes jusqu'à libérer assez de place
    size_t offset = 0;

    while (offset < bytesRead)
    {
        // Taille restante après suppression des lignes précédentes
        const size_t remaining = bytesRead - offset;

        if (remaining + entrySize <= LOGGER_MAX_FILE_SIZE)
            break;

        // Avancer jusqu'à la fin de la ligne courante
        const char * newline = (const char *)memchr(content + offset, '\n', bytesRead - offset);

        if (!newline)
        {
            // Plus de '\n' trouvé : tout le contenu restant est une seule ligne, on vide
            offset = bytesRead;
            break;
        }

        offset = (newline - content) + 1;
    }

    // Réécriture du fichier avec le contenu trimé via POSIX
    FILE * fpw = fopen(posixPath.c_str(), "w");

    if (!fpw)
    {
        Serial.printf("[Logger] ERREUR : impossible de réécrire '%s' après trim (errno=%d)\n",
            posixPath.c_str(), errno);
        Serial.flush();
        free(content);
        return ;
    }

    if (offset < bytesRead)
        fwrite(content + offset, 1, bytesRead - offset, fpw);

    free(content);
    fflush(fpw);
    fclose(fpw);

    if (DEBUG)
        Serial.printf("[Logger] Trim '%s' : %u octets supprimés en tête\n",
            this->filePath.c_str(), (unsigned)offset);

    return ;
}



const char * Logger::levelToString(Level level) const
{
    switch (level)
    {
        case Level::INFO:
            return "INFO";
        case Level::WARNING:
            return "WARNING";
        case Level::ERROR:
            return "ERROR";
        default:
            return "UNKNOWN";
    }

    return "";
}



std::string Logger::getTimestamp() const
{
    // Utilise millis()
    unsigned long ms      = millis();
    unsigned long seconds = ms / 1000;
    unsigned long minutes = seconds / 60;
    unsigned long hours   = minutes / 60;

    char buffer[16];
    snprintf(buffer, sizeof(buffer), "%02lu:%02lu:%02lu.%03lu",
        hours   % 24,
        minutes % 60,
        seconds % 60,
        ms      % 1000);

    return std::string(buffer);
}

#endif // _LOGGER_CPP_
