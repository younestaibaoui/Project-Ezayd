# Generated by Django 5.2.2 on 2025-06-06 06:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ezayd', '0002_remove_immobilier_prix_and_more'),
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationdemandeenchaire',
            name='enchaire',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='Ezayd.enchaire'),
        ),
    ]
