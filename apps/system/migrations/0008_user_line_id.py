# Generated by Django 4.2.11 on 2025-01-07 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0007_verificationcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='line_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='LINE ID'),
        ),
    ]
