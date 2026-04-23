"use client"

import { useState } from 'react'
import { SongResponse } from '@/services/song.service'
import {
    usePlaylists,
    useCreatePlaylist,
    useAddSongToPlaylist,
} from '@/services/playlist.service'
import { useCreatorId } from '@/services/creator.service'

interface Props {
    song: SongResponse | null
    onClose: () => void
}

export default function AddToPlaylistModal({ song, onClose }: Props) {
    const creatorId = useCreatorId()
    const { data: playlists = [] } = usePlaylists(creatorId)
    const { mutate: createPlaylist, isPending: isCreating } = useCreatePlaylist()
    const { mutate: addSong, isPending: isAdding } = useAddSongToPlaylist()

    const [newName, setNewName] = useState('')
    const [addedIds, setAddedIds] = useState<Set<string>>(new Set())

    if (!song) return null

    function handleAdd(playlistId: string) {
        addSong(
            { playlistId, songId: song!.song_id },
            { onSuccess: () => setAddedIds((s) => new Set(s).add(playlistId)) }
        )
    }

    function handleCreate(e: React.FormEvent) {
        e.preventDefault()
        if (!newName.trim() || !creatorId) return
        createPlaylist(
            { name: newName.trim(), creatorId },
            {
                onSuccess: (playlist) => {
                    setNewName('')
                    handleAdd(playlist.playlist_id)
                },
            }
        )
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
            <div className="w-full max-w-sm rounded-xl border border-border bg-card p-6 shadow-xl">
                <h2 className="mb-1 text-base font-semibold">Add to Playlist</h2>
                <p className="mb-4 truncate text-sm text-muted-foreground">{song.title}</p>

                {/* Create new playlist */}
                <form onSubmit={handleCreate} className="mb-4 flex gap-2">
                    <input
                        className="h-8 flex-1 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring"
                        placeholder="New playlist name…"
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                    />
                    <button
                        type="submit"
                        disabled={!newName.trim() || isCreating}
                        className="h-8 rounded-lg bg-primary px-3 text-sm font-medium text-primary-foreground disabled:opacity-50"
                    >
                        Create
                    </button>
                </form>

                {/* Existing playlists */}
                <div className="flex max-h-60 flex-col gap-1 overflow-y-auto">
                    {playlists.length === 0 && (
                        <p className="py-4 text-center text-sm text-muted-foreground">No playlists yet</p>
                    )}
                    {playlists.map((pl) => {
                        const added = addedIds.has(pl.playlist_id)
                        const alreadyIn = pl.songs.some((s) => s.song_id === song.song_id)
                        return (
                            <div
                                key={pl.playlist_id}
                                className="flex items-center justify-between rounded-lg border border-border px-3 py-2"
                            >
                                <div>
                                    <p className="text-sm font-medium">{pl.name}</p>
                                    <p className="text-xs text-muted-foreground">{pl.song_count} songs</p>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => handleAdd(pl.playlist_id)}
                                    disabled={alreadyIn || added || isAdding}
                                    className="h-7 rounded-md border border-input px-2.5 text-xs hover:bg-accent disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {alreadyIn || added ? 'Added' : 'Add'}
                                </button>
                            </div>
                        )
                    })}
                </div>

                <div className="mt-4 flex justify-end">
                    <button
                        type="button"
                        onClick={onClose}
                        className="h-8 rounded-lg border border-input px-4 text-sm text-muted-foreground hover:text-foreground"
                    >
                        Done
                    </button>
                </div>
            </div>
        </div>
    )
}
