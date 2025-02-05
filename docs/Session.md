# Gestion des sessions dans Django

L'application met en place un **timeout d'inactivité** afin de :
- Déconnecter automatiquement les utilisateurs **après 1 heure d'inactivité**.
- Permettre aux appels automatiques du frontend (ex. `/user_info` pour le SSO) **de ne pas prolonger la session**.
- Expirer la session sans affecter les requêtes de vérification de statut.

---

## 🛠️ Variables de configuration des sessions

### `SESSION_COOKIE_AGE`
- **Valeur** : `86400` (24h en secondes)
- **Effet** : Durée **maximale** d'une session côté serveur.
- **Impact** : Après 24h, l’utilisateur devra **se reconnecter**, même s'il est actif.

### `SESSION_EXPIRE_AT_BROWSER_CLOSE`
- **Valeur** : `True`
- **Effet** : Convertit le cookie `sessionid` en **cookie temporaire**.
- **Impact** : La session est détruite **si le navigateur est fermé** (sauf si restauré par le navigateur).

### `SESSION_SAVE_EVERY_REQUEST`
- **Valeur** : `False`
- **Effet** : Empêche Django de prolonger la session à chaque requête.
- **Impact** : La session expire strictement après **`SESSION_COOKIE_AGE`** ou **`SESSION_IDLE_TIMEOUT`**.

### `SESSION_IDLE_TIMEOUT`
- **Valeur** : `3600` (1h en secondes)
- **Effet** : Supprime la session après **1h d'inactivité**.
- **Impact** : Si aucune action pendant 1h, la session expire, obligeant l'utilisateur à se reconnecter.

---

## 🎯 Expiration de session après inactivité

Django ne propose pas de mécanisme natif pour expirer une session après inactivité.  
Les sessions sont stockées côté serveur, mais Django ne vérifie pas depuis combien de temps un utilisateur est inactif.

Un middleware Django a été ajouté pour suivre l’activité de l’utilisateur et expirer la session après un délai configurable (`SESSION_IDLE_TIMEOUT`).

## 🔧 Middleware `SessionIdleTimeoutMiddleware`
Ce middleware surveille l'activité des utilisateurs et **supprime la session** après une période d’inactivité.

**📌 Fonctionnement :**
1. À chaque requête, si l’utilisateur est **authentifié**, il récupère le dernier moment d’activité.
2. Si le temps d’inactivité dépasse **1 heure**, la session est **supprimée** et l’utilisateur est déconnecté.
3. Si l'utilisateur est actif, **on met à jour** la dernière activité.
4. **Les requêtes automatiques (`/user_info`) ne prolongent pas la session**, mais détectent si elle a expiré.

---

**📌 Configuration :**
- Durée d'inactivité configurable via une variable d’environnement :
  ```env
  SESSION_IDLE_TIMEOUT=3600  # 1h par défaut
  ```
- Ajout du middleware via la variable d’environnement :
  ```env
  SESSION_MIDDLEWARE='geocontrib.middlewares.session_timeout.SessionIdleTimeoutMiddleware'
  ```
---

## 🎯 Expiration automatique après 24h

En complément de l’expiration après inactivité, une session ne peut pas durer plus de 24h, même si l’utilisateur est actif.

### Paramètre Django utilisé : `SESSION_COOKIE_AGE`
```python
SESSION_COOKIE_AGE = 86400  # 24 heures en secondes
```
- Cette valeur ne dépend pas de l’activité utilisateur.
- Une fois 24h écoulées, la session expire automatiquement et nécessite une reconnexion.

---

## Résumé de l’implémentation
| Mécanisme | Implémentation dans le code |
|-----------|----------------------------|
| Expiration après inactivité | Middleware Django (`SESSION_IDLE_TIMEOUT`) |
| Fermeture de session à la fermeture du navigateur | Non implémenté car non fiable |
| Expiration après 24h | `SESSION_COOKIE_AGE = 86400` |
