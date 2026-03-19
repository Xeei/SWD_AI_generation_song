import json

from django.http import JsonResponse, HttpResponse
from .models import Song, PlayList, Creator


# ── Swagger / OpenAPI ─────────────────────────────────────────────────────────

_OPENAPI_SCHEMA = {
    "openapi": "3.0.3",
    "info": {
        "title": "AI Generation Song API",
        "version": "1.0.0",
        "description": "REST API for AI-powered song generation, playlist management, and creator accounts.",
    },
    "servers": [{"url": "/api"}],
    "paths": {
        # ── Song ──────────────────────────────────────────────────────────────
        "/songs/": {
            "get": {
                "tags": ["Song"],
                "summary": "List all songs",
                "operationId": "listSongs",
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SongList"}}},
                    }
                },
            }
        },
        "/songs/create/": {
            "post": {
                "tags": ["Song"],
                "summary": "Create a song",
                "operationId": "createSong",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SongCreate"}}},
                },
                "responses": {
                    "201": {"description": "Created", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SongResponse"}}}},
                    "400": {"description": "Bad Request"},
                },
            }
        },
        "/songs/{song_id}/": {
            "get": {
                "tags": ["Song"],
                "summary": "Get a song",
                "operationId": "getSong",
                "parameters": [{"name": "song_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}],
                "responses": {
                    "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SongResponse"}}}},
                    "404": {"description": "Not Found"},
                },
            }
        },
        "/songs/{song_id}/update/": {
            "put": {
                "tags": ["Song"],
                "summary": "Update a song",
                "operationId": "updateSong",
                "parameters": [{"name": "song_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SongUpdate"}}},
                },
                "responses": {
                    "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SongResponse"}}}},
                    "400": {"description": "Bad Request"},
                    "404": {"description": "Not Found"},
                },
            }
        },
        "/songs/{song_id}/delete/": {
            "delete": {
                "tags": ["Song"],
                "summary": "Delete a song",
                "operationId": "deleteSong",
                "parameters": [{"name": "song_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}],
                "responses": {
                    "200": {"description": "Deleted"},
                    "404": {"description": "Not Found"},
                },
            }
        },
        # ── PlayList ──────────────────────────────────────────────────────────
        "/playlists/": {
            "get": {
                "tags": ["PlayList"],
                "summary": "List all playlists",
                "operationId": "listPlaylists",
                "responses": {
                    "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PlayListList"}}}},
                },
            }
        },
        "/playlists/create/": {
            "post": {
                "tags": ["PlayList"],
                "summary": "Create a playlist",
                "operationId": "createPlaylist",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PlayListCreate"}}},
                },
                "responses": {
                    "201": {"description": "Created", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PlayListResponse"}}}},
                    "400": {"description": "Bad Request"},
                },
            }
        },
        "/playlists/{playlist_id}/": {
            "get": {
                "tags": ["PlayList"],
                "summary": "Get a playlist",
                "operationId": "getPlaylist",
                "parameters": [{"name": "playlist_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}],
                "responses": {
                    "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PlayListResponse"}}}},
                    "404": {"description": "Not Found"},
                },
            }
        },
        "/playlists/{playlist_id}/update/": {
            "put": {
                "tags": ["PlayList"],
                "summary": "Update a playlist",
                "operationId": "updatePlaylist",
                "parameters": [{"name": "playlist_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PlayListCreate"}}},
                },
                "responses": {
                    "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PlayListResponse"}}}},
                    "400": {"description": "Bad Request"},
                    "404": {"description": "Not Found"},
                },
            }
        },
        "/playlists/{playlist_id}/delete/": {
            "delete": {
                "tags": ["PlayList"],
                "summary": "Delete a playlist",
                "operationId": "deletePlaylist",
                "parameters": [{"name": "playlist_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}],
                "responses": {
                    "200": {"description": "Deleted"},
                    "404": {"description": "Not Found"},
                },
            }
        },
        # ── Creator ───────────────────────────────────────────────────────────
        "/creators/": {
            "get": {
                "tags": ["Creator"],
                "summary": "List all creators",
                "operationId": "listCreators",
                "responses": {
                    "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreatorList"}}}},
                },
            }
        },
        "/creators/create/": {
            "post": {
                "tags": ["Creator"],
                "summary": "Create a creator",
                "operationId": "createCreator",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreatorCreate"}}},
                },
                "responses": {
                    "201": {"description": "Created", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreatorResponse"}}}},
                    "400": {"description": "Bad Request"},
                },
            }
        },
        "/creators/{creator_id}/": {
            "get": {
                "tags": ["Creator"],
                "summary": "Get a creator",
                "operationId": "getCreator",
                "parameters": [{"name": "creator_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}],
                "responses": {
                    "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreatorResponse"}}}},
                    "404": {"description": "Not Found"},
                },
            }
        },
        "/creators/{creator_id}/update/": {
            "put": {
                "tags": ["Creator"],
                "summary": "Update a creator",
                "operationId": "updateCreator",
                "parameters": [{"name": "creator_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreatorCreate"}}},
                },
                "responses": {
                    "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreatorResponse"}}}},
                    "400": {"description": "Bad Request"},
                    "404": {"description": "Not Found"},
                },
            }
        },
        "/creators/{creator_id}/delete/": {
            "delete": {
                "tags": ["Creator"],
                "summary": "Delete a creator",
                "operationId": "deleteCreator",
                "parameters": [{"name": "creator_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}}],
                "responses": {
                    "200": {"description": "Deleted"},
                    "404": {"description": "Not Found"},
                },
            }
        },
    },
    "components": {
        "schemas": {
            # Song schemas
            "Song": {
                "type": "object",
                "properties": {
                    "song_id": {"type": "string", "format": "uuid"},
                    "title": {"type": "string"},
                    "occasion": {"type": "string"},
                    "generation_status": {"type": "integer", "enum": [1, 2, 3], "description": "1=Generating, 2=Generated, 3=Error"},
                    "mood_tone": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6], "description": "1=Happy, 2=Sad, 3=Upbeat, 4=Romantic, 5=Chill, 6=Epic"},
                    "voice_type": {"type": "integer", "enum": [1, 2, 3, 4, 5], "description": "1=Male Pop, 2=Female Pop, 3=Male Rock, 4=Female Rock, 5=Instrumental Only"},
                    "lyrics_content": {"type": "string"},
                    "duration": {"type": "integer"},
                    "audio_file_url": {"type": "string"},
                    "share_url": {"type": "string"},
                    "is_favorite": {"type": "boolean"},
                    "time_stamp": {"type": "string", "format": "date-time"},
                },
            },
            "SongCreate": {
                "type": "object",
                "required": ["title", "occasion", "mood_tone", "voice_type", "lyrics_content", "duration", "audio_file_url", "share_url"],
                "properties": {
                    "title": {"type": "string"},
                    "occasion": {"type": "string"},
                    "generation_status": {"type": "integer", "default": 1},
                    "mood_tone": {"type": "integer"},
                    "voice_type": {"type": "integer"},
                    "lyrics_content": {"type": "string"},
                    "duration": {"type": "integer"},
                    "audio_file_url": {"type": "string"},
                    "share_url": {"type": "string"},
                    "is_favorite": {"type": "boolean", "default": False},
                },
            },
            "SongUpdate": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "occasion": {"type": "string"},
                    "generation_status": {"type": "integer"},
                    "mood_tone": {"type": "integer"},
                    "voice_type": {"type": "integer"},
                    "lyrics_content": {"type": "string"},
                    "duration": {"type": "integer"},
                    "audio_file_url": {"type": "string"},
                    "share_url": {"type": "string"},
                    "is_favorite": {"type": "boolean"},
                },
            },
            "SongResponse": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "song": {"$ref": "#/components/schemas/Song"},
                },
            },
            "SongList": {
                "type": "object",
                "properties": {
                    "song_list": {"type": "array", "items": {"$ref": "#/components/schemas/Song"}},
                },
            },
            # PlayList schemas
            "PlayList": {
                "type": "object",
                "properties": {
                    "playlist_id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "create_at": {"type": "string", "format": "date-time"},
                },
            },
            "PlayListCreate": {
                "type": "object",
                "required": ["name"],
                "properties": {"name": {"type": "string"}},
            },
            "PlayListResponse": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "playlist": {"$ref": "#/components/schemas/PlayList"},
                },
            },
            "PlayListList": {
                "type": "object",
                "properties": {
                    "playlist_list": {"type": "array", "items": {"$ref": "#/components/schemas/PlayList"}},
                },
            },
            # Creator schemas
            "Creator": {
                "type": "object",
                "properties": {
                    "creator_id": {"type": "string", "format": "uuid"},
                    "email": {"type": "string", "format": "email"},
                },
            },
            "CreatorCreate": {
                "type": "object",
                "required": ["email"],
                "properties": {"email": {"type": "string", "format": "email"}},
            },
            "CreatorResponse": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "creator": {"$ref": "#/components/schemas/Creator"},
                },
            },
            "CreatorList": {
                "type": "object",
                "properties": {
                    "creator_list": {"type": "array", "items": {"$ref": "#/components/schemas/Creator"}},
                },
            },
        }
    },
}


