"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useCreatorId } from '@/services/creator.service'
import {
    usePlaylists,
    useCreatePlaylist,
    useDeletePlaylist,
} from '@/services/playlist.service'
import { Skeleton } from '@/components/ui/skeleton'

export default function PlaylistsPage() {
    const router = useRouter()
    const creatorId = useCreatorId()
    const { data: playlists = [], isLoading } = usePlaylists(creatorId)
    const { mutate: createPlaylist, isPending: isCreating } = useCreatePlaylist()
    const { mutate: deletePlaylist } = useDeletePlaylist()

    const [newName, setNewName] = useState('')

    function handleCreate(e: React.FormEvent) {
        e.preventDefault()
        if (!newName.trim() || !creatorId) return
        createPlaylist(
            { name: newName.trim(), creatorId },
            { onSuccess: () => setNewName('') }
        )
    }

    return (
        <div className="flex min-h-screen flex-col p-6">
            <h1 className="mb-6 text-2xl font-semibold">Playlists</h1>

            {/* Create */}
            <form onSubmit={handleCreate} className="mb-6 flex gap-2">
                <input
                    className="h-9 flex-1 max-w-xs rounded-lg border border-input bg-transparent px-3 text-sm outline-none focus-visible:border-ring"
                    placeholder="New playlist name…"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                />
                <button
                    type="submit"
                    disabled={!newName.trim() || isCreating || !creatorId}
                    className="h-9 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground disabled:opacity-50"
                >
                    {isCreating ? 'Creating…' : 'Create'}
                </button>
            </form>

            {isLoading ? (
                <div className="flex flex-col gap-2">
                    {[0, 1, 2].map((i) => <Skeleton key={i} className="h-16 w-full rounded-lg" />)}
                </div>
            ) : playlists.length === 0 ? (
                <div className="flex min-h-40 items-center justify-center text-sm text-muted-foreground">
                    No playlists yet
                </div>
            ) : (
                <div className="flex flex-col gap-2">
                    {playlists.map((pl) => (
                        <div
                            key={pl.playlist_id}
                            className="flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3 hover:bg-accent/50 cursor-pointer"
                            onClick={() => router.push(`/playlists/${pl.playlist_id}`)}
                        >
                            <div>
                                <p className="font-medium">{pl.name}</p>
                                <p className="text-xs text-muted-foreground">{pl.song_count} songs</p>
                            </div>
                            <button
                                type="button"
                                onClick={(e) => {
                                    e.stopPropagation()
                                    deletePlaylist(pl.playlist_id)
                                }}
                                className="rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                            >
                                Delete
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
