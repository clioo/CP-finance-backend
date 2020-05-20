# Generated by Django 3.0.6 on 2020-05-19 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_income'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='periodicity',
            field=models.CharField(blank=True, choices=[('m', 'Monthly'), ('a', 'Annual')], max_length=255),
        ),
    ]
