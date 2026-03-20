import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .models import Song, PlayList, Creator


# ── Exceptions ────────────────────────────────────────────────────────────────

class NotFound(Exception):
	pass


class ValidationError(Exception):
	def __init__(self, message, fields=None):
		super().__init__(message)
		self.fields = fields or []


# ── Use Cases ─────────────────────────────────────────────────────────────────

class SongUseCase:
	def list_songs(self):
		return [self._to_dict(s) for s in Song.objects.all()]

	def get_song(self, song_id):
		try:
			return self._to_dict(Song.objects.get(pk=song_id))
		except Song.DoesNotExist:
			raise NotFound("Song not found")

	def create_song(self, data):
		required = [
			"title", "occasion", "mood_tone", "voice_type",
			"lyrics_content", "duration", "audio_file_url", "share_url",
		]
		missing = [f for f in required if data.get(f) in (None, "")]
		if missing:
			raise ValidationError("Missing required fields", fields=missing)
		try:
			song = Song.objects.create(
				title=data["title"],
				occasion=data["occasion"],
				generation_status=int(data.get("generation_status", Song._meta.get_field("generation_status").default)),
				mood_tone=int(data["mood_tone"]),
				voice_type=int(data["voice_type"]),
				lyrics_content=data["lyrics_content"],
				duration=int(data["duration"]),
				audio_file_url=data["audio_file_url"],
				share_url=data["share_url"],
				is_favorite=bool(data.get("is_favorite", False)),
			)
		except (TypeError, ValueError):
			raise ValidationError("Invalid field type")
		return self._to_dict(song)

	def update_song(self, song_id, data):
		try:
			song = Song.objects.get(pk=song_id)
		except Song.DoesNotExist:
			raise NotFound("Song not found")
		updatable = {
			"title": str, "occasion": str, "lyrics_content": str,
			"audio_file_url": str, "share_url": str,
			"generation_status": int, "mood_tone": int, "voice_type": int, "duration": int,
			"is_favorite": bool,
		}
		try:
			for field, cast in updatable.items():
				if field in data:
					setattr(song, field, cast(data[field]))
		except (TypeError, ValueError):
			raise ValidationError("Invalid field type")
		song.save()
		return self._to_dict(song)

	def delete_song(self, song_id):
		try:
			Song.objects.get(pk=song_id).delete()
		except Song.DoesNotExist:
			raise NotFound("Song not found")

	def _to_dict(self, s):
		return {
			"song_id": str(s.song_id),
			"title": s.title,
			"occasion": s.occasion,
			"generation_status": s.generation_status,
			"mood_tone": s.mood_tone,
			"voice_type": s.voice_type,
			"lyrics_content": s.lyrics_content,
			"duration": s.duration,
			"audio_file_url": s.audio_file_url,
			"share_url": s.share_url,
			"is_favorite": s.is_favorite,
			"time_stamp": s.time_stamp.isoformat(),
		}


class PlaylistUseCase:
	def list_playlists(self):
		return [self._to_dict(p) for p in PlayList.objects.all()]

	def get_playlist(self, playlist_id):
		try:
			return self._to_dict(PlayList.objects.get(pk=playlist_id))
		except PlayList.DoesNotExist:
			raise NotFound("PlayList not found")

	def create_playlist(self, data):
		if not data.get("name"):
			raise ValidationError("Missing required fields", fields=["name"])
		playlist = PlayList.objects.create(name=data["name"])
		return self._to_dict(playlist)

	def update_playlist(self, playlist_id, data):
		try:
			playlist = PlayList.objects.get(pk=playlist_id)
		except PlayList.DoesNotExist:
			raise NotFound("PlayList not found")
		if not data.get("name"):
			raise ValidationError("Missing required fields", fields=["name"])
		playlist.name = data["name"]
		playlist.save()
		return self._to_dict(playlist)

	def delete_playlist(self, playlist_id):
		try:
			PlayList.objects.get(pk=playlist_id).delete()
		except PlayList.DoesNotExist:
			raise NotFound("PlayList not found")

	def _to_dict(self, p):
		return {
			"playlist_id": str(p.playlist_id),
			"name": p.name,
			"create_at": p.create_at.isoformat(),
		}


