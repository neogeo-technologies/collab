# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [6.4.3] - 2024-01-27

### Correctifs
- Redmine 25860 : Ajout d'une durée de session limitée côté Django

### Évolution
- Redmine 25836 : Publication en masse des signalements

## [6.4.2] - 2024-01-23

### Correctifs
- Redmine 24200 : Déconnexion OGS <-> GC
- Redmine 25708 : Ordre des fonds de plan perdu à la modification d'une couche
- Redmine 25837 : Plugin geOrchstra - Accès utilisateur non synchronisés dans GC

## [6.4.1] - 2024-12-24

### Correctifs
- Redmine 23954 : Saisie de lignes et polygones - clic gauche pas toujours enregistré
- Redmine 25337 : Notifications et signalement à l'état de brouillon

## [6.4.0] - 2024-11-28

### Evolutions

- Redmine 22942 : Montée de version Postgre 12 > 16
- Redmine 18861 : Montée de version Python 3.12 + django 4.2 + lib associées
- Redmine 23375 : Création de vues pour les types de signalements générées automatiquement dans un schéma métier de la BD PostgreSQL
- Redmine 23374 : Création d’un Web Component pour l’affichage de données issues de GéoContrib dans un site web tiers

### Correctifs

- Redmine 23007 : Bouton ajouter signalement visible pour multi-géométries
- Redmine 21597 : Lien vers signalement avec id - erreur si position(offset) égale à 0
- Redmine 23165 : Import CSV avec texte multiligne ne fonctionne pas


### Environement variables

- AUTOMATIC_VIEW_CREATION_MODE (default : 'type')
-> Permet de choisir le mode de création de vues automatique
-> valeurs possibles : 'type' ou 'projet'

- AUTOMATIC_VIEW_SCHEMA_NAME (default : 'Data')
-> Nom du schéma métier dans lequel vont être stockées les vues


### Processus de migration dans Docker pour la mise à jour de PostgreSQL

(Le nom des variables est à adapter à votre environnement.)

#### 1. Création d'un backup

- Éteindre tous les conteneurs :
```sh
docker-compose down
```
- Redémarrer uniquement le conteneur de la base de données :
```sh
docker-compose up -d geocontrib-db
```
- Créer un dump SQL de la base de données :
```sh
docker exec -t <nom-conteneur-postgis> pg_dump -U geocontrib -F p -f ./backup.sql geocontrib
```
- Déplacer le backup du conteneur vers un emplacement local avec un nom spécifique :
```sh
docker cp <nom-conteneur-postgis>:./backup.sql ./backup_geocontrib_recette_postgis_11.sql
```
- Vérifier le contenu du backup pour s'assurer qu'il contient bien des instructions SQL :
```sh
cat backup.sql
```
#### 2. Création d'un volume de backup
Les données sont persistantes dans un volume Docker qui n'est pas compatible entre les versions de PostgreSQL. Ce volume doit être renommé pour conserver une copie de sécurité.

- Éteindre les conteneurs :
```sh
docker-compose down
```
- Renommer le volume en le copiant dans un nouveau volume :  
Adapter le nom des volumes selon la valeur présente dans le *docker-compose.yml.*  
Attention, ces valeurs peuvent être surchargé par le *docker-compose.override.yml*.  
Par exemple, sur notre recette dans le *docker-compose.yml*, on a geocontrib_db et dans le *docker-compose.override.yml* :   
```yaml
  geocontrib_db:
      name: "geocontrib_db_${ENV_MODE}" 
```
Pour vérifier, on peut lister les volumes existants avec:
```sh
docker volume list
```
Le nom de notre volume sera dans cette exemple geocontrib_db_recette et nous pouvons nommer la copie de sauvegarde du volume (conserver le suffixe à la fin) : geocontrib_db_old_recette  
La commande résultante est:
```sh
docker run --rm -v geocontrib_db_recette:/source -v geocontrib_db_old_recette:/destination alpine ash -c "cd /source && cp -a . /destination"
```
#### 3. Vérification de la sauvegarde
Vérifier les données dans le volume copié
- Pour utiliser le volume de sauvegarde, modifiez temporairement le fichier *docker-compose.yml*, par exemple :   
```yaml
volumes:
  geocontrib_db:
  geocontrib_db_old: # ajouter le volume de sauvegarde pour qu'il soit créé
  geocontrib_media:
  geocontrib_static:

postgres:
  [...]
  volumes:
    - geocontrib_db_old:/var/lib/postgresql/data/ # changez le nom du volume utilisé par la BDD
```

