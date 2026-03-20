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
	MALE_POP = 1, 'Male Pop'
	FEMALE_POP = 2, 'Female Pop'
	MALE_ROCK = 3, 'Male Rock'
	FEMALE_ROCK = 4, 'Female Rock'
	INSTRUMENTAL_ONLY = 5, 'Instrumental Only'
