from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_song_voice_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='creator',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='songs',
                to='myapp.creator',
            ),
        ),
    ]
