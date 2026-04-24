# Layer Architecture Diagram

```mermaid
graph TB
    %% ─── UI LAYER ───────────────────────────────────────────────
    subgraph UI["🖥️  UI Layer (Next.js Pages & Components)"]
        direction TB
        subgraph Pages["Pages"]
            P1[LandingPage<br/>/]
            P2[GenerationPage<br/>/generation]
            P3[LibraryPage<br/>/library]
            P4[PlaylistsPage<br/>/playlists]
            P5[PlaylistDetailPage<br/>/playlists/id]
            P6[SharePage<br/>/share/id]
            P7[LoginPage<br/>/login]
        end
        subgraph Components["Components"]
            C1[AppSidebar]
            C2[SongList]
            C3[AudioPlayer]
            C4[RegenerateModal]
            C5[AddToPlaylistModal]
            C6[AuthButton]
        end
    end

    %% ─── CONTROLLER LAYER ───────────────────────────────────────
    subgraph Controller["⚙️  Controller Layer"]
        direction TB
        subgraph FEServices["Frontend Services (TanStack Query)"]
            S1[song.service<br/>useSongs · useGenerateSong<br/>useUpdateSong · useDeleteSong<br/>useRegenerateSong · useSongById]
            S2[playlist.service<br/>usePlaylists · usePlaylist<br/>useCreatePlaylist · useDeletePlaylist<br/>useAddSongToPlaylist · useRemoveSongFromPlaylist]
            S3[creator.service<br/>useCreatorId · syncCreator]
            S4[enum.service<br/>useEnumChoices]
        end
        subgraph BEViews["Backend Views (Django)"]
            V1[SongUseCase<br/>list · get · create · update<br/>delete · generate · regenerate]
            V2[PlaylistUseCase<br/>list · create · update · delete<br/>add_song · remove_song]
            V3[CreatorUseCase<br/>list · get · create · update<br/>delete · sync]
            V4[View Functions<br/>song_list_view · generate_song_view<br/>suno_callback_view · playlist_views<br/>creator_views · enum_choices_view]
        end
    end

    %% ─── MODEL LAYER ────────────────────────────────────────────
    subgraph Model["🗄️  Model Layer (Django ORM)"]
        direction LR
        M1[Song<br/>song_id · title · occasion<br/>mood_tone · voice_type · duration<br/>audio_file_url · share_url<br/>generation_status · is_favorite<br/>time_stamp · creator_id]
        M2[PlayList<br/>playlist_id · name<br/>create_at · creator_id]
        M3[PlaylistSong<br/>playlist · song · order]
        M4[Creator<br/>creator_id · email]
        M5[Choices<br/>GenerationStatus<br/>MoodTone · VoiceType]
    end

    %% ─── RELATIONSHIPS ──────────────────────────────────────────
    Pages --> FEServices
    Components --> FEServices
    FEServices -->|HTTP REST| V4
    V4 --> V1
    V4 --> V2
    V4 --> V3
    V1 --> M1
    V1 --> M4
    V2 --> M2
    V2 --> M3
    V3 --> M4
    M3 --> M1
    M3 --> M2
    M1 --> M5

    %% ─── COLORS ─────────────────────────────────────────────────
    classDef uiPage     fill:#1e3a5f,stroke:#3b82f6,color:#bfdbfe
    classDef uiComp     fill:#1e3a5f,stroke:#60a5fa,color:#bfdbfe
    classDef feService  fill:#1a3a2a,stroke:#22c55e,color:#bbf7d0
    classDef beView     fill:#1a3a2a,stroke:#4ade80,color:#bbf7d0
    classDef model      fill:#3b1f1f,stroke:#f87171,color:#fecaca
    classDef choices    fill:#2d1f3b,stroke:#c084fc,color:#e9d5ff

    class P1,P2,P3,P4,P5,P6,P7 uiPage
    class C1,C2,C3,C4,C5,C6 uiComp
    class S1,S2,S3,S4 feService
    class V1,V2,V3,V4 beView
    class M1,M2,M3,M4 model
    class M5 choices
```

## Layer Summary

| Layer                              | Color                | Responsibility                                         |
| ---------------------------------- | -------------------- | ------------------------------------------------------ |
| **UI — Pages**                     | Blue (dark)          | Route-level screens, compose components                |
| **UI — Components**                | Blue (light border)  | Reusable UI blocks, no direct API calls                |
| **Controller — Frontend Services** | Green (dark)         | HTTP calls, caching, mutation via TanStack Query       |
| **Controller — Backend Views**     | Green (light border) | Request routing, use-case orchestration                |
| **Model — Entities**               | Red                  | Django ORM models, DB schema                           |
| **Model — Choices**                | Purple               | Enum constants (GenerationStatus, MoodTone, VoiceType) |

```

```