- Modifier les volumes dans le *docker-compose.override.yml* le cas échéant:
```yaml
volumes:
  geocontrib_db:
    name: "geocontrib_db_${ENV_MODE}" 
  geocontrib_db_old:
    name: "geocontrib_db_old_${ENV_MODE}" 
```
- [Uniquement si l'ancien volume était utilisé par un PostgreSQL 11] La version actuelle de GC (6.4) n'est pas compatible avec PostgreSQL 11 en raison d'une incompatibilité avec la version de Django. Si cette version est utilisée, pour tester le volume de sauvegarde, il est nécessaire de modifier la version dans le fichier *.env* comme suit :
```yaml
FRONT_VERSION=6.3.0
GEOCONTRIB_VERSION=6.3.0
```
- Redémarrer les conteneurs pour procéder à la vérification dans l'application
```sh
docker-compose up -d
```
Une fois la vérification terminée, rétablissez les fichiers dans leur état d'origine.

- Supprimer l'ancien volume après validation :
```sh
docker volume rm geocontrib_db_recette
```

#### 3. Changement de version et restauration
- Mettre à jour la version de PostGIS dans le fichier *.env* :
```yaml
POSTGIS_VERSION=16-3.5-alpine
```
- Ajouter ou mettre à jour la variable suivante dans le fichier *.env* :
```yaml
CSRF_TRUSTED_ORIGINS=https://geocontrib.recette.neogeo.fr
```
Si le fichier d'environnement est versionné en utilisant GIT, modifier le fichier sur le dépot de préférence

- Pour que la nouvelle variable soit prise en compte, mettre à jour le fichier *docker-compose.yml* en faisant un ```git pull``` si nécessaire, avec l'utilisateur ```gitlab-runner```, comme les droits lui sont attribués pour l'éxécution de CI:
```sh
sudo -u gitlab-runner git pull
```

- Redémarrer uniquement le conteneur de la base de données :
```sh
docker-compose up -d geocontrib-db
```
- Copier le backup SQL dans le conteneur de la base de données :
```sh
docker cp ./backup_geocontrib_recette_postgis_11.sql geocontrib-db:/tmp/backup.sql
```
- Restaurer les données dans la nouvelle base de données :
```sh
docker exec -i <nom-conteneur-postgis> sh -c "psql -U geocontrib -d geocontrib < /tmp/backup.sql"
```

#### 4. Finalisation et nettoyage
- Redémarrer les autres conteneurs :
```sh
docker-compose up -d
```
- Vérifier les logs :
```sh
docker-compose logs --tail 100 --timestamps
```
- Supprimer l'ancien volume de sauvegarde si tout fonctionne correctement :
```sh
docker volume rm geocontrib_db_old_recette
```

## [6.3.0] - 2024-09-20

### Evolution

- Redmine 21162 : Assignation d’un signalement à un utilisateur - envoi d’un mail de notification immédiat à la personnes assignée

### Commande Django

**IMPORTANT**

Au passage entre la version 5 et la version 6 de GéoContrib, une commande doit être lancée :

L'opération consiste à faire dans le docker "...-geocontrib" ou à la racine du projet django si pas de docker :

```
./manage.py migrate geocontrib 0050 --fake
```

Pour marquer la migration 0050 comme déjà appliquée :
```
./manage.py migrate 
```

Pour appliquer toutes les migrations restantes

## [6.2.2] - 2024-09-10

### Correction

- Redmine 19725 : Accès aux documents PDF : erreur 404 à la redirection

## [6.2.1] - 2024-09-03

### Evolutions

- Redmine 22911 : Ajout du header geOrchestra
- Redmine 20757 : Créer la periodic task "Notify subscribers" automatiquement au déploiement de l'appli

### Corrections

- Redmine 19725 : Faille sécu - accès aux documents PDF d'un signalement sans authentification préalabletion vers la page de connexion du portail MRN si l'utilisateur n'est pas connecté - Correctif sur les liens des mails
- Redmine 21879 : Import signalement mix simple et multi
- Redmine 21772 : Faire fonctionner l'affichage du favicon
- Redmine 21598 : Membres du projet - pas d'erreur affichée si pas d'admin projet
- Redmine 21366 : Centre et zoom de la carte par défaut
- Redmine 21029 : Erreur console template inexistant
- Redmine 20534 : Détail d'un signalement - Ordre des champs

## [6.2.0] - 2024-07-10

### Evolutions

- Redmine 19726 : Permettre de modifier le contenu du mail via l’administration Django
- Redmine 19727 : Rendre paramétrable le fait d’envoyer une notification globale ou une notification par projet
- Redmine 19728 : Ajouter un nouveau type de notification : Notification de publication d’un document clé
- Redmine 19729 : Réorganiser les éléments affichés dans le mail de notification
- Redmine 19730 : Choisir les types de signalements apparaissant sur les notifications

## [6.1.0] - 2024-03-20

### Evolution

- Redmine 19725 : Redirection vers la page de connexion d'un portail externe si l'utilisateur n'est pas connecté

### Corrections

- Redmine 19510 : Admin Django - Le label de suppression n'est pas bon dans la table "Valeurs pré-enregistrées"
- Redmine 19670 : Édition projet - Le fond de carte ne s'affiche pas dans l'aperçu
- Redmine 20442 : Accueil projet - Ajouter un bouton pour l'import d'un JSON (non-géo)
- Redmine 20500 : Création d'un nouveau signalement en géométrie multi
- Redmine 21098 : La recherche textuelle n'est pas conservé au changement de page

### Environment variables

- SSO_LOGIN_URL_WITH_REDIRECT : chaine de caractères
-> Permet de rediriger l'utilisateur vers un lien de connexion s'il n'est pas déjà connecté.

## [6.0.0] - 2024-03-12

### Evolutions

- Redmine 19720 : Amélioration du bouton de suppression sur la carte
- Redmine 19721 : Ajouter des attributs dans les projets
- Redmine 19722 : Créer des filtres pour les attributs projet sur l'accueil de l'application
- Redmine 19723 : Sélectionner les filtres « classiques » à afficher sur l’accueil projet
- Redmine 19724 : Liste et carte – Faire de la sélection multiple dans les filtres

### Corrections

- Redmine 18836 : La recherche par adresse ne disparait pas
- Redmine 19667 : La recherche de doublon à l'import de signalement s'applique sur les signalements supprimés
- Redmine 20240 : Liste et carte - La carte passe par dessus la liste des types de signalements
- Redmine 20344 : Mettre à jour le lien vers la documentation sur l'accueil projet
- Redmine 20677 : Utilisation des flux de la geoplateforme IGN
- Redmine 20788 : Lien popup ne dirige plus vers signalement

### Environment variables

- PROJECT_FILTERS: chaine de caractère ou liste de chaînes de caractères.
-> Permet de sélectionner les filtres affichés sur la page d'accueil.

Valeurs possibles : 'access_level,user_access_level,moderation,search'
Valeur par défaut : 'access_level,user_access_level,moderation,search'

Pour n'afficher aucun filtre, la valeur doit être 'empty' (ou n'importe quelle autre valeur qui ne fait pas partie des filtres existants)

Lien vers la liste des valeurs possibles pour configurer les filtres: https://git.neogeo.fr/geocontrib/geocontrib-django/-/blob/develop/docs/documentation_technique/Docker.md?plain=1#L78

- URL_DOCUMENTATION: chaine de caractères
-> Permet de sélectionner le lien vers la doucmentation sur le bouton "?" sur l'accueil de GéoContrib

Valeur par défaut : https://www.onegeosuite.fr/docs/module-geocontrib/intro


## [5.4.0] - 2024-01-22

### Evolutions

- Redmine 19119 : Permettre la gestion de signalements non-géographiques
- Redmine 19162 : Adaptation de GéoContrib à une charte UI / UX

### Corrections

