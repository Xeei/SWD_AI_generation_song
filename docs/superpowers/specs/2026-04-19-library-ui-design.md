# Library UI — Design Spec

**Date:** 2026-04-19  
**Branch:** feature/song-generation

---

## Overview

A library page at `/library` showing all generated songs in a dense list view, with client-side search/filter, sticky audio player, and favorite toggling.

---

## Architecture

### New files

| File | Purpose |
|---|---|
| `frontend/app/library/page.tsx` | Page component — owns filter state and currentSong state |
| `frontend/components/SongList/index.tsx` | Table rows — receives filtered songs, emits onPlay / onFavorite |
| `frontend/components/AudioPlayer/index.tsx` | Sticky bottom bar — native `<audio>`, scrubber, play/pause, close |

### Modified files

| File | Change |
|---|---|
| `frontend/services/song.service.ts` | Add `getSongs`, `useSongs`, `updateSong`, `useUpdateSong` |

---

## Data Flow

1. `useSongs()` calls `GET /api/songs/` once on mount → `{ song_list: SongResponse[] }`
2. Filter state (`searchQuery`, `statusFilter`, `favoritesOnly`) lives in `LibraryPage` via `useState`
3. Filtered list derived via `useMemo(songs, filters)` — no API calls on filter change
4. Click ▶ on a row → set `currentSong` state in page → passed to `AudioPlayer`
5. Click ♡ → `useUpdateSong` → `PUT /api/songs/<id>/update/` `{ is_favorite }` → invalidate `songKeys.all` query

---

## Components

### `LibraryPage` (`app/library/page.tsx`)

- Fetches songs with `useSongs()`
- State: `searchQuery: string`, `statusFilter: number | null`, `favoritesOnly: boolean`, `currentSong: SongResponse | null`
- Computes `filteredSongs` via `useMemo`
- Renders: page title → filter bar → `<SongList>` → `<AudioPlayer>`

### `SongList` (`components/SongList/index.tsx`)

Props: `songs: SongResponse[]`, `currentSongId: string | null`, `onPlay: (song) => void`, `onFavorite: (song) => void`

Table columns:

| Col | Content |
|---|---|
| Play | ▶ / ⏸ button. Disabled + dimmed if `generation_status !== GENERATED` |
| Title | Song title (bold) + occasion (muted subtitle) |
| Mood | Colored pill badge from enum label |
| Duration | `M:SS` format (e.g. `2:30`). `—` if not generated |
| Status | Colored pill: Generated (green) / Generating (amber) / Error (red) |
| Favorite | ♡ / ♥ toggle button. Calls `onFavorite` |

Active (playing) row has highlighted border.

### `AudioPlayer` (`components/AudioPlayer/index.tsx`)

Props: `song: SongResponse | null`, `onClose: () => void`

- Renders `null` when no song
- Sticky positioned at page bottom
- Contains hidden `<audio src={song.audio_file_url}>` controlled via ref
- Shows: song title + occasion · play/pause button · progress scrubber (click to seek) · elapsed / total time · close (✕) button
- Syncs playback state via `onTimeUpdate` and `onEnded` audio events

### Filter Bar (inline in `LibraryPage`)

- Search `<Input>` — filters by `title.toLowerCase().includes(query)`
- Status `<select>` — All / Generated / Generating / Error (maps to `GenerationStatus` values)
- Favorites `<button>` toggle — filters `song.is_favorite === true`

---

## Service additions (`song.service.ts`)

```typescript
// fetch all songs
export const getSongs = (): Promise<SongResponse[]> =>
  instance.get<{ song_list: SongResponse[] }>('/songs/').then(r => r.data.song_list)

export const useSongs = () =>
  useQuery({ queryKey: songKeys.all, queryFn: getSongs })

// update song (used for favorite toggle)
export const updateSong = (songId: string, data: Partial<SongResponse>): Promise<SongResponse> =>
  instance.put<{ song: SongResponse }>(`/songs/${songId}/update/`, data).then(r => r.data.song)

export const useUpdateSong = () =>
  useMutation({
    mutationFn: ({ songId, data }: { songId: string; data: Partial<SongResponse> }) =>
      updateSong(songId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: songKeys.all }),
  })
```

`queryClient` must be created outside the provider component in `components/Provider/TanstackQuery.tsx` and exported so `useUpdateSong` can call `invalidateQueries` directly.

---

## Behavior Details

- Songs with `generation_status !== GENERATED` — play button disabled, row dimmed to 50% opacity
- Clicking ▶ on a different row while audio is playing → switches to new song immediately
- Clicking ✕ on player → `currentSong = null`, audio pauses
- Empty state (no songs or no filter matches) → centered message: "No songs found"
- Loading state → show skeleton rows (3 placeholder rows)

---

## Out of Scope

- Sorting columns (not requested)
- Pagination (small dataset, client-side filter sufficient)
- Delete song from library page
- Share song from library page
