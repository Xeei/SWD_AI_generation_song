import uuid

from django.db import models


class PlayList(models.Model):
	playlist_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=50)
	create_at = models.DateTimeField(auto_now_add=True)

	creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='playlists')
	songs = models.ManyToManyField(
		'Song',
		through='PlaylistSong',
		related_name='playlists',
		blank=True
	)
