# Generated by Django 5.2.1 on 2025-06-07 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ezayd', '0004_remove_demandeenchaire_approved_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demandeenchaire',
            name='state',
            field=models.CharField(choices=[('unread', 'Non lu'), ('Approuvée', 'Approuvée'), ('Rejetée', 'Rejetée')], default='unread', max_length=10),
        ),
    ]
