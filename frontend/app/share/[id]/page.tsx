"use client"

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useSongById, GenerationStatus } from '@/services/song.service'
import { Skeleton } from '@/components/ui/skeleton'
import { Disc } from 'lucide-react'
import { downloadAudio } from '@/lib/download'

const MOOD_LABEL: Record<number, string> = {
    1: 'Happy', 2: 'Sad', 3: 'Upbeat', 4: 'Romantic', 5: 'Chill', 6: 'Epic',
}

const MOOD_CLASS: Record<number, string> = {
    1: 'bg-yellow-500/20 text-yellow-300',
    2: 'bg-blue-500/20 text-blue-300',
    3: 'bg-green-500/20 text-green-300',
    4: 'bg-pink-500/20 text-pink-300',
    5: 'bg-cyan-500/20 text-cyan-300',
    6: 'bg-orange-500/20 text-orange-300',
}

const VOICE_LABEL: Record<number, string> = {
    1: 'Male', 2: 'Female',
}

function formatDuration(seconds: number): string {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${String(s).padStart(2, '0')}`
}

export default function SharePage() {
    useSession({ required: true })

    const { id } = useParams<{ id: string }>()
    const [downloading, setDownloading] = useState(false)
    const { data: song, isLoading } = useSongById(id)

    async function handleDownload() {
        if (!song?.audio_file_url) return
        setDownloading(true)
        try {
            await downloadAudio(song.audio_file_url, song.title)
        } finally {
            setDownloading(false)
        }
    }

    if (isLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center p-6">
                <div className="flex w-full max-w-sm flex-col gap-4">
                    <Skeleton className="h-8 w-48" />
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-12 w-full rounded-lg" />
                </div>
            </div>
        )
    }

    if (!song) {
        return (
            <div className="flex min-h-screen items-center justify-center p-6">
                <p className="text-sm text-muted-foreground">Song not found.</p>
            </div>
        )
    }

    const isPlayable = song.generation_status === GenerationStatus.GENERATED

    return (
        <div className="flex min-h-screen items-center justify-center p-6">
            <div className="flex w-full max-w-md flex-col gap-6">
                {/* Header */}
                <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10">
                        <Disc size={24} className="text-primary" />
                    </div>
                    <div className="min-w-0">
                        <h1 className="truncate text-xl font-semibold">{song.title}</h1>
                        <p className="truncate text-sm text-muted-foreground">{song.occasion}</p>
                    </div>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-2">
                    <span className={`rounded-full px-3 py-1 text-xs font-medium ${MOOD_CLASS[song.mood_tone] ?? 'bg-muted text-muted-foreground'}`}>
                        {MOOD_LABEL[song.mood_tone] ?? '—'}
                    </span>
                    <span className="rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
                        {VOICE_LABEL[song.voice_type] ?? '—'}
                    </span>
                    {isPlayable && (
                        <span className="rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
                            {formatDuration(song.duration)}
                        </span>
                    )}
                </div>

                {/* Player */}
                {isPlayable && song.audio_file_url ? (
                    <div className="flex flex-col gap-3 rounded-xl border border-border bg-card p-4">
                        <audio controls src={song.audio_file_url} className="w-full" />
                        <button
                            type="button"
                            onClick={handleDownload}
                            disabled={downloading}
                            className="inline-flex items-center justify-center gap-2 rounded-lg border border-input px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground disabled:opacity-50"
                        >
                            {downloading ? '⏳ Downloading…' : '↓ Download'}
                        </button>
                    </div>
                ) : (
                    <div className="rounded-xl border border-border bg-card p-4 text-sm text-muted-foreground">
                        {song.generation_status === GenerationStatus.GENERATING
                            ? 'Song is still generating…'
                            : 'Song is unavailable.'}
                    </div>
                )}
            </div>
        </div>
    )
}
