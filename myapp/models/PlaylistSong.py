from django.db import models


class PlaylistSong(models.Model):
	playlist = models.ForeignKey(
		'PlayList',
		on_delete=models.CASCADE,
		related_name='playlist_songs'
	)
	song = models.ForeignKey(
		'Song',
		on_delete=models.CASCADE,
		related_name='playlist_songs'
	)
	order = models.IntegerField(default=0)
	added_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['order']
		unique_together = ('playlist', 'song')
