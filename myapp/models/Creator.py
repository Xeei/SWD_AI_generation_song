import uuid

from django.db import models


class Creator(models.Model):
	creator_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	email = models.EmailField(max_length=254, unique=True)
