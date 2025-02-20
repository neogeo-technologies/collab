![alt text](geocontrib/static/geocontrib/img/logo-geocontrib.png?raw=true)

GéoContrib est un outil libre de signalement contributif et collaboratif. Une version de démonstration est accessible sur https://geocontrib.demo.neogeo.fr/.

Depuis la version 2.0.0, l'interface web est dans une dépôt séparé : https://git.neogeo.fr/geocontrib/geocontrib-frontend

## Documentation

L'intégralité de la documentation de GéoContrib est accessible ici : https://www.onegeosuite.fr/docs/module-geocontrib/intro
Celle-ci n'est plus disponible dans le répertoire /docs du dépôt à partir de la version 5.4.1.

## Version stable

La version stable de GéoContrib est une version qui a été testée et validée par la communauté GéoContrib. Nous recommandons l'installation de cette version dans le cas d'une utilisation optimale et sans instabilité. 

La version actuellement stabilisée est la version **6.4.3**.

## Installation

### Prérequis

* Python 3.12 (minimum 3.8)
* Instance de PostgreSQL/PostGIS avec une base de données dédiée à l'application 
(cf. paramètre DATABASES du fichier settings.py)


### Création du projet Django et clone du repo

#### 1. Installation des dépendances système

```shell
# Ces dépendances sont requises pour les fonctionnalités de base du projet, telles que l'interaction avec une base de données PostgreSQL, la manipulation de fichiers géospatiaux, etc.
apt-get install -y libproj-dev gdal-bin ldap-utils libpq-dev libmagic1

# Ces dépendances sont nécessaires pour compiler et utiliser la bibliothèque Pillow, qui est utilisée pour le traitement d'images (depuis passage à python 3.12).
apt-get install -y libjpeg-dev zlib1g-dev libpng-dev
```

#### 2. Création et activation d'un environnement virtuel Python
```shell
# Création d'un environnement virtuel
python3 -m venv geocontrib_venv/
# Activation de cet environnement
source geocontrib_venv/bin/activate
```

#### 3. Clonage du projet - récupération des sources  
```shell
# Actuellement, la branche par défaut du projet est develop. Ce sera celle qui sera active par défaut immédiatement après le clonage.
git clone https://git.neogeo.fr/geocontrib/geocontrib-django.git
# Se déplacer dans le répertoire cloné
cd geocontrib-django
```

#### 4. Installer les dépendances Python
```shell
pip install -r requirements.txt
```

#### 5. Création d'un projet Django
```shell
django-admin startproject config .
```

### Installation de l'interface Web en VueJS

L'interface Web intégrée à Django n'est plus maintenue depuis la 2.0, et a été retirée dans la 2.3

Il faut utiliser cette interface à la place: https://git.neogeo.fr/geocontrib/geocontrib-frontend

### Édition des fichiers settings.py et url.py

Copier le contenu du fichier config_sample/settings.py dans config/settings.py.

Éditer les paramètres classiques de Django dans config/settings.py :
* SECRET_KEY https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key
* DEBUG https://docs.djangoproject.com/en/2.2/ref/settings/#debug
* DATABASES https://docs.djangoproject.com/en/2.2/ref/settings/#databases
* TIME_ZONE https://docs.djangoproject.com/en/2.2/ref/settings/#std%3Asetting-TIME_ZONE
* STATIC_ROOT https://docs.djangoproject.com/en/2.2/ref/settings/#static-root
* MEDIA_ROOT https://docs.djangoproject.com/en/2.2/ref/settings/#media-root
* LOGGING https://docs.djangoproject.com/en/2.2/ref/settings/#logging
* EMAIL_HOST https://docs.djangoproject.com/en/2.2/ref/settings/#email-host
* EMAIL_PORT https://docs.djangoproject.com/en/2.2/ref/settings/#email-port
* EMAIL_USE_TLS https://docs.djangoproject.com/en/2.2/ref/settings/#email-use-tls
* EMAIL_HOST_USER https://docs.djangoproject.com/en/2.2/ref/settings/#std%3Asetting-EMAIL_HOST_USER
* EMAIL_HOST_PASSWORD https://docs.djangoproject.com/en/2.2/ref/settings/#email-host-password
* DEFAULT_FROM_EMAIL https://docs.djangoproject.com/en/2.2/ref/settings/#default-from-email
* DATA_UPLOAD_MAX_NUMBER_FIELDS https://docs.djangoproject.com/fr/2.2/ref/settings/#data-upload-max-number-fields
* LOGIN_URL https://docs.djangoproject.com/fr/3.1/ref/settings/#login-url