class CreatorUseCase:
	def list_creators(self):
		return [self._to_dict(c) for c in Creator.objects.all()]

	def get_creator(self, creator_id):
		try:
			return self._to_dict(Creator.objects.get(pk=creator_id))
		except Creator.DoesNotExist:
			raise NotFound("Creator not found")

	def create_creator(self, data):
		if not data.get("email"):
			raise ValidationError("Missing required fields", fields=["email"])
		if Creator.objects.filter(email=data["email"]).exists():
			raise ValidationError("Email already exists")
		creator = Creator.objects.create(email=data["email"])
		return self._to_dict(creator)

	def update_creator(self, creator_id, data):
		try:
			creator = Creator.objects.get(pk=creator_id)
		except Creator.DoesNotExist:
			raise NotFound("Creator not found")
		if not data.get("email"):
			raise ValidationError("Missing required fields", fields=["email"])
		if Creator.objects.filter(email=data["email"]).exclude(pk=creator_id).exists():
			raise ValidationError("Email already exists")
		creator.email = data["email"]
		creator.save()
		return self._to_dict(creator)

	def delete_creator(self, creator_id):
		try:
			Creator.objects.get(pk=creator_id).delete()
		except Creator.DoesNotExist:
			raise NotFound("Creator not found")

	def _to_dict(self, c):
		return {
			"creator_id": str(c.creator_id),
			"email": c.email,
		}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_json(request):
	try:
		return json.loads(request.body) if request.body else {}, None
	except json.JSONDecodeError:
		return None, JsonResponse({"error": "Invalid JSON payload"}, status=400)


def _error_response(e):
	if isinstance(e, NotFound):
		return JsonResponse({"error": str(e)}, status=404)
	body = {"error": str(e)}
	if e.fields:
		body["fields"] = e.fields
	return JsonResponse(body, status=400)


# Song

def song_list_view(request):
	return JsonResponse({"song_list": SongUseCase().list_songs()})


@csrf_exempt
def create_song_view(request):
	if request.method != "POST":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	payload, err = _parse_json(request)
	if err:
		return err
	try:
		song = SongUseCase().create_song(payload)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"message": "Song created successfully", "song": song}, status=201)


def song_detail_view(request, song_id):
	try:
		song = SongUseCase().get_song(song_id)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"song": song})


@csrf_exempt
def update_song_view(request, song_id):
	if request.method != "PUT":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	payload, err = _parse_json(request)
	if err:
		return err
	try:
		song = SongUseCase().update_song(song_id, payload)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"message": "Song updated successfully", "song": song})


@csrf_exempt
def delete_song_view(request, song_id):
	if request.method != "DELETE":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	try:
		SongUseCase().delete_song(song_id)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"message": "Song deleted successfully"})


# PlayList

def playlist_list_view(request):
	return JsonResponse({"playlist_list": PlaylistUseCase().list_playlists()})


@csrf_exempt
def create_playlist_view(request):
	if request.method != "POST":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	payload, err = _parse_json(request)
	if err:
		return err
	try:
		playlist = PlaylistUseCase().create_playlist(payload)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"message": "PlayList created successfully", "playlist": playlist}, status=201)


def playlist_detail_view(request, playlist_id):
	try:
		playlist = PlaylistUseCase().get_playlist(playlist_id)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"playlist": playlist})


@csrf_exempt
def update_playlist_view(request, playlist_id):
	if request.method != "PUT":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	payload, err = _parse_json(request)
	if err:
		return err
	try:
		playlist = PlaylistUseCase().update_playlist(playlist_id, payload)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"message": "PlayList updated successfully", "playlist": playlist})


@csrf_exempt
def delete_playlist_view(request, playlist_id):
	if request.method != "DELETE":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	try:
		PlaylistUseCase().delete_playlist(playlist_id)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"message": "PlayList deleted successfully"})


# Creator

def creator_list_view(request):
	return JsonResponse({"creator_list": CreatorUseCase().list_creators()})


@csrf_exempt
def create_creator_view(request):
	if request.method != "POST":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	payload, err = _parse_json(request)
	if err:
		return err
	try:
		creator = CreatorUseCase().create_creator(payload)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"message": "Creator created successfully", "creator": creator}, status=201)


def creator_detail_view(request, creator_id):
	try:
		creator = CreatorUseCase().get_creator(creator_id)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"creator": creator})


@csrf_exempt
def update_creator_view(request, creator_id):
	if request.method != "PUT":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	payload, err = _parse_json(request)
	if err:
		return err
	try:
		creator = CreatorUseCase().update_creator(creator_id, payload)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"message": "Creator updated successfully", "creator": creator})


@csrf_exempt
def delete_creator_view(request, creator_id):
	if request.method != "DELETE":
		return JsonResponse({"error": "Method not allowed"}, status=405)
	try:
		CreatorUseCase().delete_creator(creator_id)
	except (NotFound, ValidationError) as e:
		return _error_response(e)
	return JsonResponse({"message": "Creator deleted successfully"})