def schema_view(request):
    return JsonResponse(_OPENAPI_SCHEMA)


def swagger_ui_view(request):
    html = """<!DOCTYPE html>
<html>
<head>
  <title>AI Generation Song API Docs</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
  SwaggerUIBundle({
    url: "/api/schema/",
    dom_id: "#swagger-ui",
    presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
    layout: "BaseLayout",
  });
</script>
</body>
</html>"""
    return HttpResponse(html)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _parse_json(request):
	try:
		return json.loads(request.body) if request.body else {}, None
	except json.JSONDecodeError:
		return None, JsonResponse({"error": "Invalid JSON payload"}, status=400)


def _song_dict(s):
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


def _playlist_dict(p):
	return {
		"playlist_id": str(p.playlist_id),
		"name": p.name,
		"create_at": p.create_at.isoformat(),
	}


def _creator_dict(c):
	return {
		"creator_id": str(c.creator_id),
		"email": c.email,
	}


# ── Song ─────────────────────────────────────────────────────────────────────

def song_list_view(request):
	songs = Song.objects.all()
	return JsonResponse({"song_list": list(songs.values())})


def create_song_view(request):
	if request.method != "POST":
		return JsonResponse({"error": "Method not allowed"}, status=405)

	payload, err = _parse_json(request)
	if err:
		return err

	required_fields = [
		"title", "occasion", "mood_tone", "voice_type",
		"lyrics_content", "duration", "audio_file_url", "share_url",
	]
	missing_fields = [f for f in required_fields if payload.get(f) in (None, "")]
	if missing_fields:
		return JsonResponse({"error": "Missing required fields", "fields": missing_fields}, status=400)

	try:
		song = Song.objects.create(
			title=payload.get("title"),
			occasion=payload.get("occasion"),
			generation_status=int(payload.get("generation_status", Song._meta.get_field("generation_status").default)),
			mood_tone=int(payload.get("mood_tone")),
			voice_type=int(payload.get("voice_type")),
			lyrics_content=payload.get("lyrics_content"),
			duration=int(payload.get("duration")),
			audio_file_url=payload.get("audio_file_url"),
			share_url=payload.get("share_url"),
			is_favorite=bool(payload.get("is_favorite", False)),
		)
	except (TypeError, ValueError):
		return JsonResponse({"error": "Invalid field type"}, status=400)

	return JsonResponse({"message": "Song created successfully", "song": _song_dict(song)}, status=201)


