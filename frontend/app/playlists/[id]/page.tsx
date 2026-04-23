"use client"

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { DropdownMenu } from 'radix-ui'
import {
    usePlaylist,
    useUpdatePlaylist,
    useDeletePlaylist,
    useRemoveSongFromPlaylist,
} from '@/services/playlist.service'
import { Skeleton } from '@/components/ui/skeleton'
import AudioPlayer from '@/components/AudioPlayer'
import { SongResponse, GenerationStatus } from '@/services/song.service'
import { downloadAudio } from '@/lib/download'

const MOOD_LABEL: Record<number, string> = {
    1: 'Happy', 2: 'Sad', 3: 'Upbeat', 4: 'Romantic', 5: 'Chill', 6: 'Epic',
}

function formatDuration(seconds: number): string {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${String(s).padStart(2, '0')}`
}

export default function PlaylistDetailPage() {
    const { id } = useParams<{ id: string }>()
    const router = useRouter()
    const { data: playlist, isLoading } = usePlaylist(id)
    const { mutate: updatePlaylist, isPending: isUpdating } = useUpdatePlaylist()
    const { mutate: deletePlaylist, isPending: isDeleting } = useDeletePlaylist()
    const { mutate: removeSong } = useRemoveSongFromPlaylist()

    const [editingName, setEditingName] = useState(false)
    const [nameInput, setNameInput] = useState('')
    const [currentSong, setCurrentSong] = useState<SongResponse | null>(null)

    if (isLoading) {
        return (
            <div className="flex flex-col gap-2 p-6">
                <Skeleton className="mb-4 h-8 w-48" />
                {[0, 1, 2].map((i) => <Skeleton key={i} className="h-14 w-full rounded-lg" />)}
            </div>
        )
    }

    if (!playlist) {
        return <div className="p-6 text-sm text-muted-foreground">Playlist not found.</div>
    }

    function startEdit() {
        setNameInput(playlist!.name)
        setEditingName(true)
    }

    function handleRename(e: React.FormEvent) {
        e.preventDefault()
        if (!nameInput.trim()) return
        updatePlaylist(
            { playlistId: playlist!.playlist_id, name: nameInput.trim() },
            { onSuccess: () => setEditingName(false) }
        )
    }

    function handleDelete() {
        deletePlaylist(playlist!.playlist_id, {
            onSuccess: () => router.push('/playlists'),
        })
    }

    return (
        <div className="flex min-h-screen flex-col p-6 pb-24">
            {/* Header */}
            <div className="mb-6 flex items-center gap-3">
                <button
                    type="button"
                    onClick={() => router.push('/playlists')}
                    className="text-sm text-muted-foreground hover:text-foreground"
                >
                    ← Playlists
                </button>
                {editingName ? (
                    <form onSubmit={handleRename} className="flex gap-2">
                        <input
                            className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-lg font-semibold outline-none focus-visible:border-ring"
                            value={nameInput}
                            onChange={(e) => setNameInput(e.target.value)}
                            autoFocus
                        />
                        <button
                            type="submit"
                            disabled={isUpdating}
                            className="h-8 rounded-lg bg-primary px-3 text-sm font-medium text-primary-foreground disabled:opacity-50"
                        >
                            Save
                        </button>
                        <button
                            type="button"
                            onClick={() => setEditingName(false)}
                            className="h-8 rounded-lg border border-input px-3 text-sm text-muted-foreground"
                        >
                            Cancel
                        </button>
                    </form>
                ) : (
                    <div className="flex flex-1 items-center gap-2">
                        <h1 className="text-2xl font-semibold">{playlist.name}</h1>
                        <button
                            type="button"
                            onClick={startEdit}
                            className="text-xs text-muted-foreground hover:text-foreground"
                        >
                            ✎
                        </button>
                        <span className="ml-2 text-sm text-muted-foreground">{playlist.song_count} songs</span>
                    </div>
                )}
                <button
                    type="button"
                    onClick={handleDelete}
                    disabled={isDeleting}
                    className="ml-auto rounded-md px-3 py-1.5 text-sm text-muted-foreground hover:bg-destructive/10 hover:text-destructive disabled:opacity-50"
                >
                    Delete playlist
                </button>
            </div>

            {/* Songs */}
            {playlist.songs.length === 0 ? (
                <div className="flex min-h-40 items-center justify-center text-sm text-muted-foreground">
                    No songs in this playlist
                </div>
            ) : (
                <div className="flex flex-col gap-1">
                    {playlist.songs.map((song) => {
                        const isPlayable = song.generation_status === GenerationStatus.GENERATED
                        const isPlaying = currentSong?.song_id === song.song_id
                        return (
                            <div
                                key={song.song_id}
                                className={[
                                    'grid grid-cols-[32px_1fr_100px_60px_32px] gap-3 items-center rounded-lg border px-3 py-2',
                                    isPlaying ? 'border-primary bg-primary/10' : 'border-border bg-card',
                                    !isPlayable && 'opacity-50',
                                ].filter(Boolean).join(' ')}
                            >
                                <button
                                    type="button"
                                    onClick={() => setCurrentSong(song)}
                                    disabled={!isPlayable}
                                    className="flex items-center justify-center text-primary disabled:cursor-not-allowed disabled:text-muted-foreground"
                                >
                                    {isPlaying ? '⏸' : '▶'}
                                </button>
                                <div className="min-w-0">
                                    <div className="truncate text-sm font-semibold">{song.title}</div>
                                    <div className="truncate text-xs text-muted-foreground">{song.occasion}</div>
                                </div>
                                <span className="text-xs text-muted-foreground">
                                    {MOOD_LABEL[song.mood_tone] ?? '—'}
                                </span>
                                <span className="text-xs text-muted-foreground">
                                    {isPlayable ? formatDuration(song.duration) : '—'}
                                </span>

                                <DropdownMenu.Root>
                                    <DropdownMenu.Trigger asChild>
                                        <button
                                            type="button"
                                            className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"
                                            aria-label="Song actions"
                                        >
                                            •••
                                        </button>
                                    </DropdownMenu.Trigger>
                                    <DropdownMenu.Portal>
                                        <DropdownMenu.Content
                                            className="z-50 min-w-44 overflow-hidden rounded-lg border border-border bg-popover text-popover-foreground shadow-md"
                                            align="end"
                                            sideOffset={4}
                                        >
                                            <DropdownMenu.Group className="p-1">
                                                <DropdownMenu.Item
                                                    className="flex w-full cursor-pointer items-center gap-2 rounded-md px-2.5 py-1.5 text-sm outline-none select-none data-highlighted:bg-accent data-highlighted:text-accent-foreground"
                                                    disabled={!isPlayable}
                                                    onSelect={() => downloadAudio(song.audio_file_url, song.title)}
                                                >
                                                    <span>↓</span>
                                                    Download
                                                </DropdownMenu.Item>
                                            </DropdownMenu.Group>
                                            <DropdownMenu.Separator className="my-1 h-px bg-border" />
                                            <DropdownMenu.Group className="p-1">
                                                <DropdownMenu.Item
                                                    className="flex w-full cursor-pointer items-center gap-2 rounded-md px-2.5 py-1.5 text-sm text-destructive outline-none select-none data-highlighted:bg-destructive/10"
                                                    onSelect={() => removeSong({ playlistId: playlist.playlist_id, songId: song.song_id })}
                                                >
                                                    <span>✕</span>
                                                    Remove from playlist
                                                </DropdownMenu.Item>
                                            </DropdownMenu.Group>
                                        </DropdownMenu.Content>
                                    </DropdownMenu.Portal>
                                </DropdownMenu.Root>
                            </div>
                        )
                    })}
                </div>
            )}

            <AudioPlayer song={currentSong} onClose={() => setCurrentSong(null)} />
        </div>
    )
}
