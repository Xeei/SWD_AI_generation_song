# Library UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/library` page that lists all songs in a table with client-side search/filter, sticky audio player, and favorite toggling.

**Architecture:** Fetch all songs once on mount, filter client-side via `useMemo`. `LibraryPage` owns filter state and `currentSong` state, passes them to `SongList` and `AudioPlayer` as props. Audio playback uses a native `<audio>` element controlled via a ref in `AudioPlayer`.

**Tech Stack:** Next.js 16 App Router, React 19, TanStack Query v5, Tailwind CSS v4, shadcn/ui, TypeScript

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Create | `frontend/lib/queryClient.ts` | Singleton `QueryClient` instance — imported by both provider and service |
| Modify | `frontend/components/Provider/TanstackQuery.tsx` | Import `queryClient` from `lib/queryClient.ts` instead of creating inline |
| Modify | `frontend/services/song.service.ts` | Add `getSongs`, `useSongs`, `updateSong`, `useUpdateSong` |
| Create | `frontend/components/SongList/index.tsx` | Table rows — play, title, mood, duration, status, favorite |
| Create | `frontend/components/AudioPlayer/index.tsx` | Sticky bottom bar with native `<audio>` |
| Create | `frontend/app/library/page.tsx` | Page — filter state, currentSong state, renders SongList + AudioPlayer |

---

## Task 1: Extract `queryClient` to its own module

**Files:**
- Create: `frontend/lib/queryClient.ts`
- Modify: `frontend/components/Provider/TanstackQuery.tsx`

Currently `new QueryClient()` is created inside the component on every render — this is a bug. Extract to a singleton module so both the provider and service files can import it without circular dependencies.

- [ ] **Step 1: Create `frontend/lib/queryClient.ts`**

```typescript
import { QueryClient } from "@tanstack/react-query"

export const queryClient = new QueryClient()
```

- [ ] **Step 2: Update TanstackQuery.tsx to import from lib**

Replace the entire file with:

```tsx
"use client"
import { QueryClientProvider } from "@tanstack/react-query"
import React from "react"
import { queryClient } from "@/lib/queryClient"

interface Props {
    children: React.ReactNode
}

export default function TanstackQueryProvider({ children }: Props) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}
```

- [ ] **Step 3: Verify dev server starts without errors**

```bash
cd frontend && pnpm dev
```

Expected: no TypeScript or runtime errors in terminal.

- [ ] **Step 4: Commit**

```bash
git add frontend/lib/queryClient.ts frontend/components/Provider/TanstackQuery.tsx
git commit -m "fix: extract queryClient singleton to lib/queryClient.ts"
```

---

## Task 2: Add song service functions

**Files:**
- Modify: `frontend/services/song.service.ts`

- [ ] **Step 1: Add imports and new functions**

Add to the top of the file — import `queryClient`:

```typescript
import { queryClient } from '@/lib/queryClient'
```

Then add these exports after the existing `useSongById` hook:

```typescript
export const getSongs = (): Promise<SongResponse[]> =>
    instance
        .get<{ song_list: SongResponse[] }>('/songs/')
        .then((res) => res.data.song_list)

export const useSongs = () =>
    useQuery({
        queryKey: songKeys.all,
        queryFn: getSongs,
    })

export const updateSong = (
    songId: string,
    data: Partial<Pick<SongResponse, 'is_favorite' | 'title' | 'occasion'>>
): Promise<SongResponse> =>
    instance
        .put<{ song: SongResponse }>(`/songs/${songId}/update/`, data)
        .then((res) => res.data.song)

export const useUpdateSong = () =>
    useMutation({
        mutationFn: ({
            songId,
            data,
        }: {
            songId: string
            data: Partial<Pick<SongResponse, 'is_favorite' | 'title' | 'occasion'>>
        }) => updateSong(songId, data),
        onSuccess: () =>
            queryClient.invalidateQueries({ queryKey: songKeys.all }),
    })
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend && pnpm typecheck
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/services/song.service.ts
git commit -m "feat: add getSongs, useSongs, updateSong, useUpdateSong to song service"
```

---

## Task 3: Create SongList component

**Files:**
- Create: `frontend/components/SongList/index.tsx`

