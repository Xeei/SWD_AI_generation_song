import uuid

from django.db import models

from .Choices import GenerationStatus, MoodTone, VoiceType


class Song(models.Model):
	song_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	title = models.CharField(max_length=200)
	occasion = models.CharField(max_length=50)
	generation_status = models.IntegerField(choices=GenerationStatus.choices, default=GenerationStatus.GENERATING)
	mood_tone = models.IntegerField(choices=MoodTone.choices)
	voice_type = models.IntegerField(choices=VoiceType.choices)
	duration = models.IntegerField()
	audio_file_url = models.CharField(max_length=500, blank=True, default="")
	share_url = models.CharField(max_length=500, blank=True, default="")
	time_stamp = models.DateTimeField(auto_now_add=True)
	is_favorite = models.BooleanField(default=False)
	suno_task_id = models.CharField(max_length=200, blank=True, default="")

	creator = models.ForeignKey('Creator', on_delete=models.SET_NULL, null=True, blank=True, related_name='songs')
