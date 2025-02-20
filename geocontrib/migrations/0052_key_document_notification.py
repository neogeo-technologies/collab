# Generated by Django 3.2.18 on 2024-05-28 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geocontrib', '0051_notificationmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='is_key_document',
            field=models.BooleanField(default=False, verbose_name='Document clé'),
        ),
        migrations.AddField(
            model_name='featuretype',
            name='enable_key_doc_notif',
            field=models.BooleanField(default=False, verbose_name='Activer la notification de publication de pièces jointes'),
        ),
        migrations.AddField(
            model_name='stackedevent',
            name='only_key_document',
            field=models.BooleanField(default=False, verbose_name='Document clé uniquement'),
        ),
        migrations.AlterField(
            model_name='event',
            name='object_type',
            field=models.CharField(choices=[('comment', 'Commentaire'), ('feature', 'Signalement'), ('attachment', 'Pièce jointe'), ('key_document', 'Document clé'), ('project', 'Projet')], max_length=100, verbose_name="Type de l'objet lié"),
        ),
    ]
