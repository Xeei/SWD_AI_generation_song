from django.db import models
import uuid


class GenerationStatus(models.IntegerChoices):
	GENERATING = 1, 'Generating'
	GENERATED = 2, 'Generated'
	ERROR = 3, 'Error'


class MoodTone(models.IntegerChoices):
	HAPPY = 1, 'Happy'
	SAD = 2, 'Sad'
	UPBEAT = 3, 'Upbeat'
	ROMANTIC = 4, 'Romantic'
	CHILL = 5, 'Chill'
	EPIC = 6, 'Epic'


class VoiceType(models.IntegerChoices):
	MALE_POP = 1, 'Male Pop'
	FEMALE_POP = 2, 'Female Pop'
	MALE_ROCK = 3, 'Male Rock'
	FEMALE_ROCK = 4, 'Female Rock'
	INSTRUMENTAL_ONLY = 5, 'Instrumental Only'


class Song(models.Model):
	song_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	title = models.CharField(max_length=200)
	occasion = models.CharField(max_length=50)
	generation_status = models.IntegerField(choices=GenerationStatus.choices, default=GenerationStatus.GENERATING)
	mood_tone = models.IntegerField(choices=MoodTone.choices)
	voice_type = models.IntegerField(choices=VoiceType.choices)
	lyrics_content = models.CharField(max_length=2000)
	duration = models.IntegerField()
	audio_file_url = models.CharField(max_length=50)
	share_url = models.CharField(max_length=50)
	time_stamp = models.DateTimeField(auto_now_add=True)
	is_favorite = models.BooleanField(default=False)


class PlayList(models.Model):
	playlist_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=50)
	create_at = models.DateTimeField(auto_now_add=True)


class Creator(models.Model):
	creator_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	email = models.EmailField(max_length=254, unique=True)