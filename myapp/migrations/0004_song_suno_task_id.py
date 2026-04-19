from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_song_audio_file_url_alter_song_share_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='suno_task_id',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
