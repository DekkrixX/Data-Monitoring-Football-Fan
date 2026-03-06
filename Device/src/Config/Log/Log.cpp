/**
 * @file Log.cpp
 *
 * @brief Implémentation de l'export automatique des logs LittleFS.
 */

#ifndef _LOG_CPP_
#define _LOG_CPP_

// ============================================================================
//  Import des bibliothèques
// ============================================================================

#include "./Log.hpp"

// ============================================================================
//  Constantes
// ============================================================================

static const char * DUMP_START = "<<<DUMP_START>>>"; ///< @brief Marqueur de début du dump détecté par le script bash.
static const char * FILE_START = "<<<FILE_START:";   ///< @brief Préfixe du marqueur de début de fichier suivi du chemin absolu.
static const char * FILE_END   = "<<<FILE_END>>>";   ///< @brief Marqueur de fin de fichier détecté par le script bash.
static const char * DUMP_END   = "<<<DUMP_END>>>";   ///< @brief Marqueur de fin du dump détecté par le script bash.

static constexpr uint8_t LINE_DELAY_MS = 2; ///< @brief Délai en ms entre chaque ligne envoyée.

// ============================================================================
//  Fonctions privées
// ============================================================================

/**
 * @brief Envoie le contenu d'un fichier sur le port série via l'API POSIX.
 *
 * @param path Chemin absolu du fichier sur LittleFS (ex : "/Logs/mqtt.log").
 */
static void dumpFile(const char * path)
{
    // Construction du chemin POSIX complet
    std::string posixPath = std::string("/littlefs") + path;

    FILE * fp = fopen(posixPath.c_str(), "r");

    if (!fp)
    {
        Serial.printf("<<<ERROR: Impossible d'ouvrir %s (errno=%d)>>>\n", path, errno);
        return ;
    }

    // Marqueur de début avec le chemin complet du fichier
    Serial.printf("%s%s>>>\n", FILE_START, path);

    // Envoi du contenu ligne par ligne avec délai anti-saturation
    char line[512];
    while (fgets(line, sizeof(line), fp))
    {
        // Suppression du '\n' final pour éviter le double saut de ligne avec println
        size_t len = strlen(line);
        if (len > 0 && line[len - 1] == '\n')
            line[len - 1] = '\0';

        Serial.println(line);
        delay(LINE_DELAY_MS);
    }

    Serial.println(FILE_END);
    fclose(fp);

    return ;
}

// ============================================================================
//  Fonctions publiques
// ============================================================================

void dumpLogsOnBoot()
{
    Serial.println(DUMP_START);

    // Ouverture du dossier /Logs via POSIX
    DIR * dir = opendir("/littlefs/Logs");

    if (!dir)
    {
        Serial.printf("<<<ERROR: Pas de dossier /Logs (errno=%d)>>>\n", errno);
        Serial.println(DUMP_END);
        return ;
    }

    struct dirent * entry;

    while ((entry = readdir(dir)) != nullptr)
    {
        // Filtrage des fichiers .log uniquement
        std::string name = std::string(entry->d_name);

        if (name.size() < 4 || name.compare(name.size() - 4, 4, ".log") != 0)
            continue;

        std::string filePath = std::string("/Logs/") + name;
        dumpFile(filePath.c_str());
    }

    closedir(dir);
    Serial.println(DUMP_END);

    return ;
}

#endif // _LOG_CPP_