- [ ] **Step 1: Create the file**

```tsx
import { SongResponse, GenerationStatus } from '@/services/song.service'

const MOOD_LABEL: Record<number, string> = {
    1: 'Happy',
    2: 'Sad',
    3: 'Upbeat',
    4: 'Romantic',
    5: 'Chill',
    6: 'Epic',
}

const MOOD_CLASS: Record<number, string> = {
    1: 'bg-yellow-500/20 text-yellow-300',
    2: 'bg-blue-500/20 text-blue-300',
    3: 'bg-green-500/20 text-green-300',
    4: 'bg-pink-500/20 text-pink-300',
    5: 'bg-cyan-500/20 text-cyan-300',
    6: 'bg-orange-500/20 text-orange-300',
}

function formatDuration(seconds: number): string {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${String(s).padStart(2, '0')}`
}

interface Props {
    songs: SongResponse[]
    currentSongId: string | null
    onPlay: (song: SongResponse) => void
    onFavorite: (song: SongResponse) => void
}

export default function SongList({ songs, currentSongId, onPlay, onFavorite }: Props) {
    if (songs.length === 0) {
        return (
            <div className="flex min-h-40 items-center justify-center text-sm text-muted-foreground">
                No songs found
            </div>
        )
    }

    return (
        <div className="flex flex-col gap-1">
            {/* Header */}
            <div className="grid grid-cols-[32px_1fr_100px_60px_90px_32px] gap-3 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <span />
                <span>Title</span>
                <span>Mood</span>
                <span>Duration</span>
                <span>Status</span>
                <span />
            </div>

            {/* Rows */}
            {songs.map((song) => {
                const isPlaying = song.song_id === currentSongId
                const isPlayable = song.generation_status === GenerationStatus.GENERATED
                const statusLabel =
                    song.generation_status === GenerationStatus.GENERATED
                        ? 'Generated'
                        : song.generation_status === GenerationStatus.GENERATING
                          ? 'Generating'
                          : 'Error'
                const statusClass =
                    song.generation_status === GenerationStatus.GENERATED
                        ? 'bg-green-500/20 text-green-400'
                        : song.generation_status === GenerationStatus.GENERATING
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-red-500/20 text-red-400'

                return (
                    <div
                        key={song.song_id}
                        className={[
                            'grid grid-cols-[32px_1fr_100px_60px_90px_32px] gap-3 items-center rounded-lg border px-3 py-2 transition-colors',
                            isPlaying
                                ? 'border-primary bg-primary/10'
                                : 'border-border bg-card',
                            !isPlayable && 'opacity-50',
                        ]
                            .filter(Boolean)
                            .join(' ')}
                    >
                        <button
                            onClick={() => isPlayable && onPlay(song)}
                            disabled={!isPlayable}
                            className="flex items-center justify-center text-primary disabled:cursor-not-allowed disabled:text-muted-foreground"
                            aria-label={isPlaying ? 'Pause' : 'Play'}
                        >
                            {isPlaying ? '⏸' : '▶'}
                        </button>

                        <div className="min-w-0">
                            <div className="truncate text-sm font-semibold">{song.title}</div>
                            <div className="truncate text-xs text-muted-foreground">
                                {song.occasion}
                            </div>
                        </div>

                        <span
                            className={`w-fit rounded-full px-2 py-0.5 text-xs ${MOOD_CLASS[song.mood_tone] ?? 'bg-muted text-muted-foreground'}`}
                        >
                            {MOOD_LABEL[song.mood_tone] ?? '—'}
                        </span>

                        <span className="text-xs text-muted-foreground">
                            {isPlayable ? formatDuration(song.duration) : '—'}
                        </span>

                        <span className={`w-fit rounded-full px-2 py-0.5 text-xs ${statusClass}`}>
                            {statusLabel}
                        </span>

                        <button
                            onClick={() => onFavorite(song)}
                            className={
                                song.is_favorite
                                    ? 'text-amber-400'
                                    : 'text-muted-foreground hover:text-amber-400'
                            }
                            aria-label={song.is_favorite ? 'Unfavorite' : 'Favorite'}
                        >
                            {song.is_favorite ? '♥' : '♡'}
                        </button>
                    </div>
                )
            })}
        </div>
    )
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend && pnpm typecheck
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/components/SongList/index.tsx
git commit -m "feat: add SongList component"
```

---

## Task 4: Create AudioPlayer component

**Files:**
- Create: `frontend/components/AudioPlayer/index.tsx`

- [ ] **Step 1: Create the file**

```tsx
"use client"

import { useEffect, useRef, useState } from 'react'
import { SongResponse } from '@/services/song.service'

interface Props {
    song: SongResponse | null
    onClose: () => void
}

export default function AudioPlayer({ song, onClose }: Props) {
    const audioRef = useRef<HTMLAudioElement>(null)
    const [isPlaying, setIsPlaying] = useState(false)
    const [currentTime, setCurrentTime] = useState(0)
    const [duration, setDuration] = useState(0)

    // When song changes, reset and autoplay
    useEffect(() => {
        const audio = audioRef.current
        if (!audio || !song) return
        audio.src = song.audio_file_url
        audio.currentTime = 0
        setCurrentTime(0)
        setIsPlaying(false)
        audio.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false))
    }, [song?.song_id])

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            audioRef.current?.pause()
        }
    }, [])

    function togglePlay() {
        const audio = audioRef.current
        if (!audio) return
        if (isPlaying) {
            audio.pause()
            setIsPlaying(false)
        } else {
            audio.play().then(() => setIsPlaying(true)).catch(() => {})
        }
    }

    function handleSeek(e: React.MouseEvent<HTMLDivElement>) {
        const audio = audioRef.current
        if (!audio || !duration) return
        const rect = e.currentTarget.getBoundingClientRect()
        const ratio = (e.clientX - rect.left) / rect.width
        audio.currentTime = ratio * duration
    }

    function formatTime(s: number) {
        if (!isFinite(s)) return '0:00'
        const m = Math.floor(s / 60)
        const sec = Math.floor(s % 60)
        return `${m}:${String(sec).padStart(2, '0')}`
    }

    if (!song) return null

    const progress = duration > 0 ? (currentTime / duration) * 100 : 0

    return (
        <div className="fixed bottom-0 left-0 right-0 z-50 flex items-center gap-3 border-t border-border bg-card px-4 py-3 shadow-lg">
            <audio
                ref={audioRef}
                onTimeUpdate={() => setCurrentTime(audioRef.current?.currentTime ?? 0)}
                onLoadedMetadata={() => setDuration(audioRef.current?.duration ?? 0)}
                onEnded={() => setIsPlaying(false)}
            />

            {/* Song info */}
            <div className="w-32 shrink-0">
                <div className="truncate text-sm font-semibold">{song.title}</div>
                <div className="truncate text-xs text-muted-foreground">{song.occasion}</div>
            </div>

            {/* Play/pause */}
            <button
                onClick={togglePlay}
                className="shrink-0 text-xl text-primary"
                aria-label={isPlaying ? 'Pause' : 'Play'}
            >
                {isPlaying ? '⏸' : '▶'}
            </button>

            {/* Scrubber */}
            <div className="flex flex-1 items-center gap-2">
                <span className="shrink-0 text-xs tabular-nums text-muted-foreground">
                    {formatTime(currentTime)}
                </span>
                <div
                    className="relative h-1.5 flex-1 cursor-pointer rounded-full bg-muted"
                    onClick={handleSeek}
                >
                    <div
                        className="h-full rounded-full bg-primary transition-all"
                        style={{ width: `${progress}%` }}
                    />
                </div>
                <span className="shrink-0 text-xs tabular-nums text-muted-foreground">
                    {formatTime(duration)}
                </span>
            </div>

            {/* Close */}
            <button
                onClick={onClose}
                className="shrink-0 text-muted-foreground hover:text-foreground"
                aria-label="Close player"
            >
                ✕
            </button>
        </div>
    )
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend && pnpm typecheck
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/components/AudioPlayer/index.tsx
git commit -m "feat: add AudioPlayer sticky bottom component"
```

---

## Task 5: Create library page

**Files:**
- Create: `frontend/app/library/page.tsx`

- [ ] **Step 1: Create library directory and page**

```bash
mkdir -p frontend/app/library
```

```tsx
"use client"

