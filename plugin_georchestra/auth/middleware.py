# Copyright (c) 2019 Neogeo-Technologies.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import logging

from decouple import config, Csv
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.urls import resolve

User = get_user_model()
logger = logging.getLogger(__name__)

IGNORED_PATHS = config('IGNORED_PATHS', default='geocontrib:logout,', cast=Csv())
HEADER_UID = config('HEADER_UID', default='HTTP_SEC_USERNAME')


class RemoteUserMiddleware(object):

    def __init__(self, get_response):
        # Enregistre la fonction qui sera appelée pour traiter la requête après le middleware.
        self.get_response = get_response

    def path_is_ignored(self, request, admin_ignored=False):
        """Détermine si la requête courante concerne une url qui n'a pas besoin
        d'être traitée par ce middleware. Et si on traite les requêtes en direction
        du site d'admin Django
        """
        # Si l'option 'admin_ignored' est activée et que le chemin de la requête
        # commence par l'URL de l'index de l'admin, alors on ignore le traitement.
        if admin_ignored and request.path.startswith(reverse('admin:index')):
            return True
        
        # Résout le chemin de la requête pour obtenir son namespace et son nom d'URL.
        resolved = resolve(request.path)
        if len(resolved.app_names) > 0:
            # Construit un nom de namespace sous la forme "app_name:url_name".
            namespace = "{}:{}".format(resolved.app_names[0], resolved.url_name)
            # Vérifie si ce namespace est dans la liste des chemins ignorés.
            return IGNORED_PATHS.count(namespace) > 0

        # Si aucun cas de figure précédent n'est rencontré, on ignore par défaut.
        return True

    def sso_setted(self, request):
        # Vérifie si l'authentification SSO est active en se basant sur un header spécifique
        # (HTTP_SEC_PROXY), qui doit être égal à 'true' pour indiquer que le SSO est actif.
        return request.META.get('HTTP_SEC_PROXY', 'false') == 'true'

    def process_request(self, request):
        # Récupère l'identifiant de l'utilisateur à partir d'un header HTTP (HEADER_UID) envoyé par geOrchestra.
        sid_user_id = request.META.get(HEADER_UID)
        logger.warning(request.headers)
        logger.warning(request.user)
        logger.warning(request.user.is_authenticated)
        logger.warning(sid_user_id)
        logger.warning(self.sso_setted(request))

        # Cas 1 : Déconnexion lorsque l'utilisateur est authentifié dans l'application
        # mais que le SSO n'est plus actif.
        if self.sso_setted(request) and not sid_user_id and request.user.is_authenticated:
            logout(request)
            logger.warning('USER LOGGED OUT due to SSO logout')
            logger.warning(request.headers)
            return  # Fin du traitement, l'utilisateur est déconnecté.
        
        # Cas 2: Si le SSO est actif et qu'un identifiant utilisateur envoyé par geOrchestra est présent :
        if self.sso_setted(request) and sid_user_id:
            # Log pour le débogage : affiche l'identifiant de l'utilisateur récupéré.
            logger.debug('HEADER_UID: {header_uid}, VALUE: {value}'.format(
                header_uid=HEADER_UID,
                value=sid_user_id,
            ))

            try:
                # Recherche l'utilisateur correspondant à l'identifiant dans la base de données.
                proxy_user = User.objects.get(username=sid_user_id)
            except User.DoesNotExist as e:
                # Si l'utilisateur n'existe pas, log l'erreur et refuse l'accès.
                logger.debug(e)
                raise PermissionDenied()

            # Sanity Check: Si l'utilisateur connecté n'est pas celui envoyé par le proxy
            # on déconnecte l'utilisateur en cours.
            if request.user.is_authenticated and proxy_user != request.user:
                logout(request)
                logger.warning('USER LOGGED OUT')
                logger.warning(request.headers)

            # On évite de reconnecter un utilisateur déjà connecté, sinon les tokens CSRF
            # sont altérés entre la création du formulaire et son post.
            # La méthode login() est donc appelée uniquement si l'utilisateur n'est pas déjà authentifié.
            if not request.user.is_authenticated:
                backend = 'django.contrib.auth.backends.ModelBackend'
                # Connecte l'utilisateur à la session en utilisant le backend spécifié.
                login(request, proxy_user, backend=backend)
                logger.debug('USER LOGGED IN')
                logger.debug(request.headers)

    def __call__(self, request):
        # Vérifie si la requête ne doit pas être ignorée par le middleware.
        if not self.path_is_ignored(request):
            # Si elle n'est pas ignorée, traite la requête pour gérer l'authentification.
            self.process_request(request)

        # Continue le traitement de la requête avec la réponse générée par la vue ou le middleware suivant.
        response = self.get_response(request)
        return response
