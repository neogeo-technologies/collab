# Generated by Django 3.2.13 on 2023-01-19 16:00

from django.db import migrations

def sync_project_feature_browsing_default_sort(apps):
    Project = apps.get_model("geocontrib", "Project")
    all_projects = Project.objects.all()
    for project in all_projects:
        if project.feature_browsing_default_sort == 'created_on':
            project.feature_browsing_default_sort = '-created_on'
            project.save()

def sync_new_db(apps, schema_editor, elidible=True):
    sync_project_feature_browsing_default_sort(apps)



class Migration(migrations.Migration):

    dependencies = [
        ('geocontrib', '0034_alter_project_feature_browsing_default_sort'),
    ]

    operations = [
        migrations.RunPython(sync_new_db, elidable=True),
    ]
