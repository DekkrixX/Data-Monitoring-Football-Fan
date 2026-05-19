# Développement

## Description

Cette partie décrit l’ensemble des formats des échanges de données entre les capteurs et le serveur. Elle a pour objectif de permettre d'avoir les formats de données rapidement sans chercher dans le code.

## Capteurs

### PolarH10

Format d'envoi: JSON
{
    "t" : <int>,       # Type de capteur
    "n" : <string>,    # Nom du capteur
    "id": <int>,       # Identifiant du supporter
    "hr": [<int>, ...] # Liste de fréquences cardiaques
}
{
    "t"   : <int>,    # Type de capteur
    "n"   : <string>, # Nom du capteur
    "id"  : <int>,    # Identifiant du supporter
    "bsl" : <string>, # Location du capteur sur le corps
    "bl"  : <int>     # Niveau de batterie
}

### MinIMU-9 v6

Format d'envoi: JSON
{
    "t" : <int>,         # Type de capteur
    "n" : <string>,      # Nom du capteur
    "id": <int>,         # Identifiant de la tribune du stade
    "a" : [<float>, ...] # Liste de valeur de la norme de vecteur accélération
}

### INMP441

Format d'envoi: JSON
{
    "t" : <int>,         # Type de capteur
    "n" : <string>,      # Nom du capteur
    "id": <int>,         # Identifiant de la tribune du stade
    "a" : [<float>, ...] # Liste de valeurs de décibel
}
