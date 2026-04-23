import json
import os

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Song, PlayList, Creator, PlaylistSong
from django.db.models import Max
from .models.Choices import GenerationStatus, MoodTone
from .strategies import get_strategy

CALLBACK_BASE_URL = os.environ.get("CALLBACK_BASE_URL", "http://localhost:8000")

_strategy = get_strategy()

MOOD_TONE_STYLE = {
    MoodTone.HAPPY: "Happy, uplifting",
    MoodTone.SAD: "Sad, melancholic",
    MoodTone.UPBEAT: "Upbeat, energetic",
    MoodTone.ROMANTIC: "Romantic, tender",
    MoodTone.CHILL: "Chill, relaxing",
    MoodTone.EPIC: "Epic, cinematic",
}


# ── Exceptions ────────────────────────────────────────────────────────────────

class NotFound(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, message, fields=None):
        super().__init__(message)
        self.fields = fields or []


# ── Use Cases ─────────────────────────────────────────────────────────────────

class SongUseCase:
    def list_songs(self, creator_id=None):
        qs = Song.objects.all()
        if creator_id:
            qs = qs.filter(creator_id=creator_id)
        return [self._to_dict(s) for s in qs]

    def get_song(self, song_id):
        try:
            return self._to_dict(Song.objects.get(pk=song_id))
        except Song.DoesNotExist:
            raise NotFound("Song not found")

    def create_song(self, data):
        required = ["title", "occasion", "mood_tone", "voice_type", "duration", "creator_id"]
        missing = [f for f in required if data.get(f) in (None, "")]
        if missing:
            raise ValidationError("Missing required fields", fields=missing)
        try:
            Creator.objects.get(pk=data["creator_id"])
        except Creator.DoesNotExist:
            raise ValidationError("Creator not found", fields=["creator_id"])
        try:
            voice_type_int = int(data["voice_type"])
            mood_tone_int = int(data["mood_tone"])
            song = Song.objects.create(
                title=data["title"],
                occasion=data["occasion"],
                generation_status=GenerationStatus.GENERATING,
                mood_tone=mood_tone_int,
                voice_type=voice_type_int,
                duration=int(data["duration"]),
                is_favorite=bool(data.get("is_favorite", False)),
                creator_id=data["creator_id"],
            )
        except (TypeError, ValueError):
            raise ValidationError("Invalid field type")

        style = MOOD_TONE_STYLE.get(mood_tone_int, "Pop")
        callback_url = f"{CALLBACK_BASE_URL}/api/songs/callback/"

        try:
            task_id = _strategy.generate(song.title, style, callback_url)
            song.suno_task_id = task_id
            song.save(update_fields=["suno_task_id"])
        except RuntimeError:
            song.generation_status = GenerationStatus.ERROR
            song.save(update_fields=["generation_status"])
            raise

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

    def regenerate_song(self, song_id, data):
        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            raise NotFound("Song not found")

        if song.generation_status != GenerationStatus.GENERATED:
            raise ValidationError("Song is not in GENERATED status")

        required = ["title", "occasion", "mood_tone", "voice_type", "duration", "creator_id"]
        missing = [f for f in required if data.get(f) in (None, "")]
        if missing:
            raise ValidationError("Missing required fields", fields=missing)
        try:
            Creator.objects.get(pk=data["creator_id"])
        except Creator.DoesNotExist:
            raise ValidationError("Creator not found", fields=["creator_id"])

        try:
            mood_tone_int = int(data["mood_tone"])
            voice_type_int = int(data["voice_type"])
            title = str(data["title"])
            occasion = str(data["occasion"])
            duration = int(data["duration"])
            creator_id = data["creator_id"]
        except (TypeError, ValueError):
            raise ValidationError("Invalid field type")

        style = MOOD_TONE_STYLE.get(mood_tone_int, "Pop")
        callback_url = f"{CALLBACK_BASE_URL}/api/songs/callback/"

        try:
            task_id = _strategy.generate(title, style, callback_url)
        except RuntimeError:
            song.generation_status = GenerationStatus.ERROR
            song.save(update_fields=["generation_status"])
            raise

        song.title = title
        song.occasion = occasion
        song.mood_tone = mood_tone_int
        song.voice_type = voice_type_int
        song.duration = duration
        song.creator_id = creator_id
        song.generation_status = GenerationStatus.GENERATING
        song.audio_file_url = ""
        song.share_url = ""
        song.suno_task_id = task_id
        song.save(update_fields=[
            "title", "occasion", "mood_tone", "voice_type", "duration", "creator_id",
            "generation_status", "audio_file_url", "share_url", "suno_task_id",
        ])
        return self._to_dict(song)

    def _to_dict(self, s):
        return {
            "song_id": str(s.song_id),
            "title": s.title,
            "occasion": s.occasion,
            "generation_status": s.generation_status,
            "mood_tone": s.mood_tone,
            "voice_type": s.voice_type,
            "duration": s.duration,
            "audio_file_url": s.audio_file_url,
            "share_url": s.share_url,
            "is_favorite": s.is_favorite,
            "time_stamp": s.time_stamp.isoformat(),
            "creator_id": str(s.creator_id) if s.creator_id else None,
        }

    def handle_suno_callback(self, payload):
        code = payload.get("code")
        inner = payload.get("data", {})
        task_id = inner.get("taskId")
        status = inner.get("status")

        try:
            song = Song.objects.get(suno_task_id=task_id)
        except Song.DoesNotExist:
            raise NotFound("Song not found for task_id")

        if code == 200 and status == "SUCCESS":
            suno_data = inner.get("response", {}).get("sunoData") or []
            if suno_data:
                first = suno_data[0]
                song.audio_file_url = first.get("audioUrl", "")
                song.share_url = first.get("sourceAudioUrl", "")
                song.duration = int(first.get("duration", 0))
            song.generation_status = GenerationStatus.GENERATED
        else:
            song.generation_status = GenerationStatus.ERROR
        song.save()