Éditer les paramètres spécifiques à l'outil dans config/settings.py :
* BASE_URL : URL du site, par exemple "https://geocontrib.deme.neogeo.fr" ;
* DEFAULT_SENDING_FREQUENCY : fréquence d'envoi des notifications par email (never/instantly/daily/weekly) ;
* APPLICATION_NAME : nom de l'application telle qu'elle apparaît dans l'IHM ;
* APPLICATION_ABSTRACT : description de l'application en langage naturel ;
* IMAGE_FORMAT : formats autorisés des fichiers téléversés dans l'application ;
* FILE_MAX_SIZE : taille maximale des fichiers téléversés dans l'application ;
* DEFAULT_BASE_MAP : configuration du fond de carte par défaut ;
* PROJECT_COPY_RELATED : configuration des modèles de projets ;
* MAGIC\_IS\_AVAILABLE (default: False) active la vérification des images téléversées ;
* LOGO_PATH : chemin vers le logo affiché en page d'accueil ;
* FAVICON_PATH : chemin vers la favicon affichée dans l'onglet du navigateur ;
* LOGOUT_HIDDEN : -> permet de cacher le bouton de déconnexion dans le backend Django (utile dans le cadre du SSO)
* HIDE_USER_CREATION_BUTTON : désactive le bouton d'ajout d'un utilisateur (utile dans le cadre du SSO)
* DISABLE_LOGIN_BUTTON : désactive le bouton de connexion (utile dans le cadre du SSO)
* LOG_URL : URL de connexion externe (utile dans le cadre du SSO)
* IDGO_URL = URL pour récupérer le catalogue DataSud ;
* MAPSERVER_URL = URL pour récupérer le geojson d'une ressource du catalogue ;
* IDGO_VERIFY_CERTIFICATE = permet de se connecter à datasud sans certificat, False en dév ;
* IDGO_LOGIN = login pour accéder au catalogue idgo depuis geocontrib ;
* IDGO_PASSWORD = mot de passe pour accéder au catalogue idgo depuis geocontrib ;
* SSO_OGS_SESSION_URL = url api OGS pour vérifier l'activation de la session utilisateur (si défini active la connexion par OGS) ;
* AUTOMATIC_VIEW_CREATION_MODE = mode de création des vues SQL créées automatiquement, soit 'Projet' soit 'Type'(valeur par défaut) ;
* AUTOMATIC_VIEW_SCHEMA_NAME = nom du schema où sont créées automatiquement les vues SQL (par défaut 'data') ;


Copier le contenu du fichier config_sample/urls.py dans config/urls.py

### Création des tables et ajout de données initiales dans la base de données

```shell
python manage.py migrate
python manage.py loaddata geocontrib/data/perm.json
python manage.py loaddata geocontrib/data/flatpages.json
python manage.py loaddata geocontrib/data/geocontrib_beat.json
python manage.py loaddata geocontrib/data/notificationmodel.json
```

Ne faites pas attention aux messages d'avertissement suivants :
```
Sites not migrated yet. Please make sure you have Sites setup on Django Admin
```

### Dépot des images par défaut

Copier l'image par défaut et le logo de l'application dans le répertoire défini par le paramètre MEDIA_ROOT 
du fichier settings.py.

Par exemple, copier les images fournies dans les sources de l'application :
```shell
mkdir media
cp geocontrib/static/geocontrib/img/default.png media/
cp geocontrib/static/geocontrib/img/logo.png media/
cp geocontrib/static/geocontrib/img/logo-neogeo*.png media/
```

### Création d'un superutilisateur

Lancer la commande Django de création d'un super utilisateur et suivre les instructions :
```shell
python manage.py createsuperuser
```

### Paramétrage du domaine et du nom du site

Ces données sont à définir depuis l'admin Django dans la section Site et
permettent notamment d'afficher les url dans les gabarit d'e-mail.
Pour cela, lancer l'application Django :
```shell
python manage.py runserver
```

Se rendre dans l'interface d'administration Django et éditer le premier enregistrement des entités 
"Sites" (cf. yoururl.net/admin/sites/).

## Configuration des tâches périodiques

Deux types de tâches requièrent d'invoquer une commande régulièrement (depuis celery-beat ou depuis un cron)

### Tâches périodiques depuis celery

Copier le contenu du fichier config_sample/celery.py dans config/celery.py.
```shell
cp config_sample/celery.py config/celery.py
```
Pour une installation en local, si on a besoin de faire des imports de signalements par exemple, il faut ouvrir un nouveau terminal, activer l'environnement virtuel et lancer la commande suvante.

