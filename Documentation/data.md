# Développement

## Description

Cette partie décrit l’ensemble des formats des échanges de données entre les capteurs et le serveur. Elle a pour objectif de permettre d'avoir les formats de données rapidement sans chercher dans le code.

## Capteurs

### PolarH10

Format d'envoi: JSON
{
    "t" : <string>,      # Type de capteur
    "n" : <string>,      # Nom du capteur
    "id": <int>,         # Identifiant du supporter
    "hr": [<int>, ...]   # Liste de fréquences cardiaques
}

### MinIMU-9 v6

Format d'envoi: JSON
{
    "t" : <string>,      # Type de capteur
    "n" : <string>,      # Nom du capteur
    "id": <int>,         # Identifiant de la tribune du stade
    "a" : [<float>, ...] # Liste de valeur de la norme de vecteur accélération
}

### INMP441

Format d'envoi: JSON
{
    "t" : <string>,      # Type de capteur
    "n" : <string>,      # Nom du capteur
    "id": <int>,         # Identifiant de la tribune du stade
    "a" : [<float>, ...] # Liste de valeurs de décibel
}
