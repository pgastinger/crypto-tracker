# Generated by Django 4.0.7 on 2022-08-30 19:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crypto',
            name='wallet',
        ),
        migrations.AddField(
            model_name='cryptopurchases',
            name='wallet',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='crypto.wallet'),
            preserve_default=False,
        ),
    ]