def song_detail_view(request, song_id):
	try:
		song = Song.objects.get(pk=song_id)
	except Song.DoesNotExist:
		return JsonResponse({"error": "Song not found"}, status=404)

	return JsonResponse({"song": _song_dict(song)})


def update_song_view(request, song_id):
	if request.method != "PUT":
		return JsonResponse({"error": "Method not allowed"}, status=405)

	try:
		song = Song.objects.get(pk=song_id)
	except Song.DoesNotExist:
		return JsonResponse({"error": "Song not found"}, status=404)

	payload, err = _parse_json(request)
	if err:
		return err

	updatable = {
		"title": str, "occasion": str, "lyrics_content": str,
		"audio_file_url": str, "share_url": str,
		"generation_status": int, "mood_tone": int, "voice_type": int, "duration": int,
		"is_favorite": bool,
	}
	try:
		for field, cast in updatable.items():
			if field in payload:
				setattr(song, field, cast(payload[field]))
	except (TypeError, ValueError):
		return JsonResponse({"error": "Invalid field type"}, status=400)

	song.save()
	return JsonResponse({"message": "Song updated successfully", "song": _song_dict(song)})


def delete_song_view(request, song_id):
	if request.method != "DELETE":
		return JsonResponse({"error": "Method not allowed"}, status=405)

	try:
		song = Song.objects.get(pk=song_id)
	except Song.DoesNotExist:
		return JsonResponse({"error": "Song not found"}, status=404)

	song.delete()
	return JsonResponse({"message": "Song deleted successfully"})


