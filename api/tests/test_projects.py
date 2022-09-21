import shutil
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse
from django.conf import settings
import pytest

from geocontrib.models.project import Project
from geocontrib.models.user import UserLevelPermission
from geocontrib.models.user import User
from conftest import verify_or_create_json

@pytest.fixture
def project_default_logo():
    """
    Vérifie qu'il existe un fichier media/default.png qui est utilisé comme logo des projets.
    Si il n'existe pas, il le copie depuis le dossier static
    """
    logo_path = os.path.join(settings.MEDIA_ROOT, "default.png")
    if not os.path.exists(logo_path):
        if not os.path.exists(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)
        shutil.copyfile("geocontrib/static/geocontrib/img/default.png", logo_path)


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.freeze_time('2021-08-05')
def test_projects_list(api_client):
    url = reverse('api:projects-list')
    result = api_client.get(url)

    assert result.status_code == 200
    assert result.json() == {'count': 0, 'next': None, 'previous': None, 'results': []}

    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="usertest")

    anon_perm = UserLevelPermission.objects.get(pk="anonymous")

    project = Project.objects.create(
        title="Projet 1",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    project.save()

    result = api_client.get(url)
    assert result.status_code == 200
    assert result.json() == {
        'count': 1,
        'next': None,
        'previous': None,
        'results': [{
            'title': 'Projet 1',
            'slug': '1-projet-1',
            'created_on': '05/08/2021',
            'updated_on': '05/08/2021',
            'description': None,
            'moderation': False,
            'is_project_type': False,
            'generate_share_link': False,
            'fast_edition_mode': False,
            'thumbnail': reverse('api:project-thumbnail', args=["1-projet-1"]),
            'creator': 1,
            'access_level_pub_feature': 'Utilisateur anonyme',
            'access_level_arch_feature': 'Utilisateur anonyme',
            'archive_feature': None,
            'delete_feature': None,
            'map_max_zoom_level': 22,
            'nb_features': 0,
            'nb_published_features': 0,
            'nb_comments': 0,
            'nb_published_features_comments': 0,
            'nb_contributors': 1
        }]
    }


@pytest.mark.freeze_time('2021-08-05')
@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_projects_post(api_client):

    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    User.objects.create(username="admin", password="password", is_active=True)
    user = User.objects.create(username="usertest", password="password", is_active=True)
    user.save()

    project_json = dict(
        title="Projet 2",
        access_level_pub_feature="anonymous",
        access_level_arch_feature="anonymous",
        archive_feature=1,
        delete_feature=2,
        map_max_zoom_level=20,
    )

    api_client.force_authenticate(user=user)
    url = reverse('api:projects-list')
    result = api_client.post(url, project_json, format="json")

    assert result.status_code == 201, result.content.decode()
    assert result.json() == {
        'access_level_arch_feature': "anonymous",
        'access_level_pub_feature': "anonymous",
        'archive_feature': 1,
        'creator': user.pk,
        'delete_feature': 2,
        'map_max_zoom_level': 20,
        'description': None,
        'is_project_type': False,
        'moderation': False,
        'slug': '1-projet-2',
        'title': 'Projet 2',
        'generate_share_link': False,
        'fast_edition_mode': False,
    }


@pytest.mark.freeze_time('2021-08-05')
@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_projects_thumbnail(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="usertest", password="password", is_active=True)
    user.save()
    anon_perm = UserLevelPermission.objects.get(pk="anonymous")
    project = Project.objects.create(
        title="Projet 3",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    project.save()

    api_client.force_authenticate(user=user)
    filename = 'filename.png'
    with open("api/tests/data/img/image.png", 'rb') as file:
        simple_file = SimpleUploadedFile(filename,
                                         file.read(),
                                         content_type='multipart/form-data')

    url = reverse('api:project-thumbnail', kwargs={"slug": "1-projet-3"})


    result = api_client.put(url,
                            {'file':  simple_file})
    assert result.status_code == 200, result.content.decode()
    result_json = result.json()
    thumbnail = result_json.pop('thumbnail')
    assert thumbnail == url
    assert result_json == {
        'access_level_arch_feature': 'Utilisateur anonyme',
        'access_level_pub_feature': 'Utilisateur anonyme',
        'archive_feature': None,
        'created_on': '05/08/2021',
        'creator': user.pk,
        'delete_feature': None,
        'map_max_zoom_level': 22,
        'description': None,
        'is_project_type': False,
        'generate_share_link': False,
        'fast_edition_mode': False,
        'moderation': False,
        'nb_comments': 0,
        'nb_contributors': 1,
        'nb_features': 0,
        'nb_published_features': 0,
        'nb_published_features_comments': 0,
        'slug': '1-projet-3',
        'title': 'Projet 3',
        'updated_on': '05/08/2021',
    }

    # ensure can't POST
    result = api_client.post(url,
                            {'file':  simple_file})
    assert result.status_code == 405, result.content.decode()

    # ensure can read
    result = api_client.get(url)
    assert result.status_code == 200
    assert result.get('Content-Type') == 'image/png'
    with open("api/tests/data/img/image.png", 'rb') as file:
        # On ne compare que les 512 premiers octest du fichiers
        # (ça suffit pour voir que c'est un PNG)
        assert next(result.streaming_content)[:512] == file.read()[:512]


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
@pytest.mark.usefixtures('project_default_logo')
def test_project_duplicate(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    data = {
        'access_level_arch_feature': 'moderator',
        'access_level_pub_feature': 'anonymous',
        'title': "AZE 2"
    }

    # anon call fails
    url = reverse('api:project-duplicate', args=['1-aze'])
    with pytest.raises(ValueError):
        result = api_client.post(url, data)

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    # Ensure no parameters Fails
    result = api_client.post(url)
    assert result.status_code == 400
    assert result.json() == {
        'access_level_arch_feature': ['Ce champ est obligatoire.'],
        'access_level_pub_feature': ['Ce champ est obligatoire.'],
        'title': ['Ce champ est obligatoire.'],
    }

    # ensure it works
    result = api_client.post(url, data, format='json')
    assert result.status_code == 201
    verify_or_create_json('api/tests/data/test_feature_duplicate_create.json', result.json())

    # non existing project fails
    data['title'] = "AZE 3"
    url = reverse('api:project-duplicate', args=['2-aze'])
    result = api_client.post(url, data, format='json')
    assert result.status_code == 404


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_project_authorization(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    data = [
        {
            'level': {
                'codename': 'admin'
            },
            'user': {
                'id': 1
            }
        }
    ]
    url = reverse('api:project-authorization', args=['1-aze'])

    # anon get call success
    result = api_client.get(url)
    assert result.status_code == 200
    assert result.content.decode() == '[]'

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    # admin get call success
    result = api_client.get(url)
    assert result.status_code == 200
    assert result.content.decode() == '[]'

    # Ensure no parameters Fails
    result = api_client.put(url, [], format='json')
    assert result.status_code == 400
    assert result.json() == {'error': 'Au moins un administrateur est requis par projet. '}

    # ensure it works
    result = api_client.put(url, data, format='json')
    assert result.status_code == 200
    verify_or_create_json('api/tests/data/test_project_authorization_createjson', result.json())

    # admin get call with data success
    result = api_client.get(url)
    assert result.status_code == 200
    assert result.json() == [
        {
            "user":
            {
                "id":1,
                "first_name":"",
                "last_name":"",
                "username":"admin"
            },
            "level":
            {
                "display":"Administrateur projet",
                "codename":"admin"
            }
        }
    ]

    # non existing project fails
    url = reverse('api:project-authorization', args=['2-aze'])
    result = api_client.put(url, data, format='json')
    assert result.status_code == 404

    # anon put call fails
    # TODO uncomment when #14023 is fixed
    api_client.logout()
    url = reverse('api:project-authorization', args=['1-aze'])
    result = api_client.put(url, data, format='json')
    assert result.status_code == 403
    assert result.json() == {'detail': "Informations d'authentification non fournies."}