Lancer le worker celery:

    celery -A config worker

Lancer le générateur d'évenements:

    celery -A config beat

Dans `/admin/django_celery_beat/periodictask`, saisissez des tâches avec leur periodicité.

### Tâches périodiques depuis un cron

L'envoi de mails de notifications, vous pouvez l'appeler toutes les minutes ou tous les jours selon vos préférences d'envoi

- Pour la notification groupée
```shell
python manage.py notify_subscribers
```
- Pour la notification de publication de documents clés
```shell
python manage.py notify_subscribers_key_documents
```

L'archivage et la suppression des signalements, à invoquer une fois par jour
```shell
python manage.py data_cleansing
```

## Déploiement dans un environnement geOrchestra

Reportez-vous au README.md présent dans le répertoire `plugin_georchestra`.


## Sauvegarde des données

```shell
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > dump.json
```

## Génération du graphique du modèle

Après avoir installé graphiz et django-extensions

```shell
./manage.py graph_models --pygraphviz geocontrib --output docs/model.png
```

Le graphique est disponible ici [docs/model.png](docs/model.png)

<br>

## Exécuter les tests unitaires

Pour garantir la stabilité et la qualité de l'application, vous pouvez exécuter les tests unitaires avec les commandes suivantes.

### Prérequis :

- Lors du développement en local, pour garantir que les tests s'exécutent de manière cohérente avec l'environnement de déploiement et la configuration CI, assurez-vous de définir la variable d'environnement URL_PREFIX='geocontrib/'.

- Avant d'exécuter les tests unitaires, assurez-vous d'installer les dépendances de développement en plus des dépendances principales. Cela inclut `pytest` et d'autres outils nécessaires pour exécuter les tests et effectuer des vérifications de code.
```shell
pip install -r requirements-dev.txt
```

- Les tests d'import nécessitent un worker Celery spécifique à l'environnement de test. Assurez-vous qu'aucun worker Celery n'est actif sur votre machine avant de lancer ces tests.


### Exécution des tests

- Pour lancer tous les tests du projet, utilisez simplement :
```shell
pytest
```
- Si vous souhaitez exécuter les tests d'une application ou d'un fichier spécifique, utilisez :
```shell
pytest path/to/test_directory_or_file.py
```
- Pour exécuter un test particulier dans un fichier spécifique :
```shell
pytest path/to/test_file.py::nom_du_test
```
<br>

## Documentation de l'API

La documentation de notre API est conçue pour fournir une référence complète et claire des différents endpoints disponibles. Elle permet aux développeurs d'explorer les fonctionnalités offertes par l'API, de tester des requêtes, et de comprendre les formats de réponse.

### Accès à la documentation

La documentation de l'API est disponible via une interface Swagger à l'adresse suivante : `/api/swagger/`. Cette interface interactive permet de :

- **Explorer les endpoints** : Une navigation claire pour parcourir tous les endpoints disponibles, classés par catégorie.
- **Tester des requêtes** : Un outil intégré pour exécuter des requêtes en temps réel et visualiser les réponses directement dans le navigateur.
- **Consulter les schémas de réponse** : Des schémas JSON détaillés accompagnent chaque endpoint pour clarifier les formats de réponse attendus.
- **Voir les exemples d'utilisation** : Chaque endpoint est documenté avec des exemples de requêtes et de réponses pour aider à comprendre comment l'utiliser efficacement.

### Structure de la documentation

La documentation est organisée de manière à être à la fois exhaustive et facile à naviguer. Chaque section couvre :

- **Les paramètres de requête** : Description des paramètres acceptés par chaque endpoint, avec leur type et leur format.
- **Les réponses possibles** : Détails des différents codes de réponse HTTP pouvant être retournés, ainsi que les formats de données associés.
- **Les exemples** : Illustrations concrètes des requêtes et des réponses, pour faciliter l'intégration dans vos applications.

### Formulaires interactifs

Pour chaque endpoint, la documentation propose des formulaires interactifs permettant de tester les différents paramètres directement depuis l'interface. Ces formulaires aident les développeurs à valider leurs requêtes avant de les intégrer dans leur code.

- **Essayez** : Utilisez la fonction "Try it out" dans Swagger pour tester les endpoints directement.
- **Authentification** : Des identifiants ou tokens sont nécessaires si vous souhaitez interagir avec les endpoints sécurisés.


<br>

## Système de notifications