# ── PlayList ──────────────────────────────────────────────────────────────────

def playlist_list_view(request):
	playlists = PlayList.objects.all()
	return JsonResponse({"playlist_list": list(playlists.values())})


def create_playlist_view(request):
	if request.method != "POST":
		return JsonResponse({"error": "Method not allowed"}, status=405)

	payload, err = _parse_json(request)
	if err:
		return err

	if not payload.get("name"):
		return JsonResponse({"error": "Missing required fields", "fields": ["name"]}, status=400)

	playlist = PlayList.objects.create(name=payload["name"])
	return JsonResponse({"message": "PlayList created successfully", "playlist": _playlist_dict(playlist)}, status=201)


def playlist_detail_view(request, playlist_id):
	try:
		playlist = PlayList.objects.get(pk=playlist_id)
	except PlayList.DoesNotExist:
		return JsonResponse({"error": "PlayList not found"}, status=404)

	return JsonResponse({"playlist": _playlist_dict(playlist)})


def update_playlist_view(request, playlist_id):
	if request.method != "PUT":
		return JsonResponse({"error": "Method not allowed"}, status=405)

	try:
		playlist = PlayList.objects.get(pk=playlist_id)
	except PlayList.DoesNotExist:
		return JsonResponse({"error": "PlayList not found"}, status=404)

	payload, err = _parse_json(request)
	if err:
		return err

	if not payload.get("name"):
		return JsonResponse({"error": "Missing required fields", "fields": ["name"]}, status=400)

	playlist.name = payload["name"]
	playlist.save()
	return JsonResponse({"message": "PlayList updated successfully", "playlist": _playlist_dict(playlist)})


def delete_playlist_view(request, playlist_id):
	if request.method != "DELETE":
		return JsonResponse({"error": "Method not allowed"}, status=405)

	try:
		playlist = PlayList.objects.get(pk=playlist_id)
	except PlayList.DoesNotExist:
		return JsonResponse({"error": "PlayList not found"}, status=404)

	playlist.delete()
	return JsonResponse({"message": "PlayList deleted successfully"})


# ── Creator ───────────────────────────────────────────────────────────────────

def creator_list_view(request):
	creators = Creator.objects.all()
	return JsonResponse({"creator_list": list(creators.values())})


def create_creator_view(request):
	if request.method != "POST":
		return JsonResponse({"error": "Method not allowed"}, status=405)

	payload, err = _parse_json(request)
	if err:
		return err

	if not payload.get("email"):
		return JsonResponse({"error": "Missing required fields", "fields": ["email"]}, status=400)

	if Creator.objects.filter(email=payload["email"]).exists():
		return JsonResponse({"error": "Email already exists"}, status=400)

	creator = Creator.objects.create(email=payload["email"])
	return JsonResponse({"message": "Creator created successfully", "creator": _creator_dict(creator)}, status=201)


def creator_detail_view(request, creator_id):
	try:
		creator = Creator.objects.get(pk=creator_id)
	except Creator.DoesNotExist:
		return JsonResponse({"error": "Creator not found"}, status=404)

	return JsonResponse({"creator": _creator_dict(creator)})


def update_creator_view(request, creator_id):
	if request.method != "PUT":
		return JsonResponse({"error": "Method not allowed"}, status=405)

	try:
		creator = Creator.objects.get(pk=creator_id)
	except Creator.DoesNotExist:
		return JsonResponse({"error": "Creator not found"}, status=404)

	payload, err = _parse_json(request)
	if err:
		return err

	if not payload.get("email"):
		return JsonResponse({"error": "Missing required fields", "fields": ["email"]}, status=400)

	if Creator.objects.filter(email=payload["email"]).exclude(pk=creator_id).exists():
		return JsonResponse({"error": "Email already exists"}, status=400)

	creator.email = payload["email"]
	creator.save()
	return JsonResponse({"message": "Creator updated successfully", "creator": _creator_dict(creator)})


def delete_creator_view(request, creator_id):
	if request.method != "DELETE":
		return JsonResponse({"error": "Method not allowed"}, status=405)

	try:
		creator = Creator.objects.get(pk=creator_id)
	except Creator.DoesNotExist:
		return JsonResponse({"error": "Creator not found"}, status=404)

	creator.delete()
	return JsonResponse({"message": "Creator deleted successfully"})