- Redmine 19670 : Édition projet - Le fond de carte ne s'affiche pas dans l'aperçu
- Redmine 19667 : La recherche de doublon à l'import de signalement s'applique sur les signalements supprimés
- Redmine 19671 : Détails signalement - lien de liaison non mis à jour
- Redmine 19672 : Édition signalement - Texte popup mal mise en forme

### Environement variables

- FONT_FAMILY (default : '')
-> Permet de changer la police

- HEADER_COLOR (default : '')
-> Permet de changer la couleur de fond de la barre de menu

- PRIMARY_COLOR (default : '')
-> Permet de changer la couleur des éléments colorés de l'application (override couelur turquoise)

- PRIMARY_HIGHLIGHT_COLOR (default : '')
-> Permet de changer la couleur de focus, survol, activation des éléments


## [5.3.6] - 2023-12-13

### Correction

- Redmine 19251 : Listes de valeurs pré-enr. - Vérification que l'option existe bien dans la liste ne fonctionne pas dans le cas où j'ai un string

## [5.3.5] - 2023-11-20

### Corrections

- Redmine 14157 : Création d'un type de signalement - Interdire les noms des champs par défaut des properties
- Redmine 18942 : notifications mails - liens de notif qui pointent sur une URL générique au lieu d'une URL d'accès direct au signalement

## [5.3.4] - 2023-10-20

### Corrections

- Redmine 18568 : Certains liens vers signalement en parcours rapide sont invalides
- Redmine 18401 : Les listes de valeurs pré-définies ne se rafraichissent pas
- Redmine 17338 : Page mon compte - Activer le parcours des signalements
- Redmine 17139 : Page édition signalement - pas de suppression attribut liste pré-enregistrée ou liste
- Redmine 16896 : Import signalement - pas de rafraichissement des signalements sur la page du projet
- Redmine 18644 : Problème d'affichage sur les tool tip (message de description bouton)
- Redmine 18666 : Les formulaires de listes à choix multiples ne se rafraichissent pas
- Redmine 18757 : Export - Champs perdus
- Redmine 18568 : Certains liens vers signalement en parcours rapide sont invalides
- Redmine 18736 : Parcours de signalement & édition rapide - erreur de détection de changement avec booléens

## [5.3.3] - 2023-10-13

### Evolution

- Redmine 18514 : Rendre possible l'affichage des WMTS pour les fonds de plan

### Corrections

- Redmine 16896 : Import signalement - pas de rafraichissement des signalements sur la page du projet
- Redmine 17139 : Page édition signalement - pas de suppression attribut liste pré-enregistrée ou liste
- Redmine 17338 : Page mon compte - Activer le parcours des signalements
- Redmine 18500 : Derniers signalements absents sur page d'accueil suite passage aux signalements MVT
- Redmine 18666 : Les formulaires de listes à choix multiples ne se rafraichissent pas
- Redmine 18644 : Problème d'affichage sur les tool tip (message de description bouton)

## [5.3.2] - 2023-09-13

### Corrections

- Redmine 18295 : Paramétrage de l'affichage des signalement - La page ne n'affiche plus

## [5.3.1] - 2023-09-13

### Corrections

- Redmine 18186 : Géolocalisation : lenteurs / fonction KO de manière aléatoire
- Redmine 18185 : Prévisualisation des champs illisible
- Redmine 18184 : Temps de chargement carte accueil très lent
- Redmine 18130 : Améliorer l'affichage du logo dans la barre de menu
- Redmine 18124 : Accueil projet - Les libellés sont coupés au milieu d'une lettre

## [5.3.0] - 2023-09-01

### Evolutions

- Redmine 17473 : Zoomer sur la carte en fonction de la localisation
- Redmine 17474 : Ajouter un geocodeur ETALAB sur les cartes
- Redmine 17475 : Affichage des informations attributaires dans la pop-up au clic sur les signalements
- Redmine 17858 : Adaptation de la barre de menu pour logo hors format

### Corrections

- Redmine 18160 : Duplication des champs dans le formulaire de visualisation

## [5.2.0] - 2023-08-22

### Evolutions

- Redmine 17413 : Nouveau formulaire de création des listes de valeurs
- Redmine 17602 : Activer la recherche dans une liste de valeurs classique
- Redmine 17605 : Afficher la valeur d'un champ selon la valeur d'un autre champ
- Redmine 17628 : Forcer la valeur d'un champ selon une condition

## [5.1.3] - 2023-08-22

### Corrections

- Redmine 17962 : Gestion de la concurrence des sessions avec WordPress
- Redmine 17966 : Limiter la validité du token à 24h
- Redmine 17963 : Affichage des projets erroné avec la connexion WordPress

## [5.1.2] - 2023-08-09

### Corrections

- Redmine 17876 : Paramètre - Enlever le bouton de création d'un utilisateur dans le back office Django
- Redmine 17876 : Paramètre - Enlever le bouton de déconnexion

### Environement variables

- HIDE_USER_CREATION_BUTTON (default : false)
-> permet de cacher le bouton de creation d'un utilisateur dans l'admin Django

- LOGOUT_HIDDEN (default false)
-> permet de cacher le bouton de déconnexion dans le backend Django

## [5.1.1] - 2023-08-03

### Corrections

- Redmine 17824 : Fond de plan qui ne se rafraichit pas en édition rapide
- Redmine 17877 : Détail d'un signalement - Mauvais affichage du nom du type de signalement d'un signalement s'il est trop long

## [5.1.0] - 2023-07-12

### Evolution

-  Redmine 17472 : Connexion annuaire WP et GéoContrib

## [5.0.0] - 2023-06-30

### Evolutions

- Redmine 14470 : Fusionner l'API projet type avec l'API projet 
- Redmine 16246 : Ajouter un filtre sur la querystring pour récupérer les signalement modifié depuis une certaine date
- Redmine 16253 : Connexion QR code - Ticket 3 : point d'entrée API GET /user-info
- Redmine 16254 : Connexion QR code - Ticket 4 : Middleware pour récupérer le token + envoi du token
- Redmine 16649 : Listes de valeurs pré-enregistrées - Amélioration point d'entrée
- Redmine 16826 : Augmenter la capacité des fichiers importés
- Redmine 17372 : Ajouter une fonctionnalité de mise en plein écran de la carte


## [4.2.3] - 2023-06-29

### Corrections