### Vue d'ensemble
Notre système de notifications est conçu pour informer les utilisateurs des événements significatifs au sein de leurs projets, tels que la création, la mise à jour et la suppression de signalements, de commentaires et de pièces jointes. Ce système est configurable, permettant d'adapter les notifications aux besoins spécifiques des projets et aux préférences des utilisateurs.
- **Caractéristiques configurables commune à toutes les notifications** :
  - **Modèles Personnalisables** : Le contenu des notifications peut être personnalisé à travers des modèles éditables stockés dans la base de données, permettant un ajustement dynamique du contenu dans l'interface d'administration.

### Types de Notifications

#### - Notifications groupées
- **Objectif** : Informer tous les abonnés des différents projets sur les événements variés tels que les mises à jour, les suppressions et les créations de signalement, les évolutions du projet, ainsi que la publication de commentaires ou de pièces jointes.
- **Fonctionnement** : Les notifications sont regroupées grâce aux instances `StackedEvent`, crées par un Signal
- **Filtre** : Uniqement les événements pour les signalements dont le statut n'est pas à brouillon au moment de la génération de la notification sont envoyés.
- **Déclencheur** : Les notifications sont regroupées grâce aux instances `StackedEvent` et envoyées périodiquement selon la configuration de la tâche périodique associée.
- **Caractéristiques Configurables** :
  - **Niveau d'envoi des notifications** : Les administrateurs peuvent configurer l'envoi des notifications groupées à un niveau globale ou par projet. Ceci est géré par le champ `per_project` dans le modèle `NotificationModel`.
  - **Désactivation des notifications** : Vous pouvez désactiver les notifications pour un type de signalement via l'interface d'administration ou la configuration d'affichage de signalement dans l'application frontend. L'envoi des notifications de publication de documents clés ne sont pas impactés par ce pramétrage.

#### - Notifications de publications de documents clés
- **Objectif** : Informer tous les abonnés des différents projets sur les publications importantes de documents au sein de leurs projets.
- **Fonctionnement** : Les notifications sont regroupées grâce aux instances `StackedEvent` spécifiques, en utilisant la propriété `only_key_document`. Les piles d'événements sont crées par un Signal, lors de la publication d'une pièce jointe avec le paramètre `is_key_document`.
- **Filtre** : Uniqement les événements pour les signalements dont le statut n'est pas à brouillon au moment de la génération de la notification sont envoyés.
- **Déclencheur** : Les notifications sont envoyées périodiquement selon la configuration de la tâche périodique associée.
- **Caractéristiques Configurables** :
  - **Activation des Notifications** : Les administrateurs peuvent activer ou désactiver les notifications pour les documents clés au niveau d'un type de signalement. Ceci est géré par le champ booléen `enable_key_doc_notif` dans le modèle `FeatureType`.

#### - Notifications de créations de signalements en attente de modération
- **Objectif** : Informer les modérateurs des signalements nécessitant une modération dans les projets configurés avec le paramètre de modération activé.
- **Fonctionnement** : L'envoi de la notification est faite au niveau du modèle `Event` par la méthode `ping_users`
- **Déclencheur** : Se produit lorsqu'un signalement est créé ou modifié par un contributeur, ce qui lui attribue automatiquement le statut "En attente de publication".

#### - Notifications de publications de signalements après modération
- **Objectif** : Informer le créateur d'un signalement lorsque sa soumission a été approuvée et publiée par un modérateur.
- **Fonctionnement** : L'envoi de la notification est faite au niveau du modèle `Event` par la méthode `ping_users`
- **Déclencheur** : Se produit lorsqu'un signalement passe du statut "En attente de publication" à "Publié'.

<br>
<br>

DEVELOPPEMENT
=============

Général
-------

Geocontrib est un projet initié par NeoGeo.
Le code source de l'application est maintenu sur la plateforme https://git.neogeo.fr/geocontrib/.

les Mainteneurs actuels :
 - Timothée POUSSARD (Neogeo)
 - Camille BLANCHON (Neogeo)
 - Matthieu ETOURNEAU (Neogeo)
 - Angela Escobar (Neogeo)

La documentation de l'application 
*********************************

https://www.onegeosuite.fr/docs/team_geocontrib

Pratiques et règles de developpement
------------------------------------

Afin de partager des règles communes de développement et faciliter l'intégration de 
nouveau code, veuillez lire les recommandations et bonnes pratiques recommandées pour contribuer
au projet GeoContrib.

Git
***

 - Faire une demande de contribution en envoyant un mail à metourneau@neogeo.fr
 - Un compte vous sera créé sur notre plateforme gitlab
 - Faire un fork de l'application
 - Faire des merge requests vers la branch ``develop``
 - Faire des ``git pull`` avant chaque développement et avant chaque commit
