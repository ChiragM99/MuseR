# Generated by Django 2.2.9 on 2020-05-21 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='album',
            old_name='name',
            new_name='album_name',
        ),
        migrations.RenameField(
            model_name='album',
            old_name='spotify_id',
            new_name='album_spotify_id',
        ),
        migrations.RenameField(
            model_name='artist',
            old_name='name',
            new_name='artist_name',
        ),
        migrations.RenameField(
            model_name='artist',
            old_name='spotify_id',
            new_name='artist_spotify_id',
        ),
        migrations.RenameField(
            model_name='track',
            old_name='name',
            new_name='track_name',
        ),
        migrations.RenameField(
            model_name='track',
            old_name='spotify_id',
            new_name='track_spotify_id',
        ),
    ]