- Redmine 16399 : Accueil projet - Clic sur un commentaire dans "Derniers commentaires" donne une erreur
- Redmine 16768 : Suppression d'un signalemement depuis le détail d'un signalement
- Redmine 16825 : Page du projet - Le zoom via la molette de la souris ne fonctionne pas
- Redmine 16826 : Augmenter la capacité des fichiers importés
- Redmine 16873 : Page d'accueil du projet - Clic sur un signalement sur la carte, mauvais signalement affiché
- Redmine 16897 : Import signalement | tooltip masqué et problèmes affichage
- Redmine 16905 : Import signalement | formulaire non désactivé
- Redmine 17171 : Dropdown - sélection effacée
- Redmine 17145 : Ajout signalement - champs personnalisés trop serré
- Redmine 17201 : Carte passant au dessus du footer
- Redmine 17202 : Loader et popup apparaisent au milieu de la page et non de la fenêtre
- Redmine 17219 : Liaison signalement - duplication dédoublée

## [4.2.2] - 2023-03-03

### Correction

- Redmine 16287 : Liste de valeurs pré-enregistrées - La valeur ne s'affiche pas après l'avoir sélectionnée

## [4.2.1] - 2023-02-07

### Evolutions

- Redmine 15851 : Liste de valeurs pré-enregistrées - Pouvoir rechercher des caractères à l'intérieur de la chaîne
- Redmine 15805 : Parcours de signalements - Activer le parcours après la création et l'édition d'un signalement

### Corrections

- Redmine 15806 : Mini map détail de signalement - Les fonds apparaissent de façon aléatoire
- Redmine 15889 : Edition d'un signalement - Redirection vers la page de détail ne fonctionne plus
- Redmine 15794 : Modification des attributs en masse - Copie de tous les attributs si le champ est laissé vide
- Redmine 15793 : Edition d'un projet - Affichage incorrect des informations du projet

## [4.2.0] - 2023-01-16

### Evolutions

- Redmine 15534 : Amélioration du parcours de signalements - Activer le parcours de signalements sur tous les clics sur un signalement + affichage du tri et du filtre courants
- Redmine 15526 : Amélioration du parcours de signalements - Ajouter une configuration du tri et du filtre par défaut à la création / édition d'un projet
- Redmine 15399 : Paramétrage projet - Amélioration de l'ergonomie du choix de l'échelle max

### Correction

- Redmine 15393 : Opacité symbologie du signalement

## [4.1.1] - 2022-11-21

### Corrections

- Redmine 15118 : Création d'un signalement - Affichage incomplet des titres des champs personnalisés au-delà d’un certain nombre de caractères
- Redmine 15116 : Edition des statuts en masse des signalements - Suppression des infos attributaires
- Redmine 15115 : Accueil projet - Affichage des commentaires incohérent
- Redmine 15106 : Création d'un type de signalements - Ordre des champs personnalisés incorrect

## [4.1.0] - 2022-10-13

### Evolution

- Redmine 14895 : Ajouter un champ "Liste à choix multiples" dans les champs personnalisés

## [4.0.0] - 2022-10-12

### Evolutions

- Redmine 14606 : Mise à jour psycopg2 en 2.9
- Redmine 14427 : Listes de valeurs pré-enregistrées et auto-complétion à la saisie d'un signalement
- Redmine 14383 : Permettre la visualisation, l'import et l'export de géométries-multiples 
- Redmine 14360 : Modification des informations attributaires de plusieurs signalements issus du même type
- Redmine 14359 : Snap sur les objets existants à la création / édition d'un signalement
- Redmine 14358 : Permettre la rédaction en Markdown de la description d'un projet et limiter l'affichage sur l'accueil
- Redmine 14347 : Pouvoir rendre obligatoire la saisie des signalements
- Redmine 14000 : Ajouter un endpoint API avec le numéro de version de Geocontrib et de celery
- Redmine 12748 : Améliorer l'abonnement ou le désabonnement à un projet

## [3.3.2] - 2022-11-21

### Corrections

- Redmine 15116 : Edition des statuts en masse des signalements - Suppression des infos attributaires
- Redmine 15115 : Accueil projet - Affichage des commentaires incohérent
- Redmine 15106 : Création d'un type de signalements - Ordre des champs personnalisés incorrect

## [3.3.1] - 2022-10-12

### Corrections

- Redmine 14894 : Edition de la géométrie - Amélioration ergonomie
- Redmine 14884 : Création d'un type par import GeoJSON - Le nom du type et les attributs ne sont pas récupérés
- Redmine 14871 : Mode édition rapide - Mise à jour de la symbologie instantanée
- Redmine 14758 : Pagination de la liste des projets en page d'accueil
- Redmine 14686 : Type de signalement - Le champ "Options" d'une liste de valeurs est limité à 256 caractères
- Redmine 14023 : Un utilisateur anonyme peut affecter des droits dans un projet via l'API

## [3.3.0] - 2022-08-30

### Evolutions

- Redmine 13577 : Mode déconnecté - Empêcher d'ajouter des commentaires en mode déconnecté
- Redmine 13575 : Mode déconnecté - Désactiver les filtres dans la page liste et carte
- Redmine 13572 : Mode déconnecté - Marquer que les informations de la page « type de signalement » n'ont pas été chargées si non mise en cache
- Redmine 13571 : Mode déconnecté - Empêcher la localisation d'un signalement via une photo géolocalisée
- Redmine 13569 : Mode déconnecté - Empêcher l'ajout d'une pièce jointe dans un signalement
- Redmine 13568 : Mode déconnecté - Afficher une icône qui indique à l'utilisateur qu'il est en mode déconnecté

### Corrections

- Redmine 14586 : Création d'un type de signalement à partir d'un GeoJSON ou d'un CSV - Les nombres entiers et décimaux ne sont pas détectés


## [3.2.0] - 2022-08-17

### Evolutions

- Redmine 14074 : Personnalisation du niveau de zoom maximum de la carte par projet
- Redmine 14072 : Mode édition rapide des signalements
- Redmine 14071 : Pouvoir parcourir l'ensemble des signalements à partir de la page de détail d'un signalement
- Redmine 14051 : Changer la couleur en fonction de l'état d'une case à cocher
- Redmine 14048 : Changer la couleur en fonction de l'état d'une chaine de caractères : vide et renseigné
- Redmine 13983 : Pouvoir définir une couleur sans remplissage pour les polygones

