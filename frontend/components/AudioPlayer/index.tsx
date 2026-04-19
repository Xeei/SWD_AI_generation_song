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
                onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
                onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onEnded={() => setIsPlaying(false)}
            />

            {/* Song info */}
            <div className="w-32 shrink-0">
                <div className="truncate text-sm font-semibold">{song.title}</div>
                <div className="truncate text-xs text-muted-foreground">{song.occasion}</div>
            </div>

            {/* Play/pause */}
            <button
                type="button"
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
                type="button"
                onClick={onClose}
                className="shrink-0 text-muted-foreground hover:text-foreground"
                aria-label="Close player"
            >
                ✕
            </button>
        </div>
    )
}
