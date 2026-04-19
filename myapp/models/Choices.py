from django.db import models


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
	MALE = 1, 'Male'
	FEMALE = 2, 'Female'
