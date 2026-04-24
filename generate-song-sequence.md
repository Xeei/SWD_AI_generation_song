# Generate Song — Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant GenPage as GenerationPage<br/>(UI)
    participant SongSvc as song.service<br/>(Frontend)
    participant GenView as generate_song_view<br/>(Django)
    participant UseCase as SongUseCase<br/>(Backend)
    participant Strategy as SongGenerateStrategy<br/>(Mock / Suno)
    participant SunoAPI as Suno API<br/>(External)
    participant DB as Database<br/>(Song Model)
    participant CallbackView as suno_callback_view<br/>(Django)

    %% ── 1. User submits form ──────────────────────────────────
    User->>GenPage: Fill form & submit<br/>(title, occasion, mood, voice, duration)

    %% ── 2. Validation on frontend ────────────────────────────
    alt Missing required fields
        GenPage-->>User: Show validation error (zod)
    else Form valid
        GenPage->>SongSvc: useGenerateSong(payload)
        SongSvc->>GenView: POST /api/songs/generate/
    end

    %% ── 3. Backend input validation ──────────────────────────
    GenView->>UseCase: create_song(payload)

    alt Missing fields / invalid types
        UseCase-->>GenView: raise ValidationError
        GenView-->>SongSvc: 400 { error, fields }
        SongSvc-->>GenPage: Show error message
        GenPage-->>User: "Failed to start generation"
    else Creator not found
        UseCase-->>GenView: raise ValidationError "Creator not found"
        GenView-->>SongSvc: 400 { error }
        SongSvc-->>GenPage: Show error message
        GenPage-->>User: "Failed to start generation"
    else Inputs valid
        %% ── 4. Save Song with GENERATING status ──────────────
        UseCase->>DB: Song.objects.create(status=GENERATING)
        DB-->>UseCase: song (song_id, suno_task_id=null)

        %% ── 5. Call generation strategy ──────────────────────
        UseCase->>Strategy: generate(title, style, callback_url)

        alt Strategy = MockStrategy
            Strategy-->>UseCase: task_id = "mock_<uuid>"
            Note over Strategy: Stores audio_url in memory.<br/>No external call.
        else Strategy = SunoStrategy
            Strategy->>SunoAPI: POST /api/v1/generate<br/>{ title, style, callBackUrl }

            alt Suno API unreachable / HTTP error
                SunoAPI-->>Strategy: ConnectionError / HTTP 4xx-5xx
                Strategy-->>UseCase: raise RuntimeError
                UseCase->>DB: song.generation_status = ERROR
                DB-->>UseCase: saved
                UseCase-->>GenView: raise RuntimeError
                GenView-->>SongSvc: 502 { error }
                SongSvc-->>GenPage: Show error message
                GenPage-->>User: "Failed to start generation"
            else Suno accepted
                SunoAPI-->>Strategy: 200 { data.taskId }
                Strategy-->>UseCase: task_id
            end
        end

        %% ── 6. Save task_id & return 202 ─────────────────────
        UseCase->>DB: song.suno_task_id = task_id (save)
        DB-->>UseCase: saved
        UseCase-->>GenView: song dict (status=GENERATING)
        GenView-->>SongSvc: 202 { song }
        SongSvc-->>GenPage: song.song_id
        GenPage-->>User: Show "Generating…" state
    end

    %% ── 7. Frontend polls ────────────────────────────────────
    loop Every 5 s while status = GENERATING
        GenPage->>SongSvc: useSongById(song_id)
        SongSvc->>GenView: GET /api/songs/{song_id}/
        GenView-->>SongSvc: song (status still GENERATING)
        SongSvc-->>GenPage: Update UI
    end

    %% ── 8. Callback received (async) ─────────────────────────
    Note over SunoAPI,CallbackView: Async — arrives after generation completes (1–2 min)

    alt Callback = SUCCESS (Suno or Mock)
        SunoAPI--)CallbackView: POST /api/songs/callback/<br/>{ code:200, status:"SUCCESS", sunoData }
        CallbackView->>UseCase: handle_suno_callback(payload)
        UseCase->>DB: song.audio_file_url = audioUrl<br/>song.share_url = sourceAudioUrl<br/>song.generation_status = GENERATED
        DB-->>UseCase: saved
        UseCase-->>CallbackView: ok
        CallbackView-->>SunoAPI: 200 { message }
    else Callback = FAILURE
        SunoAPI--)CallbackView: POST /api/songs/callback/<br/>{ code: ≠200 or status: ≠SUCCESS }
        CallbackView->>UseCase: handle_suno_callback(payload)
        UseCase->>DB: song.generation_status = ERROR
        DB-->>UseCase: saved
        UseCase-->>CallbackView: ok
        CallbackView-->>SunoAPI: 200 { message }
    else Song not found for task_id
        CallbackView->>UseCase: handle_suno_callback(payload)
        UseCase-->>CallbackView: raise NotFound
        CallbackView-->>SunoAPI: 404 { error }
    end

    %% ── 9. Frontend poll picks up final status ───────────────
    GenPage->>SongSvc: useSongById(song_id) [next poll]
    SongSvc->>GenView: GET /api/songs/{song_id}/
    GenView-->>SongSvc: song (status = GENERATED or ERROR)

    alt Status = GENERATED
        SongSvc-->>GenPage: song with audio_file_url
        GenPage-->>User: Show audio player + share link
        Note over GenPage: Poll stops (refetchInterval returns false)
    else Status = ERROR
        SongSvc-->>GenPage: song (status=ERROR)
        GenPage-->>User: Show "Generation failed" message
        Note over GenPage: Poll stops
    end
```

## Alternative Flows Summary

| # | Trigger | Result |
|---|---------|--------|
| 1 | Frontend form missing fields | Zod validation error — no API call |
| 2 | Backend missing/invalid fields | 400 ValidationError — song not created |
| 3 | Creator not found in DB | 400 ValidationError — song not created |
| 4 | Suno API unreachable / HTTP error | Song saved as ERROR, 502 returned |
| 5 | MockStrategy active | No Suno call — local audio URL used |
| 6 | Callback arrives with failure status | Song marked ERROR |
| 7 | Callback task_id not in DB | 404 returned to Suno |
| 8 | Poll finds GENERATED status | Audio player shown, polling stops |
| 9 | Poll finds ERROR status | Error message shown, polling stops |