### Corrections

- Redmine 14570 : Import dans un type existant - Les types nombre entier, nombre décimal et date créent un bug à l'import
- Redmine 14567 : Création d'un signalement - Les labels des champs personnalisés ne s'affichent pas
- Redmine 14479 : Page membres - message de confirmation arrive tard
- Redmine 14463 : Responsive - débordement import fichier
- Redmine 14462 : Bouton filtres mal placé et flêche inconsistante
- Redmine 14461 : Responsive - Filtre écrasés sur page des projets
- Redmine 14460 : Responsive - les grands titres débordent et en édition rapide champ très petit
- Redmine 14458 : Responsive - description projet mal disposée
- Redmine 14454 : Responsive - espace vide sur liste signalement
- Redmine 14451 : Déconnecté - détection offline trop lente
- Redmine 14450 : Édition type de signalement - ordre par position pas respecté
- Redmine 14416 : Ajout de commentaire ne fonctionne plus

## [3.1.0] - 2022-06-08

### Evolutions

- Redmine 13365 : Import et export - Format CSV pour les ponctuels
- Redmine 13322 : Migration vers OpenLayers
- Redmine 12384 : Supprimer les templates DJANGO
- Redmine 11860 : Page du signalement - affichage du type de signalement
- Redmine 9400 : Déplacer les cadres dans "Mon compte"
- Redmine 13600 : Mise en place de tests automatiques
- Redmine 13742 : Docker étendue des cartes de signalement configurables

### Corrections

- Redmine 13934 : L'ordre des couches de la légende est inversé
- Redmine 13910 : Pièce jointe - Image géolocalisée ne s'enregistre pas en pièce jointe
- Redmine 13902 : Importer une image géoréférencée - Améliorer l'ergonomie
- Redmine 13848 : Si on n'est pas connecté, on ne vois pas les fonds de plan customisés
- Redmine 13844 : Gestionnaire métier ne peux pas créer un signalement
- Redmine 13833 : Modèle de projet : Image du projet modèle disparaît lors de la suppression d'un projet issu de ce modèle (sur version 3.0.3)
- Redmine 13788 : Création d'un projet depuis un modèle - Erreur à la création du projet
- Redmine 13948 : Edition d'un type de signalement - Impossible de modifier les champs personnalisés
- Redmine 13916 : Admin Django - La création de vues postgreSQL ne fonctionne plus
- Redmine 13799 : Liste et carte - Rechargement de l'appli au clic sur un signalement sur la carte
- Redmine 13789 : Cartes - A la création ou l'édition d'un signalement, il est possible de modifier les autres signalements
- Redmine 13695 : Page d'accueil projet - Rétablir le bouton "Voir tous les signalements"
- Redmine 13359 : Supression / Archivage auto - Désactiver la fonctionnalité
- Redmine 13696 : Page d'accueil projet - Erreur a la supression d'un type de signalement

### Docker settings change

- DEFAULT_MAP_VIEW_CENTER valeur par défaut : '[47.0, 1.0]'
- DEFAULT_MAP_VIEW_ZOOM valeur par défault 4

## [3.0.6] - 2022-06-17

### Correction

- Redmine 14159 : Liste et carte - Impossible cliquer sur les signalements s'ils sont filtrées et paginées

## [3.0.5] - 2022-05-25

### Corrections

- Redmine 13910 : Pièce jointe - Image géolocalisée ne s'enregistre pas en pièce jointe
- Redmine 13902 : Importer une image géoréférencée - Améliorer l'ergonomie
- Redmine 13848 : Si on n'est pas connecté, on ne vois pas les fonds de plan customisés
- Redmine 13844 : Gestionnaire métier ne peux pas créer un signalement
- Redmine 13833 : Modèle de projet : Image du projet modèle disparaît lors de la suppression d'un projet issu de ce modèle (sur version 3.0.3)

## [3.0.4] - 2022-05-04

### Corrections

- Redmine 13828 : Vue carte : la fermeture d'une popup renvoie sur la page d'accueil de l'application

## [3.0.3] - 2022-21-04

### Corrections

- Redmine 13498 : Accueil GéoContrib - Les filtres ne fonctionnent plus
- Redmine 13277 : Mode déconnecté - L'envoi d'une modification de signalement ne fonctionne plus
- Redmine 13263 : Mode déconnecté - Revoir la mise en cache automatique

## [3.0.2] - 2022-30-03

### Corrections

- Redmine 13361 : Responsive design - bouton de logout disparait de la barre de menu
- Redmine 13321 : Mode déconnecté - Conserver le cache dans le navigateur après rafraichissement de la page
- Redmine 13305 : Liaison entre les signalements - Erreur 400 à l'enregistrement
- Redmine 13240 : Responsive design - Sur la vue liste, le sélecteur modifier/supprimer en masse ne s'affiche pas
- Redmine 13238 : Responsive design - Affichage du clavier au clic sur la map dans la page Liste et Carte
- Redmine 13226 : Page d'accueil - Si l'utilisateur est anonyme, il n'a plus accès aux projets dont la visibilité est à "anonyme"
- Redmine 13183 : Page mon compte - récupérer les projets sans pagination et par utilisateur
- Redmine 13084 : URLs personnalisées - rendre visible à nouveau les cadres de "mon compte" avec les infos du projet cloisonné

## [3.0.1] - 2022-17-02

### Corrections

- Redmine 13111 : Suppression des signalements en masse - Affichage en erreur de la vue carte
- Redmine 13110 : Accueil du projet - Rétablissement pop-up du clic sur les signalements sur la carte

## [3.0.0] - 2022-09-02

### Evolutions

- Redmine 12779 : URLs personnalisées pour le partage d'un projet en externe
- Redmine 12379 : Page des projets - Affichage adapté à l'utilisateur, filtrages, pagination
- Redmine 12378 : Import de données de IDGO (Plugin IDGO)
- Redmine 11834 : Changement des status des signalements de façon multiple
- Redmine 12720 : Passage à Django 3.2
- Redmine 12841 : Symbologie - Création du formulaire de modification de la couleur de la symbo pour les linéaires et les surfaciques

