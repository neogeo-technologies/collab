# Generated by Django 2.2.16 on 2021-11-04 10:17

from django.db import migrations, models


def reset_user_permission_ranks(apps, schema_editor, elidible=True):
    UserLevelPermission = apps.get_model('geocontrib.UserLevelPermission')
    UserLevelPermission.objects.update_or_create(
        user_type_id='admin', defaults={'rank': 5}
    )
    UserLevelPermission.objects.update_or_create(
        user_type_id='moderator', defaults={'rank': 4}
    )
    UserLevelPermission.objects.update_or_create(
        user_type_id='super_contributor', defaults={'rank': 3}
    )
    UserLevelPermission.objects.update_or_create(
        user_type_id='contributor', defaults={'rank': 2}
    )
    UserLevelPermission.objects.update_or_create(
        user_type_id='logged_user', defaults={'rank': 1}
    )
    UserLevelPermission.objects.update_or_create(
        user_type_id='anonymous', defaults={'rank': 0}
    )


class Migration(migrations.Migration):

    dependencies = [
        ('geocontrib', '0015_auto_20211018_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlevelpermission',
            name='user_type_id',
            field=models.CharField(choices=[('anonymous', 'Utilisateur anonyme'), ('logged_user', 'Utilisateur connecté'), ('contributor', 'Contributeur'), ('super_contributor', 'Super Contributeur'), ('moderator', 'Modérateur'), ('admin', 'Administrateur projet')], max_length=100, primary_key=True, serialize=False, verbose_name='Identifiant'),
        ),
        migrations.RunPython(reset_user_permission_ranks, elidable=True),
    ]
