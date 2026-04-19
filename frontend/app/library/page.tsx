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
        updateSong(
            { songId: song.song_id, data: { is_favorite: !song.is_favorite } },
            {
                onSuccess: (updated) => {
                    if (currentSong?.song_id === updated.song_id) setCurrentSong(updated)
                },
            }
        )
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
                    type="button"
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
