# Debug

## Problème de permissions

Si vous rencontrez des problèmes de permission lors de l'installation, du flash ou du lancement des serveurs. Ajouter l'utilisateur au groupe suivant:
- docker
- dialout
Pour cela utiliser les commandes suivante en remplaçant $USER par votre nom d'utilisateur.
- `sudo usermod -aG docker $USER`
- `sudo usermod -aG dialout $USER`
Une fois les commandes lancées il faut relancer le terminal pour que les changements soit actif.

## Problème d'installation de docker

Si vous rencontrez des problèmes lors de l'installation automatique de docker. Installer docker manuellement en suivant la documentation en ligne : `https://docs.docker.com/engine/install/`.
