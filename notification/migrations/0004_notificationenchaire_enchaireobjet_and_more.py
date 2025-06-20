# Generated by Django 5.2.2 on 2025-06-09 01:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ezayd', '0009_alter_participationenchaire_date_participation'),
        ('notification', '0003_alter_notificationdemandeenchaire_enchaire_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationenchaire',
            name='enchaireObjet',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='Ezayd.enchaireobjet'),
        ),
        migrations.AlterField(
            model_name='notificationenchaire',
            name='enchaire',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='Ezayd.enchaire'),
        ),
    ]