### Corrections

- Redmine 12996 : Les statuts dans le tableau ne sont pas mis à jour suite à une modification en masse
- Redmine 12997 : Les envois d'emails sont incomplets suite à une modification des statuts en masse

## [2.3.9] - 2022-07-07

### Corrections

- Redmine 14268 : Administration des fonds cartographiques - Duplication des couches quand on les intervertit
- Redmine 14234 : Liste et carte - Erreur couches requêtables avec plusieurs fonds

## [2.3.8] - 2022-05-25

### Evolution

- Redmine 13742 : Docker étendue des cartes de signalement configurables

### Corrections

- Redmine 13934 : L'ordre des couches de la légende est inversé
- Redmine 13910 : Pièce jointe - Image géolocalisée ne s'enregistre pas en pièce jointe
- Redmine 13902 : Importer une image géoréférencée - Améliorer l'ergonomie
- Redmine 13848 : Si on n'est pas connecté, on ne vois pas les fonds de plan customisés
- Redmine 13844 : Gestionnaire métier ne peux pas créer un signalement
- Redmine 13833 : Modèle de projet : Image du projet modèle disparaît lors de la suppression d'un projet issu de ce modèle (sur version 3.0.3)
- Redmine 13788 : Création d'un projet depuis un modèle - Erreur à la création du projet
- Redmine 13781 : Contributeur et Super-contributeurs ne reçoivent plus les notifications de modération

### Docker settings change

- DEFAULT_MAP_VIEW_CENTER valeur par défaut : '[47.0, 1.0]'
- DEFAULT_MAP_VIEW_ZOOM valeur par défault 4

## [2.3.7] - 2022-05-04

### Corrections

- Redmine 13828 : Vue carte : la fermeture d'une popup renvoie sur la page d'accueil de l'application

## [2.3.6] - 2022-04-29

#### Corrections

- Redmine 13775 : Liste et carte - Les fonds cartographiques se placent au dessus des signalements au clic sur un fond
- Redmine 13748 : Nombre de caractères dans le nom du signalement
- Redmine 13737 : L'ordre des fonds cartographiques est modifié à l'enregistrement

## [2.3.5] - 2022-03-31

#### Corrections

- Redmine 13277 : Mode déconnecté - L'envoi d'une modification de signalement ne fonctionne plus
- Redmine 13263 : Mode déconnecté - Revoir la mise en cache automatique

## [2.3.4] - 2022-03-14

#### Corrections

- Redmine 13354 : Droit de l'adminstrateur d'un projet
- Redmine 13296 : Vue liste : problème de rechargement du tableau suite à une suppression en masse
- Redmine 13278 : Vue Liste & Carte - le message de l'info bulle de suppression n'est pas bon
- Redmine 13260 : Accueil du projet - Création d'un bouton vers la page Liste et Carte

## [2.3.3] - 2022-02-02

### Evolutions

- Redmine 12846 : Rendre la variable DEFAULT_BASE_MAP configurable

### Corrections

- Redmine 12917 : CAS : pas de recopie du mail dans Geocontrib quand l'utilisateur se connecte avec le CAS
- Redmine 11892 : Affichage index - optimisation de l'affichage des niveaux d'autorisation

## [2.3.2] - 2022-01-12

### Evolutions

- Redmine 12739 : Amélioration de tables Django
- Redmine 11912 : Permettre la suppression d'un projet et/ou d'un type de signalement


### Evolution en BETA

 - Redmine 11087 : Biblio de pictos - Signalements ponctuels


### Corrections

- Redmine 12030 : Ajout d'un commentaire - Empêcher la création du commentaire si le commentaire est vide
- Redmine 12559 : Page de connexion - Il est possible d'accéder à la page de connexion alors qu'on est connecté
- Redmine 11992 : Faire marcher l'envoi de mail
- Redmine 12702 : Liaison entre les signalement - Champ de sélection du signalement sensible à la casse
- Redmine 12339 : Import de signalements - Ne pas autoriser l’import de signalements « en cours de publication » dans un projet non-modéré



## [2.3.1] - 2021-12-13

### Corrections

- Simplifie déploiement docker (LOG_URL devient une string dans template de configuration du front)

## [2.3.0] - 2021-12-08

### Evolutions

- Redmine 11784 : Faire un pagination sur les liste de features en se basant sur le back
- Redmine 11081 : Amélioration des performances en cas de grand nombre de signalements
- Redmine 9784 : Avoir un statut intermédiaire entre contributeur et modérateur : Super Contributeur

### Evolution en BETA

 - Redmine 11087 : Biblio de pictos - Signalements ponctuels

### Corrections

- Redmine 11332 : filtrage dans la page "liste et carte"
- Redmine 11320 : Nombre de signalements sur la page "type de signalement"
- Redmine 11264 : Ajout de la table Attachement dans Django

## [2.2.0] - 2021-11-12

### Evolutions

- Redmine 12131 : Ajouter un endpoint API qui sort des signalements en MVT
- Redmine 12084 : Filtrage des droits projets par niveau
- Redmine 10911 : Revoir la page de gestion des membres d'un projet
- Redmine 9753 : Rajouter une colonne avec dernier éditeur dans la liste des signalements


### Evolutions en BETA

- Redmine 11084 : Supprimer en masse des signalements
- Redmine 12363 : Droits contributeur - Modification de signalement publié


### Corrections

- Redmine 12343 : Page inconnue - Corriger une faute
- Redmine 12306 : Création et édition d'un type de signalement - Suppression de tous les champs personnalisés
- Redmine 12249 : Liste et carte - Clic sur un signalement puis Clic sur son type de signalement : erreur
- Redmine 12064 : Dropdown affiche mauvais champs
- Redmine 12063 : Options invalides pour custom form
- Redmine 12060 : Export des signalements publiés


### Docker settings change

- La configuration du front est desormais générer par le back : il faut la placer dans un volume docker partagé entre les deux containers:

```yaml
  geocontrib
    volumes:
      - geocontrib_config_front:/home/apprunner/geocontrib_app/config_front

  front:
    volumes:
      - geocontrib_config_front:/opt/geocontrib/config/:ro

```

### Extra operations:

- Database migration needed:

    python manage.py migrate