class PlaylistUseCase:
    def list_playlists(self, creator_id=None):
        qs = PlayList.objects.all()
        if creator_id:
            qs = qs.filter(creator_id=creator_id)
        return [self._to_dict(p) for p in qs]

    def get_playlist(self, playlist_id):
        try:
            return self._to_dict(PlayList.objects.get(pk=playlist_id))
        except PlayList.DoesNotExist:
            raise NotFound("PlayList not found")

    def create_playlist(self, data):
        required = ["name", "creator_id"]
        missing = [f for f in required if data.get(f) in (None, "")]
        if missing:
            raise ValidationError("Missing required fields", fields=missing)
        try:
            Creator.objects.get(pk=data["creator_id"])
        except Creator.DoesNotExist:
            raise ValidationError("Creator not found", fields=["creator_id"])
        playlist = PlayList.objects.create(name=data["name"], creator_id=data["creator_id"])
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

    def add_song(self, playlist_id, song_id):
        try:
            playlist = PlayList.objects.get(pk=playlist_id)
        except PlayList.DoesNotExist:
            raise NotFound("PlayList not found")
        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            raise NotFound("Song not found")
        max_order = playlist.playlist_songs.aggregate(m=Max('order'))['m'] or 0
        PlaylistSong.objects.get_or_create(
            playlist=playlist, song=song,
            defaults={'order': max_order + 1},
        )
        return self._to_dict(playlist)

    def remove_song(self, playlist_id, song_id):
        try:
            playlist = PlayList.objects.get(pk=playlist_id)
        except PlayList.DoesNotExist:
            raise NotFound("PlayList not found")
        PlaylistSong.objects.filter(playlist=playlist, song_id=song_id).delete()
        return self._to_dict(playlist)

    def _to_dict(self, p):
        songs = [
            {
                "song_id": str(ps.song.song_id),
                "title": ps.song.title,
                "occasion": ps.song.occasion,
                "mood_tone": ps.song.mood_tone,
                "voice_type": ps.song.voice_type,
                "duration": ps.song.duration,
                "generation_status": ps.song.generation_status,
                "audio_file_url": ps.song.audio_file_url,
                "share_url": ps.song.share_url,
                "is_favorite": ps.song.is_favorite,
                "time_stamp": ps.song.time_stamp.isoformat(),
            }
            for ps in p.playlist_songs.select_related("song").order_by("order")
        ]
        return {
            "playlist_id": str(p.playlist_id),
            "name": p.name,
            "create_at": p.create_at.isoformat(),
            "song_count": len(songs),
            "songs": songs,
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

    def sync_creator(self, email):
        if not email:
            raise ValidationError("Missing required fields", fields=["email"])
        creator, _ = Creator.objects.get_or_create(email=email)
        return self._to_dict(creator)

    def _to_dict(self, c):
        return {
            "creator_id": str(c.creator_id),
            "email": c.email,
        }


# ── Background poll ───────────────────────────────────────────────────────────

_SUNO_FAILED_STATUSES = {
    "CREATE_TASK_FAILED",
    "GENERATE_AUDIO_FAILED",
    "CALLBACK_EXCEPTION",
    "SENSITIVE_WORD_ERROR",
}


def check_generating_songs():
    songs = Song.objects.filter(
        generation_status=GenerationStatus.GENERATING,
    ).exclude(suno_task_id="")

    for song in songs:
        try:
            result = _strategy.check_task(song.suno_task_id)
            data = result.get("data", {})
            status = data.get("status")

            if status == "SUCCESS":
                suno_data = data.get("response", {}).get("sunoData") or []
                if suno_data:
                    first = suno_data[0]
                    song.audio_file_url = first.get("audioUrl", "")
                    song.share_url = first.get("sourceAudioUrl", "")
                    song.duration = int(first.get("duration", song.duration))
                song.generation_status = GenerationStatus.GENERATED
                song.save(update_fields=["audio_file_url", "share_url", "duration", "generation_status"])
            elif status in _SUNO_FAILED_STATUSES:
                song.generation_status = GenerationStatus.ERROR
                song.save(update_fields=["generation_status"])
            # PENDING / TEXT_SUCCESS / FIRST_SUCCESS → still in progress, do nothing
        except Exception:
            pass


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
    creator_id = request.GET.get("creator_id") or None
    return JsonResponse({"song_list": SongUseCase().list_songs(creator_id=creator_id)})


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
    creator_id = request.GET.get("creator_id")
    return JsonResponse({"playlist_list": PlaylistUseCase().list_playlists(creator_id=creator_id)})


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


@csrf_exempt
def playlist_song_view(request, playlist_id, song_id):
    uc = PlaylistUseCase()
    try:
        if request.method == "POST":
            playlist = uc.add_song(playlist_id, song_id)
            return JsonResponse({"message": "Song added to playlist", "playlist": playlist})
        elif request.method == "DELETE":
            playlist = uc.remove_song(playlist_id, song_id)
            return JsonResponse({"message": "Song removed from playlist", "playlist": playlist})
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
    except (NotFound, ValidationError) as e:
        return _error_response(e)


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


@csrf_exempt
def sync_creator_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    payload, err = _parse_json(request)
    if err:
        return err
    try:
        creator = CreatorUseCase().sync_creator(payload.get("email", ""))
    except (NotFound, ValidationError) as e:
        return _error_response(e)
    return JsonResponse({"creator": creator})


def mock_audio_view(_request, filename):
    if not filename.endswith('.mp3'):
        raise Http404
    path = os.path.join(
        settings.BASE_DIR, 'myapp', 'static', 'myapp', 'mock_audio', filename
    )
    if not os.path.exists(path):
        raise Http404
    return FileResponse(open(path, 'rb'), content_type='audio/mpeg')


@csrf_exempt
def enum_choices_view(request):
    from .models.Choices import MoodTone, VoiceType
    return JsonResponse({
        "mood_tones": [{"value": v, "label": l} for v, l in MoodTone.choices],
        "voice_types": [{"value": v, "label": l} for v, l in VoiceType.choices],
    })


@csrf_exempt
def generate_song_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    payload, err = _parse_json(request)
    if err:
        return err
    try:
        song = SongUseCase().create_song(payload)
    except (NotFound, ValidationError) as e:
        return _error_response(e)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=502)
    return JsonResponse({"message": "Generation in progress", "song": song}, status=202)


@csrf_exempt
def regenerate_song_view(request, song_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    payload, err = _parse_json(request)
    if err:
        return err
    try:
        song = SongUseCase().regenerate_song(song_id, payload)
    except (NotFound, ValidationError) as e:
        return _error_response(e)
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=502)
    return JsonResponse({"message": "Regeneration in progress", "song": song}, status=202)


@csrf_exempt
def suno_callback_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    payload, err = _parse_json(request)
    if err:
        return err
    try:
        SongUseCase().handle_suno_callback(payload)
    except (NotFound, ValidationError) as e:
        return _error_response(e)
    return JsonResponse({"message": "Callback handled"})