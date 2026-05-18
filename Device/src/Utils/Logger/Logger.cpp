/**
 * @file Logger.cpp
 *
 * @brief Implémentation du système de journalisation pour ESP32.
 */

#ifndef _LOGGER_CPP_
#define _LOGGER_CPP_

// ============================================================================
//  Import des headers internes
// ============================================================================

#include "./Logger.hpp"
#include "../LEDManager/LEDManager.hpp"

// ============================================================================
//  Variable externe
// ============================================================================

extern LEDManager * ledManager;

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

#if DEBUG == 1
        Serial.println("[Logger] Dossier /Logs créé");
        Serial.flush();
#endif
    }

#if DEBUG == 1
    Serial.printf("[Logger] Logger '%s' initialisé (fichier=%s)\n", name, fileEnabled ? filePath.c_str() : "désactivé");
    Serial.flush();
#endif
}

// ============================================================================
//  Destructeur
// ============================================================================

Logger::~Logger() = default;

// ============================================================================
//  Méthode static
// ============================================================================

std::string Logger::logString(const char * format, ...)
{
    va_list args;
    va_start(args, format);
    char buffer[LOGGER_MAX_MESSAGE_SIZE];
    std::vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);

    return std::string(buffer);
}

// ============================================================================
//  Méthodes publiques
// ============================================================================

void Logger::info(const std::string & message)
{
    this->write(Level::INFO, message.c_str());
    return ;
}



void Logger::warning(const std::string & message)
{
    this->write(Level::WARNING, message.c_str());
    return ;
}



void Logger::error(const std::string & message)
{
    this->write(Level::ERROR, message.c_str());

    ledManager->changeColor(LED_COLOR_ERROR);
    ledManager->turnOn();

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
#if DEBUG == 1
        Serial.printf("[Logger] ERREUR : entrée trop grande pour '%s' (%u > %u)\n",
            this->filePath.c_str(), (unsigned)entrySize, (unsigned)LOGGER_MAX_FILE_SIZE);
        Serial.flush();
#endif

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
#if DEBUG == 1
        Serial.printf("[Logger] ERREUR : fopen failed pour '%s' (errno=%d)\n",
            posixPath.c_str(), errno);
        Serial.flush();
#endif

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
#if DEBUG == 1
        Serial.printf("[Logger] ERREUR : impossible d'ouvrir '%s' pour trim (errno=%d)\n",
            posixPath.c_str(), errno);
        Serial.flush();
#endif

        return ;
    }

    fseek(fp, 0, SEEK_END);
    const size_t fileSize = (size_t)ftell(fp);
    fseek(fp, 0, SEEK_SET);

    // Allocation du buffer en PSRAM pour ne pas consommer le heap interne
    char * content = (char *)ps_malloc(fileSize + 1);

    if (!content)
    {
#if DEBUG == 1
        Serial.printf("[Logger] ERREUR : ps_malloc(%u) échoué pour trim de '%s'\n",
            (unsigned)(fileSize + 1), posixPath.c_str());
        Serial.flush();
#endif

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
#if DEBUG == 1
        Serial.printf("[Logger] ERREUR : impossible de réécrire '%s' après trim (errno=%d)\n",
            posixPath.c_str(), errno);
        Serial.flush();
#endif

        free(content);
        
        return ;
    }

    if (offset < bytesRead)
        fwrite(content + offset, 1, bytesRead - offset, fpw);

    free(content);
    fflush(fpw);
    fclose(fpw);

#if DEBUG == 1
    Serial.printf("[Logger] TrimFile '%s' : %u octets supprimés en tête\n", this->filePath.c_str(), (unsigned)offset);
#endif

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