## [2.1.2] - 2021-10-15

### Evolutions en BETA

- Redmine 11913 Création d'un signalement en mode déconnecté
- Redmine 12008 Passer la synchro LDAP en tâche celery.

### Corrections

- Redmine 11770 Création de fonds cartographique sans titre : fonds créé, pas de message d'erreur
- Redmine 12032 Import image géoréférencée - Mettre le formulaire dans une pop-up
- Redmine 12024 Création type de signalement - Liste déroulante, expliquer comment faire
- Redmine 12015 Ajout d'un commentaire - Refresh de la page et message, ne marche plus
- Redmine 12014 Ajout d'une pièce jointe - Accepte les mauvais formats
- Redmine 12012 Création type de signalement - Erreur nom dupliqué mais création quand même
- Redmine 11994 Erreur de clé dupliqué sur le détail d'une feature
- Redmine 11955 Création type de signalement - Nom du champs en double, erreur mais pas sur interface
- Redmine 11954 Création type de signalement - Position du champ personnalisé ne fonctionne pas
- Redmine 11953 Création type de signalement - Position du champ personnalisé, deux positions égales et pas d'erreur
- Redmine 11952 Suppression d'un signalement - Erreur 400
- Redmine 11951 Suppression d'un signalement - Permissions
- Redmine 11949 Liste des signalements - Erreurs d'affichage
- Redmine 11944 Container map non trouvé
- Redmine 11943 Carte grise
- Redmine 11932 Permissions - Contributeurs peuvent éditer le type de signalement
- Redmine 11931 Membres - Chargement
- Redmine 11927 Page du signalement - Formatage de la date / heure
- Redmine 11926 Membres - Message de validation des changements
- Redmine 11907 Création des fonds carto - Intervertir les couches par Drag and Drop
- Redmine 11875 Ecriture et édition du statut d'un signalement - Permissions
- Redmine 11982 faire marcher geocontrib sous une url http://localhost/geocontrib
- Redmine 11850 Signalement doublon - Lien de redirection erroné
- Redmine 11833 Création des fonds carto - Affichage multiple des couches disponibles
- Redmine 11791 Erreur 400 à l'enregistrement de la modification d'un type de signalement
- Redmine 11785 Page "Mon compte", corriger affichage des 3 cadres "Mes derniers... "
- Redmine 12049 Ajout d'un commentaire - Empêcher l'ajout d'une pièce jointe corrompue
- Redmine 12045 Abonnement à un projet - Un utilisateur non-connecté ne doit pas pouvoir s'abonner à un projet
- Redmine 12044 Recherche de signalements - Enlever "en attente de publication" du menu déroulant Statut
- Redmine 12028 Page du signalement - Affichage des champs booléens
- Redmine 12027 Signalement par géolocalisation - Message d'erreur
- Redmine 12013 Liste et carte - Ajout d'un signalement sans type de signalement créé
- Redmine 12010 Edition d'un signalement - champs booléens remis à Fals
- Redmine 11915 Création d'un signalement - Chargement


## [2.1.1] - 2021-10-09

### Corrections

- Beaucoup de bugs corrigés

### Remarques

Cette version a le BASE\_URL fixé à /geocontrib

## [2.1.0] - 2021-09-29

### Changements

- Redmine 11133 : Mise à jour de signalements lors de l'import
- Redmine 11084 : Supprimer en masse des signalements
- Redmine 11083 : Full responsive design

## [2.0.0] - 2021-09-21

### Changements

- Redmine 10665: handle GeoJSON import in the background
- Redmine 9671: Use attribute status when importing GeoJSON files
- Redmine 9671: Exports all user available features, even when status is draft
- Redmine 9701: Creates a Feature Type from an GeoJSON file
- Redmine 9701: GeoJSON import : ignore the GeoJSON feature\_type
- Redmine 9701: GeoJSON import : add some logs
- Redmine 11085: Mode disconnected / New VueJS interface https://git.neogeo.fr/geocontrib/geocontrib-frontend
- Redmine 11085: Verify the format of uploaded images
- Redmine 11280: Added Attachement view in admin
- Redmine 11338: Handle features removal with Celery Beats

### Settings change

- add 'django\_celery\_beat' to INSTALLED\_APPS
- new MAGIC\_IS\_AVAILABLE (default: False) parameter to disable image file format.

### Docker settings change

- new MAGIC\_IS\_AVAILABLE (default: True) parameter to disable image file format.

### Extra operations:

- Database migration needed:

    python manage.py migrate

- To handle Celery Beat task management, load the following fixture:
    
    python manage.py loaddata geocontrib/data/geocontrib_beat.json

    You can now disable crons for running management tasks



## [1.3.6] - 2021-09-09

### Fixed

- Redmine 11613 : Docker CAS connection retrieves email

## [1.3.5] - 2021-08-11

### Changed

- Redmine 11377: Docker configuration can handle user management by a CAS server 

## [1.3.4] - 2021-08-04

### Fixed

- Redmine 9634: Prevent user to select negative valides in "Délai avant archivage" and "Délai avant suppression"
- Redmine 9803: Display feature status "En attente de publication" for admins and moderators
- Redmine 10106: Improve error message when trying to create an feature link without destination feature
- Redmine 10342: Prevents the name of field (of a feature type) to start by a number
- Redmine 10348: Feature links, fix print two links printed per link.
- Redmine 10667: Prevent user to add spaces before/after a choice in field of type list in the feature type definition
- Redmine 11066: The basemaps requests now work when creating a feature.
- Redmine 11067: Limit the zoom factor when the user have searched an addresse
- Redmine 11080: Notify the user when the base maps of a project where recorded correctly
- Redmine 11119: Fix duplicates research when importing json features
- Redmine 11164: Fix feature list in django admin

## [1.3.3] - 2021-05-06

### Fixed
- Redmine 10338: can create a feature type that has no list of values custom field and colors associated to it
- Redmine 10472: moderators are notified on pending features
- Redmine 10683: send valid links in emails
- Redmine 10571: in the search map, layers can be moved if a layer is queryable
- Redmine 10570: in the search map, can query a layer if a URL prefix is in use
- Redmine 10709: improved the mail sent to the moderators
- Redmine 10344: in the search map, old users can see the dropdown to select the layer to query
- Redmine 10683: links in the email notifications now work
- Security issues with Pillow and DRF

