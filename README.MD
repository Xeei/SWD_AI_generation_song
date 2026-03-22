# Welcome to AI Generation Song Web Application

## Prerequisite
- [Python 3.14](https://www.python.org/downloads/release/python-3143/)

## Installation
### 1. Set up python vitual enviroment
**macos/ubuntu:**
```bash
python3 -m venv .venv
```
**window (cmd):**
```bash
python -m venv .venv
```

### 2. Active venv
**macos/ubuntu:**
```bash
source .venv/bin/activate
```
**window (cmd):**
```bash
venv\\Scripts\\activate
```

### 3. Install python environment
```bash
pip install -r requirements.txt
```

## How to run
After activate your python3 vitual environment excute this command
```bash
python manage.py runserver
```
open browser to open document api http://localhost:8000/api/docs

## Documentation
### Domain Diagram
<img src="./asset/Domain_Diagram.png" width="100%" height="100%" alt="Domain Diagram" />

### CRUD API Reference

Base URL: `http://localhost:8000/api`

---

#### Song

| Operation | Method | URL |
|-----------|--------|-----|
| List all songs | GET | `/api/songs/` |
| Get a song | GET | `/api/songs/{song_id}/` |
| Create a song | POST | `/api/songs/create/` |
| Update a song | PUT | `/api/songs/{song_id}/update/` |
| Delete a song | DELETE | `/api/songs/{song_id}/delete/` |

**Create / Update request body:**
```json
{
  "title": "string",
  "occasion": "string",
  "mood_tone": 1,
  "voice_type": 1,
  "lyrics_content": "string",
  "duration": 180,
  "audio_file_url": "string",
  "share_url": "string",
  "generation_status": 0,
  "is_favorite": false
}
```
> `title`, `occasion`, `mood_tone`, `voice_type`, `lyrics_content`, `duration`, `audio_file_url`, `share_url` are **required** for create.

**List response:**
```json
{
  "song_list": [
    {
      "song_id": "uuid",
      "title": "string",
      "occasion": "string",
      "generation_status": 0,
      "mood_tone": 1,
      "voice_type": 1,
      "lyrics_content": "string",
      "duration": 180,
      "audio_file_url": "string",
      "share_url": "string",
      "is_favorite": false,
      "time_stamp": "2026-01-01T00:00:00"
    }
  ]
}
```

---

#### PlayList

| Operation | Method | URL |
|-----------|--------|-----|
| List all playlists | GET | `/api/playlists/` |
| Get a playlist | GET | `/api/playlists/{playlist_id}/` |
| Create a playlist | POST | `/api/playlists/create/` |
| Update a playlist | PUT | `/api/playlists/{playlist_id}/update/` |
| Delete a playlist | DELETE | `/api/playlists/{playlist_id}/delete/` |

**Create / Update request body:**
```json
{
  "name": "string"
}
```
> `name` is **required**.

**List response:**
```json
{
  "playlist_list": [
    {
      "playlist_id": "uuid",
      "name": "string",
      "create_at": "2026-01-01T00:00:00"
    }
  ]
}
```

---

#### Creator

| Operation | Method | URL |
|-----------|--------|-----|
| List all creators | GET | `/api/creators/` |
| Get a creator | GET | `/api/creators/{creator_id}/` |
| Create a creator | POST | `/api/creators/create/` |
| Update a creator | PUT | `/api/creators/{creator_id}/update/` |
| Delete a creator | DELETE | `/api/creators/{creator_id}/delete/` |

**Create / Update request body:**
```json
{
  "email": "string"
}
```
> `email` is **required** and must be unique.

**List response:**
```json
{
  "creator_list": [
    {
      "creator_id": "uuid",
      "email": "string"
    }
  ]
}
```

---

#### Error responses

| Status | Meaning |
|--------|---------|
| 400 | Validation error — missing or invalid fields |
| 404 | Resource not found |
| 405 | Method not allowed |

**Validation error example:**
```json
{
  "error": "Missing required fields",
  "fields": ["title", "occasion"]
}
```
