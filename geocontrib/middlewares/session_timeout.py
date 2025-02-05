from django.utils.timezone import now
from django.conf import settings

class SessionIdleTimeoutMiddleware:
    """
    Middleware pour gérer l'expiration automatique des sessions Django
    après une période d'inactivité définie dans `SESSION_IDLE_TIMEOUT`.

    Fonctionnement :
    - À chaque requête, si l'utilisateur est authentifié, on vérifie son temps d'inactivité.
    - Si l'utilisateur est inactif depuis plus de `SESSION_IDLE_TIMEOUT`, la session est supprimée.
    - Certaines requêtes (ex: `/user_info`) sont exclues de la mise à jour de l'activité
      mais peuvent toujours détecter une session expirée.
    """

    def __init__(self, get_response):
        """
        Initialisation du middleware.

        :param get_response: Fonction qui permet d’obtenir la réponse après le traitement de la requête.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Vérifie l'inactivité de l'utilisateur à chaque requête et supprime
        la session s'il a dépassé la limite `SESSION_IDLE_TIMEOUT`.

        - Ne met pas à jour l'activité pour certaines requêtes (`excluded_paths`)
          afin d'éviter que les appels automatiques (ex: SSO) ne prolongent la session.
        """
        # Liste des endpoints à exclure du suivi d'activité
        excluded_paths = ['/user_info']

        if request.user.is_authenticated:
            # Récupérer le timestamp du dernier moment d'activité enregistré en session
            last_activity = request.session.get('last_activity')

            if last_activity:
                # Calculer le temps écoulé depuis la dernière activité
                idle_time = now().timestamp() - last_activity

                # Si l'inactivité dépasse la durée autorisée, on supprime la session
                if idle_time > settings.SESSION_IDLE_TIMEOUT:
                    request.session.flush()  # Détruit la session et force la déconnexion
                    return self.get_response(request)

            # Mettre à jour le dernier moment d'activité uniquement si ce n'est pas une requête exclue
            if request.path not in excluded_paths:
                request.session['last_activity'] = now().timestamp()

        return self.get_response(request)