## [1.3.2] - 2021-02-23

### Changed
- Redmine 10053: can change color of a feature against its custom field value
- Redmine 10054 + 10266: can query properties of basemaps
- Added a scale on the maps

### Fixed
- Renamed Collab to Geocontrib in some mails
- Redmine 10574: custom characteritics' colors are now displayed

## [1.3.0 - 1.3.1] - 2021-02-23
Never released

## [1.2.3] - 2021-02-11

### Fixed
- Redmine 10209: fixed basemaps can't be saved
- Redmine 10228: added project menu on feature details
- Redmine 9962: highlight django errors

## [1.2.2] - 2021-02-11

Never released

## [1.2.1] - 2021-02-04

### Changed
- Redmine 9754 Docker can overide login URL

### Fixed
- Docker, give default values for email configuration
- Redmine 9834: use LDAP pagination
- Redmine 9839: improve feature import time
- Redmine 9846: FeatureLink cleanup
- Redmine 9848: fix admin FeatureLink filters
- Redmine 9905: can't give an empty basemap title
- Redmine 9926: fix impossible to create 2 features
- Redmine 9929: fix maps icons missing
- Redmine 9985: fix PostgreSQL view creation of a feature when adding/removing custom fields
- Redmine 9986: fix PostgreSQL view creation when no status selected
- Redmine 10083: fix a empty feature link removes the geometry of a feature on save
- Redmine 10105: fix project types don't copy feature types
- Redmine 10142: improve performance when a feature type has many features


## [1.2.0] - 2020-12-17

This evolution needs a migration (manage.py migrate)

### Changed
- Redmine 9704: allows the management of feature links in Django admin
- Redmine 8551: can import features files with extention "geojson" in addition to "json"
- Redmine 9330: a feature type can be duplicated
- Redmine 9329: can turn a project into a project template and instantiate a project from a project model
- Redmine 9544: addition of Sortable JS library
- Redmine 9507: added help on authorized characters
- Redmine 9331: imports with identical geometry are considered to be duplicates
- Django admin improvements
  - Projects list ordered by title
  - FeatureType list ordered by project, title
  - FeatureType list grouped by project
  - Users list ordered by username, last_name, first_name
  - FeatureType geom editable on create (read-only on update)
  - CustomField list ordered by feature_type, label
  - Project creator required (fixing 500 on edit)
  - Added help on authorized characters when user create a view PostgreSQL

### Fixed
- Docker, prevent creating files not readable by nginx
- Redmine 9706: The modification of the basemap form are recorded
- Redmine 9654: Creating a basemap without title doesn't crash
- Redmine 9623: A connected user doesn't see achived features if he is not allowed
- Redmine 9745: Geolocalised images are visible
- Redmine 9619: Fix bug for project creation from Django
- Redmine 9490: Fix bug when a custom field is duplicated
- Redmine 9527: Show "0" instead of « None » in the project settings
- Redmine 9526: Fix bug for view creation from Django
- Redmine 9498: Display the login if the user does not have a first and last name
- Redmine 9402: Return to the project page after modifying the project
- Redmine 9401: Error message if the archiving time is greater than the deletion time

## [1.1.3] - 2020-11-13

### Changed
- Docker image can handle forms with 10000 parameters (or more via the `DATA_UPLOAD_MAX_NUMBER_FIELDS` environement variable).
  This allows to handle more than 500 users in the project

## [1.1.2] - 2020-10-30

### Fixed
- The custom basemaps appears correctly in the list of features

## [1.1.1] - 2020-10-29

### Changed
- Increases thickness of segments of features and reduces transparency of dotted features

### Fixed
- The creator is correctly displayed in the features and the feature types
- In the basemaps form, the display of a very long layer name is now responsive
- A browser title (tab) is now displayed for all pages
- Projects with limited access are no longer accessible to everyone
- The features are now filtered when search on the map
- The search in the list of features now stays in the same page
- The Georchestra plugin now keeps user rights defined in GeoContrib
- Draft features are now hidden on the section "Last features"
- Empty comments are now blocked

## [1.1.0] - 2020-08-28

### Changed
- Increases thickness of segments borders in the basemap project management form

### Fixed
- Updates addok geocoder provider url in leaflet-control-geocoder to fix a mixed content error on client side
- flatpages.json does not reload if flatpages records exist in database
- Fixes incoherent ending h3 tags in flatpages.json

## [1.1.0-rc1] - 2020-08-19
### Added
- GeOrchestra plugin automatically associates role to users when the user database is synchronised (see
[geOrchestra plugin](plugin_georchestra/README.md))
- Adds a function to search for places and addresses in the interactive maps. This new feature comes with new settings:
`GEOCODER_PROVIDERS` and `SELECTED_GEOCODER`
- Adds a button to search for feature creation in a feature detail page
- Adds a function in the Django admin page of the feature type for creating a SQL view
- Adds a `FAVICON_PATH` setting. Default favicon is the Neogeo Technologies logo

### Changed
- Enables edition of a feature type if there is no feature associated with it yet
- Sorts users list by last_name, first_name and then username
- Changes the label of the feature type field `title` in the front-end form (Titre -> Nom)
- Changes the data model for basemaps: one basemap may contain several layers. Layers are declared by GéoContrib
admin users. Basemaps are created by project admin users by selecting layers, ordering them and setting the opacity
of each of them. End users may switch from one basemap to another in the interactive maps. One user can change
the order of the layers and their opacity in the interactive maps. These personnal adjustments are stored in the
web browser of the user (local storage) and do not alter the basemaps as seen by other users.
- Changes default value for `LOGO_PATH` setting: Neogeo Technologie logo. This new image is located in the media
directory.
- Changes all visible names in front-end and docs from `Geocontrib` to `GéoContrib`
- Sets the leaflet background container to white
- Increases the width of themap in feature_list.html

### Fixed
- Fixes tests on exif tag extraction
- Fixes serialisation of field archieved_on of features
- Uses https instead of http on link to sortable.js
- Fixes typos: basemaps management error message
- Fixes visibility of draft features

### Security
- Upgrades Pillow from 6.2.2 to 7.2.0 (Python module used for exif tags extraction)
