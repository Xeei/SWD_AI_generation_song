from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_playlist_creator_song_creator_playlistsong_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='audio_file_url',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='song',
            name='share_url',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