import { useMemo, useState } from 'react'
import { Input } from '@/components/ui/input'
import SongList from '@/components/SongList'
import AudioPlayer from '@/components/AudioPlayer'
import { Skeleton } from '@/components/ui/skeleton'
import {
    GenerationStatus,
    SongResponse,
    useSongs,
    useUpdateSong,
} from '@/services/song.service'

export default function LibraryPage() {
    const { data: songs, isLoading } = useSongs()
    const { mutate: updateSong } = useUpdateSong()

    const [searchQuery, setSearchQuery] = useState('')
    const [statusFilter, setStatusFilter] = useState<number | ''>('')
    const [favoritesOnly, setFavoritesOnly] = useState(false)
    const [currentSong, setCurrentSong] = useState<SongResponse | null>(null)

    const filteredSongs = useMemo(() => {
        if (!songs) return []
        return songs.filter((s) => {
            if (searchQuery && !s.title.toLowerCase().includes(searchQuery.toLowerCase()))
                return false
            if (statusFilter !== '' && s.generation_status !== statusFilter) return false
            if (favoritesOnly && !s.is_favorite) return false
            return true
        })
    }, [songs, searchQuery, statusFilter, favoritesOnly])

    function handleFavorite(song: SongResponse) {
        updateSong({ songId: song.song_id, data: { is_favorite: !song.is_favorite } })
    }

    return (
        <div className="flex min-h-screen flex-col p-6 pb-24">
            <h1 className="mb-6 text-2xl font-semibold">Your Library</h1>

            {/* Filter bar */}
            <div className="mb-4 flex flex-wrap items-center gap-3">
                <Input
                    placeholder="Search by title..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="max-w-xs"
                />
                <select
                    value={statusFilter}
                    onChange={(e) =>
                        setStatusFilter(e.target.value === '' ? '' : Number(e.target.value))
                    }
                    className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring"
                >
                    <option value="">All Status</option>
                    <option value={GenerationStatus.GENERATED}>Generated</option>
                    <option value={GenerationStatus.GENERATING}>Generating</option>
                    <option value={GenerationStatus.ERROR}>Error</option>
                </select>
                <button
                    onClick={() => setFavoritesOnly((v) => !v)}
                    className={[
                        'h-8 rounded-lg border px-3 text-sm transition-colors',
                        favoritesOnly
                            ? 'border-amber-400 bg-amber-400/10 text-amber-400'
                            : 'border-input text-muted-foreground hover:text-foreground',
                    ].join(' ')}
                >
                    {favoritesOnly ? '♥ Favorites' : '♡ Favorites'}
                </button>
            </div>

            {/* Song list */}
            {isLoading ? (
                <div className="flex flex-col gap-1">
                    {[0, 1, 2].map((i) => (
                        <Skeleton key={i} className="h-14 w-full rounded-lg" />
                    ))}
                </div>
            ) : (
                <SongList
                    songs={filteredSongs}
                    currentSongId={currentSong?.song_id ?? null}
                    onPlay={setCurrentSong}
                    onFavorite={handleFavorite}
                />
            )}

            <AudioPlayer song={currentSong} onClose={() => setCurrentSong(null)} />
        </div>
    )
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend && pnpm typecheck
```

Expected: no errors.

- [ ] **Step 3: Start dev server and open the library page**

```bash
cd frontend && pnpm dev
```

Open http://localhost:3000/library (requires being logged in via Google auth). Verify:
- Filter bar renders (search input, status dropdown, favorites toggle)
- Loading skeletons show while fetching
- Song rows show with correct columns (play, title+occasion, mood pill, duration, status pill, favorite)
- Rows with `generation_status !== 2` are dimmed and play button disabled
- Clicking ▶ starts playback and shows sticky bottom player
- Scrubber updates as audio plays, click on scrubber seeks
- ✕ closes the player
- ♡ toggles favorite (optimistically updates after refetch)
- Search input filters rows by title
- Status dropdown filters by generation status
- Favorites toggle shows only favorited songs

- [ ] **Step 4: Commit**

```bash
git add frontend/app/library/page.tsx
git commit -m "feat: add library page with song list, filters, and audio player"
```
