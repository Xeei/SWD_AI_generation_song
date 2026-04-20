import json
import os
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Song, PlayList, Creator, VoiceType
from .models.Choices import GenerationStatus, MoodTone

SUNO_API_TOKEN = os.environ.get("SUNO_API_TOKEN", "")
SUNO_API_BASE_URL = os.environ.get("SUNO_API_BASE_URL", "https://api.sunoapi.org")
CALLBACK_BASE_URL = os.environ.get("CALLBACK_BASE_URL", "http://localhost:8000")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

MOOD_TONE_STYLE = {
    MoodTone.HAPPY: "Happy, uplifting",
    MoodTone.SAD: "Sad, melancholic",
    MoodTone.UPBEAT: "Upbeat, energetic",
    MoodTone.ROMANTIC: "Romantic, tender",
    MoodTone.CHILL: "Chill, relaxing",
    MoodTone.EPIC: "Epic, cinematic",
}


def _build_prompt_fallback(title: str, occasion: str, mood_tone: int) -> str:
    mood = MOOD_TONE_STYLE.get(mood_tone, "")
    return (
        f"[verse]\n"
        f"A {mood.lower()} song for {occasion}.\n"
        f"{title}, a special moment to remember.\n"
        f"Memories that will last forever,\n"
        f"Celebrating this day together.\n\n"
        f"[chorus]\n"
        f"{title}, oh {title},\n"
        f"This {occasion} means so much.\n"
        f"Every moment shared with love,\n"
        f"Touched by your gentle touch.\n\n"
        f"[verse]\n"
        f"The laughter and the joy we share,\n"
        f"Show how much we truly care.\n"
        f"Through the years and days gone by,\n"
        f"Our bond will never say goodbye.\n\n"
        f"[chorus]\n"
        f"{title}, oh {title},\n"
        f"This {occasion} means so much.\n"
        f"Every moment shared with love,\n"
        f"Touched by your gentle touch.\n\n"
        f"[outro]\n"
        f"Here's to you on this special day.\n"
        f"[end]"
    )


def _build_prompt(title: str, occasion: str, mood_tone: int) -> str:
    mood = MOOD_TONE_STYLE.get(mood_tone, "")
    if not GEMINI_API_KEY:
        return _build_prompt_fallback(title, occasion, mood_tone)

    system_instruction = (
        "You are a professional songwriter. Generate song lyrics using ONLY these structural tags: "
        "[verse], [chorus], [outro], [end]. "
        "Output ONLY the lyrics with tags — no explanations, no extra text, no markdown."
    )
    user_prompt = (
        f"Write original song lyrics for a {mood.lower()} song.\n"
        f"Song title: {title}\n"
        f"Occasion: {occasion}\n"
        f"Structure: [verse], [chorus], [verse], [chorus], [outro], [end]\n"
        f"Each section 4 lines. Make it heartfelt and specific to the occasion."
    )

    try:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.9, "maxOutputTokens": 512},
        }
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        lyrics = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return lyrics
    except Exception:
        return _build_prompt_fallback(title, occasion, mood_tone)


# ── Suno Service ──────────────────────────────────────────────────────────────

class SunoService:
    @staticmethod
    def generate(title, style, callback_url, vocal_gender, prompt="") -> str:
        url = f"{SUNO_API_BASE_URL}/api/v1/generate"
        payload = {
            "customMode": True,
            "instrumental": False,
            "model": "V4",
            "title": title,
            "style": style,
            "callBackUrl": callback_url,
            "vocalGender": vocal_gender,
            "prompt": prompt,
        }
        headers = {
            "Authorization": f"Bearer {SUNO_API_TOKEN}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
            resp_json = resp.json()
            task_id = resp_json['data']['taskId']
            return task_id
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Suno API error {e.response.status_code}: {e.response.text}")
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Suno API unreachable: {e}")


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
        required = ["title", "occasion", "mood_tone", "voice_type", "duration"]
        missing = [f for f in required if data.get(f) in (None, "")]
        if missing:
            raise ValidationError("Missing required fields", fields=missing)
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
            )
        except (TypeError, ValueError):
            raise ValidationError("Invalid field type")

        vocal_gender = 'f' if voice_type_int == VoiceType.FEMALE else 'm'
        style = MOOD_TONE_STYLE.get(mood_tone_int, "Pop")
        callback_url = f"{CALLBACK_BASE_URL}/api/songs/callback/"

        try:
            prompt = _build_prompt(song.title, song.occasion, mood_tone_int)
            task_id = SunoService.generate(song.title, style, callback_url, vocal_gender, prompt=prompt)
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

        required = ["title", "occasion", "mood_tone", "voice_type", "duration"]
        missing = [f for f in required if data.get(f) in (None, "")]
        if missing:
            raise ValidationError("Missing required fields", fields=missing)

        try:
            mood_tone_int = int(data["mood_tone"])
            voice_type_int = int(data["voice_type"])
            title = str(data["title"])
            occasion = str(data["occasion"])
            duration = int(data["duration"])
        except (TypeError, ValueError):
            raise ValidationError("Invalid field type")

        vocal_gender = 'f' if voice_type_int == VoiceType.FEMALE else 'm'
        style = MOOD_TONE_STYLE.get(mood_tone_int, "Pop")
        callback_url = f"{CALLBACK_BASE_URL}/api/songs/callback/"
        prompt = _build_prompt(title, occasion, mood_tone_int)

        try:
            task_id = SunoService.generate(title, style, callback_url, vocal_gender, prompt=prompt)
        except RuntimeError:
            song.generation_status = GenerationStatus.ERROR
            song.save(update_fields=["generation_status"])
            raise

        song.title = title
        song.occasion = occasion
        song.mood_tone = mood_tone_int
        song.voice_type = voice_type_int
        song.duration = duration
        song.generation_status = GenerationStatus.GENERATING
        song.audio_file_url = ""
        song.share_url = ""
        song.suno_task_id = task_id
        song.save(update_fields=[
            "title", "occasion", "mood_tone", "voice_type", "duration",
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